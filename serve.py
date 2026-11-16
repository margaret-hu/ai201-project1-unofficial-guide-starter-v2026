#!/usr/bin/env python3
"""
The Unofficial Guide — the same pipeline, over HTTP.

    python serve.py                          run it locally on port 5000
    gunicorn serve:app                       run it the way a host runs it

Nothing new happens in this file. It is a wrapper: a request comes in, it
hands the question to `app.py::ask_pipeline` — the exact function the command
line uses — and hands the answer back as JSON. Retrieval, the relevance gate
and the grounded prompt all still live where they lived. If you change how
your system answers, you change it in those files and this one follows.

Two routes:

    POST /ask       {"question": "..."} in, the answer and its sources out
    GET  /health    is the service up, and is there an index to search

Why this exists: `app.py` runs once and exits, which is fine on your laptop
and impossible to deploy. A hosted service has to stay up and wait for
requests. This is the smallest thing that does that.

Capstone: every POST /ask writes exactly one JSONL record to the request log
(default logs/requests.jsonl, override with AI201_LOG) — answered, refused,
400 and 500 alike. Fields: timestamp, question, answer, error, refused,
sources, latency_ms, status, cache_hit, prompt_tokens, output_tokens,
thinking_tokens, best_distance, model_call_ms, attempts, generate_ms. Keys are always present; a field that doesn't apply is null.
"""

import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request

import config

app = Flask(__name__)

LOG_PATH = Path(os.getenv("AI201_LOG", "logs/requests.jsonl"))
_log_lock = threading.Lock()


def write_log(record: dict) -> None:
    """Append one JSON line. Never raises: logging must not break a request."""
    try:
        with _log_lock:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:  # noqa: BLE001
        print(f"[log] could not write request log: {exc}", file=sys.stderr)


@app.get("/health")
def health():
    """Is the service up, and is there an index to search?

    Two different questions, and the second one is the one that bites. A
    freshly deployed service answers this route happily while every /ask
    returns "no index" — hosts give you no disk that survives a restart, so
    the index has to be built as part of getting the service up. Checking
    here means you find that out in one request instead of five.
    """
    from store import index_exists

    ready = index_exists(config.CORPUS)
    return jsonify(
        {
            "status": "ok",
            "corpus": config.CORPUS,
            "index_ready": ready,
            "detail": (
                "ready"
                if ready
                else "no index for this corpus — run `python app.py index`"
            ),
        }
    )


@app.post("/ask")
def ask():
    """One question in, one grounded answer out.

    A refused question is a 200, not an error. The gate refusing is your
    system working — it is an answer, and the JSON says so with
    `"refused": true` so whatever calls this can tell the two apart.

    Exactly one log record is written per call, in `finally`, so no path
    (400, 500, refusal, success) can skip it.
    """
    from app import ask_pipeline

    started = time.perf_counter()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": None,
        "answer": None,
        "error": None,
        "refused": None,
        "sources": None,
        "latency_ms": None,
        "status": 500,  # overwritten on every path that returns normally
        "cache_hit": None,
        "prompt_tokens": None,
        "output_tokens": None,
        "thinking_tokens": None,
        "best_distance": None,
        "model_call_ms": None,  # the successful generate_content call alone; null if no model call
        "attempts": None,       # model attempts for this request (1 = no retry)
        "generate_ms": None,    # all of generate.py: limiter sleep + retries + backoff + the call
    }
    try:
        payload = request.get_json(silent=True) or {}
        question = (payload.get("question") or "").strip()
        record["question"] = question

        if not question:
            record["status"] = 400
            record["error"] = "empty question"
            return (
                jsonify(
                    {
                        "error": "Send JSON with a question in it, like "
                        '{"question": "is the housing lottery random?"}'
                    }
                ),
                400,
            )

        try:
            # Test hook for criterion C1: only honoured when explicitly enabled.
            if (
                os.getenv("AI201_ALLOW_FORCE_FAIL") == "1"
                and request.headers.get("X-Force-Failure") == "1"
            ):
                raise RuntimeError("forced failure (X-Force-Failure)")
            outcome = ask_pipeline(question, corpus=config.CORPUS)
        except Exception as exc:  # noqa: BLE001 — a reader gets this, not a traceback
            message = f"{type(exc).__name__}: {exc}"
            record["status"] = 500
            record["error"] = message
            return jsonify({"error": message}), 500

        usage = outcome.get("usage") or {}
        record.update(
            status=200,
            answer=outcome["answer"],
            refused=outcome["refused"],
            sources=outcome["sources"],
            best_distance=round(outcome["best_distance"], 4),
            cache_hit=usage.get("cache_hit"),
            prompt_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("output_tokens"),
            thinking_tokens=usage.get("thinking_tokens"),
            model_call_ms=usage.get("model_call_ms"),
            attempts=usage.get("attempts"),
            generate_ms=usage.get("generate_ms"),
        )
        return jsonify(
            {
                "question": question,
                "answer": outcome["answer"],
                "refused": outcome["refused"],
                "sources": outcome["sources"],
                "best_distance": round(outcome["best_distance"], 4),
                "threshold": outcome["threshold"],
                "corpus": config.CORPUS,
            }
        )
    except Exception as exc:  # noqa: BLE001 — anything unexpected is still a 500
        message = f"{type(exc).__name__}: {exc}"
        record["status"] = 500
        record["error"] = message
        return jsonify({"error": message}), 500
    finally:
        record["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
        write_log(record)


def main():
    # Hosts tell you which port to listen on through PORT, and they expect you
    # on 0.0.0.0. Binding 127.0.0.1 instead works perfectly on your laptop and
    # then answers nothing at all once deployed, because the host's router
    # can't reach a socket that only accepts connections from inside the
    # container. It is the single most common way a first deploy "succeeds"
    # and is unreachable.
    port = int(os.getenv("PORT", "5000"))

    # Debug mode reloads on save, which is handy, and prints a console that
    # runs arbitrary code, which is not something to leave switched on where
    # strangers can reach it. Off unless you ask for it.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"Serving The Unofficial Guide on http://localhost:{port}")
    print(f"Corpus: {config.CORPUS}    (Ctrl-C to stop)\n")
    print("Try it from another terminal:\n")
    print(f"  curl http://localhost:{port}/health")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"question\": \"is the housing lottery random?\"}}'\n"
    )

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
