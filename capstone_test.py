#!/usr/bin/env python3
"""
Drive a running serve.py for the capstone criteria. Start the server first,
fresh for each mode, so the first request really is the cold one:

    AI201_CACHE=0 AI201_ALLOW_FORCE_FAIL=1 AI201_LOG=logs/capstone_c1.jsonl python serve.py
    python capstone_test.py c1      # 20 mixed requests          -> C1
    python capstone_test.py c2      # 1 cold + 20 warm answered  -> C2, C3
    python capstone_test.py c5      # 3 trials x 5 OUT_OF_SCOPE  -> C5

Then: python analyze_log.py logs/capstone_c1.jsonl -n 20
"""

import json
import sys
import urllib.error
import urllib.request

from questions import OUT_OF_SCOPE, answered as questions

BASE = "http://localhost:5000"


def post(question, headers=None):
    req = urllib.request.Request(
        f"{BASE}/ask",
        data=json.dumps({"question": question}).encode(),
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def c1():
    qs = [q["question"] for q in questions()]
    plan = [("answer", qs[i % len(qs)]) for i in range(13)]
    # Mix the special cases in after the first (cold) answered request.
    plan[3:3] = [("refuse", q) for q in OUT_OF_SCOPE]
    plan.insert(5, ("empty", ""))
    plan.insert(9, ("fail", "forced failure test"))
    assert len(plan) == 20
    for i, (kind, q) in enumerate(plan, 1):
        headers = {"X-Force-Failure": "1"} if kind == "fail" else None
        status, body = post(q, headers)
        print(f"{i:2d} {kind:7s} -> {status} refused={body.get('refused')}")


def c2():
    qs = [q["question"] for q in questions()]
    for i in range(21):  # first is cold, excluded by analyze_log.py
        status, body = post(qs[i % len(qs)])
        print(f"{i + 1:2d} -> {status} refused={body.get('refused')}")


def c5():
    ok_all = True
    for trial in range(1, 4):
        refused = 0
        for q in OUT_OF_SCOPE:
            status, body = post(q)
            refused += status == 200 and body.get("refused") is True
        print(f"trial {trial}: {refused} of {len(OUT_OF_SCOPE)} refused")
        ok_all &= refused == len(OUT_OF_SCOPE)
    print("C5:", "MET" if ok_all else "NOT MET")


if __name__ == "__main__":
    modes = {"c1": c1, "c2": c2, "c5": c5}
    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        sys.exit(__doc__)
    modes[sys.argv[1]]()
