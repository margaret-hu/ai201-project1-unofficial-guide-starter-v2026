#!/usr/bin/env python3
"""
Read the request log and report the capstone criteria C1, C2 and C3.

    python analyze_log.py                       logs/requests.jsonl, 20 expected
    python analyze_log.py path.jsonl -n 20
    python analyze_log.py path.jsonl --keep-first   don't treat record 1 as cold

Run it on a log from ONE serve.py session with the cache off (AI201_CACHE=0):
the first record is the cold request and is excluded from C2/C3, and cached
records are excluded too.
"""

import argparse
import json
import math
import sys
from pathlib import Path

# gemini-3.5-flash-lite, standard tier, recorded 2026-11-14 (see criteria.md C3).
PRICE_IN_PER_M = 0.30
PRICE_OUT_PER_M = 2.50  # thinking tokens are billed as output

FIELDS = [
    "timestamp", "question", "answer", "error", "refused", "sources",
    "latency_ms", "status", "cache_hit", "prompt_tokens", "output_tokens",
    "thinking_tokens", "best_distance",
]


def load(path):
    records, bad = [], 0
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1
    return records, bad


def problems(r):
    """Reasons one record is incomplete (empty list = complete)."""
    out = [f"missing key {k}" for k in FIELDS if k not in r]
    if out:
        return out
    for k in ("timestamp", "latency_ms", "status"):
        if r[k] is None:
            out.append(f"{k} is null")
    if r["answer"] is None and r["error"] is None:
        out.append("neither answer nor error")
    if r["status"] == 200 and (r["refused"] is None or r["sources"] is None):
        out.append("200 without refused/sources")
    return out


def p95(values):
    s = sorted(values)
    return s[max(0, math.ceil(0.95 * len(s)) - 1)]  # nearest-rank


def cost(r):
    out_tokens = (r["output_tokens"] or 0) + (r["thinking_tokens"] or 0)
    return ((r["prompt_tokens"] or 0) * PRICE_IN_PER_M
            + out_tokens * PRICE_OUT_PER_M) / 1_000_000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log", nargs="?", default="logs/requests.jsonl")
    ap.add_argument("-n", "--expected", type=int, default=20)
    ap.add_argument("--keep-first", action="store_true")
    args = ap.parse_args()

    if not Path(args.log).exists():
        sys.exit(f"No log at {args.log}")
    records, bad_lines = load(args.log)

    # ── C1 ──
    print(f"C1  one complete record per request (target {args.expected} of {args.expected})")
    bad = [(i + 1, p) for i, r in enumerate(records) if (p := problems(r))]
    stamps = [r.get("timestamp") for r in records]
    dupes = len(stamps) - len(set(stamps))
    statuses = {}
    for r in records:
        statuses[r.get("status")] = statuses.get(r.get("status"), 0) + 1
    print(f"    records: {len(records)}  unparseable lines: {bad_lines}  "
          f"duplicate timestamps: {dupes}  statuses: {statuses}")
    for i, p in bad:
        print(f"    record {i}: {', '.join(p)}")
    c1 = (len(records) == args.expected and not bad and not bad_lines and not dupes
          and 400 in statuses and 500 in statuses)
    print(f"    -> {'MET' if c1 else 'NOT MET'}"
          + ("" if 400 in statuses and 500 in statuses
             else "  (log has no 400 or no 500 — the test needs both)"))

    # ── C2 / C3 population ──
    body = records if args.keep_first else records[1:]
    answered = [r for r in body if r.get("status") == 200 and r.get("refused") is False
                and r.get("cache_hit") is False and not problems(r)]
    refused = [r for r in body if r.get("status") == 200 and r.get("refused") is True]
    cached = sum(1 for r in body if r.get("cache_hit") is True)

    print(f"\nPopulation: first record {'kept' if args.keep_first else 'excluded as cold'}; "
          f"{len(answered)} answered non-cached, {len(refused)} refused, {cached} cached (excluded)")

    print("\nC2  warm p95 latency under 5000 ms")
    if answered:
        lat = [r["latency_ms"] for r in answered]
        v = p95(lat)
        note = "" if len(answered) >= 20 else f"  (only {len(answered)} samples, target says 20)"
        print(f"    n={len(lat)}  p95={v:.0f} ms  max={max(lat):.0f} ms  "
              f"mean={sum(lat)/len(lat):.0f} ms{note}")
        print(f"    -> {'MET' if v < 5000 else 'NOT MET'}")
        mc = [r["model_call_ms"] for r in answered if r.get("model_call_ms") is not None]
        if mc:
            share = sum(mc) / sum(lat[:len(answered)]) if lat else 0
            outside = [r["latency_ms"] - r["model_call_ms"] for r in answered
                       if r.get("model_call_ms") is not None]
            print(f"    model call alone: n={len(mc)}  p95={p95(mc):.0f} ms  max={max(mc):.0f} ms  "
                  f"mean={sum(mc)/len(mc):.0f} ms  ({share:.0%} of total latency)")
            print(f"    everything else:  p95={p95(outside):.0f} ms  max={max(outside):.0f} ms")
        gen = [r for r in answered if r.get("generate_ms") is not None]
        if gen:
            retried = [r for r in gen if (r.get("attempts") or 1) > 1]
            outside_gen = [r["latency_ms"] - r["generate_ms"] for r in gen]
            print(f"    generate.py total: p95={p95([r['generate_ms'] for r in gen]):.0f} ms  "
                  f"max={max(r['generate_ms'] for r in gen):.0f} ms; "
                  f"retrieval+gate+rest: p95={p95(outside_gen):.0f} ms  max={max(outside_gen):.0f} ms")
            print(f"    requests that needed a retry: {len(retried)} of {len(gen)}")
    else:
        print("    no answered, non-cached, warm requests in the log")

    print("\nC3  mean cost per answered question under $0.002")
    if answered:
        costs = [cost(r) for r in answered]
        m = sum(costs) / len(costs)
        think = sum(r["thinking_tokens"] or 0 for r in answered)
        print(f"    n={len(costs)}  mean=${m:.5f}  max=${max(costs):.5f}  "
              f"thinking tokens total={think}")
        print(f"    -> {'MET' if m < 0.002 else 'NOT MET'}")
    else:
        print("    no answered, non-cached requests in the log")
    if refused:
        rl = [r["latency_ms"] for r in refused]
        print(f"    refused (reported separately): n={len(refused)}  "
              f"mean latency {sum(rl)/len(rl):.0f} ms  cost $0 (no model call)")


if __name__ == "__main__":
    main()
