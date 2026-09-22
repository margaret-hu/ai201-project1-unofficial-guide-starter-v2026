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
<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

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
