# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that contains the answer.

**Why this target:**
My question about whether summer courses improve your housing lottery number touches a topic only two documents mention (`admin_housing_lottery.txt` and `advising_registration.txt`), so I expect that one to be harder to retrieve correctly than the other four.

> **Revised in unit 2:** For at least 4 of 5 questions, the retrieved chunks
> include one that states the answer directly — quotable as-is, not
> inferred by combining or negating facts.
>
> **Why revised:** Four questions have a chunk that states the answer
> outright. The fifth (housing lottery) doesn't: `admin_housing_lottery.txt`
> never says "no" and never attaches "number" to juniors/seniors, only to
> the random draw for sophomores — my system's negation is the generator's
> inference, not a sentence in the chunk. "Contains the answer" couldn't
> tell those two cases apart, so I made it mean directly quotable.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
Attribution is deterministic, not fuzzy retrieval — the pipeline either points to the right file or it doesn't. A miss would mean a bug in the attachment logic, not a content-matching shortfall, so I expect this to hold every time.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate stops it and the system returns "I don't have enough information about that" — in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
In-corpus questions topped out at a 0.439 best distance and out-of-scope questions bottomed out at 0.825 — a wide, clean gap — so I set the cutoff at the midpoint, 0.63. With that much margin on both sides, I expect the gate to hold on 4 of 5.

---

## 4. Something about your chunks

No chunk, across all chunks in my corpus, is under 150 or over 600 characters.

**Why this target:**
My chunks average 317 characters, ranging from 178 to 549. A 150–600 band leaves headroom on both ends to catch a chunking bug — a stray fragment or two merged sections — without flagging normal length variation.

---

## 5. Your choice

Every answer the system produces must be supported by the retrieved chunks and must not include unsupported information.

**Why this target:**
A fabricated detail is worse than an admitted miss, since it looks just as authoritative as a correct answer — that's why this criterion gets zero slack instead of the 4-of-5 I gave the others.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone — shape A (deploy and instrument), Path B (local with logs)

Written before any capstone results exist. Criteria C1-C4 are about the new
operational layer; C5 checks that the layer didn't break the system underneath.

"Warm" means a request made after at least one earlier request has already
been answered by the same running `serve.py` process; the first request after
start is cold and is reported separately, not counted toward any target.
Cached model responses (`.cache/`) are excluded from C2 and C3: the cache is
disabled or each record carries a `cache_hit` field, so a hit never makes
latency or cost look better than a real call.

## C1. Every request leaves a complete log record

Across 20 requests sent to `POST /ask` — including refused questions, an empty
question (400), and one forced pipeline failure (500) — every request writes
exactly one JSONL record containing: timestamp, question, answer (or error),
refused, sources, and latency in milliseconds. Target: 20 of 20, no missing
fields, no missing records, no duplicates.

**Why this target:**
Zero slack makes the test straightforward: all 20 requests must produce exactly
one record, including the 400 and forced 500 paths. A missing error-path record
removes the evidence needed to diagnose failures later; duplicates make the
request count and latency data unreliable.

## C2. Warm latency: p95 under 5 seconds

p95 end-to-end latency (the logged latency field) over 20 warm, non-cached
answered requests is under 5 seconds.

**Why this target:**
A warm request is one local retrieval over 88 chunks plus a single call to the
hosted model, so the model call is the only external hop and should take a few
seconds at most. 5 s leaves room for network variability but would still catch
a real slow path; a looser ceiling would pass even when something is badly
wrong. p95 rather than the mean because a few very slow requests are hidden by
otherwise fast ones.

## C3. Cost per answered question: under $0.002

Mean cost per answered (non-refused, non-cached) question, computed from the
token counts the Gemini response reports and the selected model's published
per-token price, is under $0.002. Refused questions are reported separately so
they don't distort it.

**Why this target:**
Each prompt carries 8 retrieved chunks of about 317 characters, roughly 1,000
input tokens, plus a short answer of about 100 output tokens. Even at a
pessimistic price that comes to well under a quarter of a cent, so $0.002
leaves headroom for longer answers while still catching a prompt that has
grown. Computed from reported usage, not estimated.

## C4. A clean checkout runs from RUNNING.md alone

On a fresh `git clone` into an empty directory, following only the Capstone
section of RUNNING.md, I reach a successful `POST /ask` (HTTP 200, non-empty
answer) with no step I had to remember from outside the document. Target:
succeeds on the first attempt, tried once from a clean directory.

**Why this target:**
Success on the first attempt checks that RUNNING.md is a complete, reproducible
procedure, not just a description of the code. In particular it should cover
prerequisites, credentials, index building, and any model download needed
before serving.

## C5. The gate still holds through the HTTP path

Sent through `POST /ask`, the 5 `OUT_OF_SCOPE` questions are all refused
(`"refused": true`), in each of 3 trials. Target: 5 of 5, every trial.

**Why this target:**
The 5-of-5 target in every trial checks that adding the HTTP and logging layers
hasn't changed refusal behavior. A miss would indicate a regression in the gate
or its integration, rather than acceptable variation in logging.
