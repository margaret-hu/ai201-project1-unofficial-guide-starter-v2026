# The Unofficial Guide

Margaret Hu — campus_life corpus

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

A retrieval-augmented Q&A system over `campus_life`, 88 short student-life posts on dining halls, dorms, courses, and administrative rules like add/drop deadlines and the housing lottery. It embeds and retrieves the closest chunks for a question, then answers from only that material, citing the source. A relevance gate refuses questions the corpus doesn't cover instead of guessing. It answers specific, factual questions ("How late can I declare pass/fail?"), not vague ones ("What are good dining halls?").

## Chunking Strategy

**Chunk size:** 600
**Overlap:** 0

`campus_life` posts are short (178–549 characters, average 317), and none exceed criterion 4's 600-character ceiling — so the goal is one post per chunk, splitting only if a document ever crosses 600.

I first tried overlap=100, but that backfired: two documents (516 and 549 characters) fully fit in the first 600-character window, yet still produced a second, spurious chunk of just their last 16–48 characters — meaningless on their own and under criterion 4's 150-character floor. Since nothing here needs a real multi-chunk split, overlap was only ever causing that bug, so I set it to 0. That closes the bug entirely and restores 88 documents → 88 clean chunks (178–549 chars each).

## Sample Chunks

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::fallback_split`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160.txt#0` — produced by: `chunker.py::fallback_split`

```
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: `chunker.py::fallback_split`

```
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: `chunker.py::fallback_split`

```
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: `chunker.py::fallback_split`

```
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

**Question:** Can I change my meal plan tier after the semester starts?

**Answer:**

```
  (best distance 0.165, cutoff 0.63)

Yes, you can change your meal plan tier once, but only in the first ten days of the semester. After that, it is locked (admin_meal_plan_changes.txt).

Sources retrieved: admin_dining_dollars.txt, admin_meal_plan_changes.txt, dining_north_kitchen_followup.txt, dining_verrill_street_grill.txt, money_jobs.txt
```

**My relevance cutoff:** 0.63

I ran `python app.py retrieve "..."` for my five in-corpus questions and the five `OUT_OF_SCOPE` questions and recorded the best (lowest) distance for each. The in-corpus group topped out at 0.439; the out-of-scope group bottomed out at 0.825 — a wide, clean gap with nothing in between. I set the cutoff at the midpoint, 0.63, so it isn't hugging either edge.

| Question | In corpus? | Best distance |
|---|---|---|
| How late in the semester can I declare a pass/fail course? | yes | 0.204 |
| Does the library stay open later during term or during reading week? | yes | 0.439 |
| Is there a waitlist for parking permits if I miss the sale window? | yes | 0.366 |
| Can I change my meal plan tier after the semester starts? | yes | 0.165 |
| Does taking summer courses for extra credit hours get me a better housing lottery number? | yes | 0.388 |
| What is the capital of Mongolia? | no | 0.825 |
| How do I change the oil in a diesel engine? | no | 0.934 |
| Who won the 1994 World Cup? | no | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.844 |
| How do I write a for loop in Rust? | no | 0.896 |

## How I Used AI

**1.** I asked Claude to self-check my five `criteria.md` targets for being numeric, corpus-grounded, and measurable twice. It found criterion 3's "why" was still an unfilled placeholder, and flagged criteria 1 and 5 as relying on subjective judgment calls worth watching later. I filled in criterion 3's "why" with the actual gap between my in-corpus and out-of-scope distances.

**2.** I asked Claude to run `app.py chunks` and check whether each chunk could answer a question standalone. The 5-chunk sample looked fine, but it dug further and found `CHUNK_OVERLAP=100` was producing 16–48 character orphan fragments from two documents — under my own 150-char floor — because `fallback_split` doesn't stop once a window already covers the whole document. I set `CHUNK_OVERLAP = 0` instead of patching the function.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. No chunk under 150 or over 600 characters | 0 of 88 | 0 of 88 | 0 of 88 | 0 of 88 | MET |
| 5. Every answer supported, nothing unsupported | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |

Produced by `run_eval.py::main` and `run_eval.py::check_out_of_scope`; raw output in `results/run_2026-09-26_2319_before.md`. Retrieval and the gate are deterministic, so criterion 1's sources retrieved and criterion 3's gate outcome don't vary run to run — only the generated wording does. Criterion 4 is likewise deterministic — chunking doesn't change run to run — so the same number repeats across all three columns.

**Criterion 1** — every question's retrieved set includes the file that answers it:

```
### How late in the semester can I declare a pass/fail course? — run 1
Sources retrieved: admin_add_drop_deadline.txt, admin_declaring_a_major.txt, admin_graduation_requirements.txt, admin_pass_fail_option.txt, course_cs_340.txt
```

**Criterion 2** — every answer cites a source, e.g.:

```
You can declare a course pass/fail as late as week eight.

Source: admin_pass_fail_option.txt
```

**Criterion 3** — the gate on `OUT_OF_SCOPE`, one deterministic pass:

```
| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.934 | refused |
| Who won the 1994 World Cup? | 0.886 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.844 | refused |
| How do I write a for loop in Rust? | 0.896 | refused |
```

**Criterion 4** — `chunker.py::describe`, printed by `python app.py index`:

```
chunked  88 chunks, 317 characters on average (shortest 178, longest 549), produced by chunker.py::fallback_split
```

**Criterion 5** — read against the retrieved-chunk text in `results/run_2026-09-26_2319_before.md`; all 15 answers (5 questions × 3 runs) stay within what their cited source says. Example:

```
Yes, you can change your meal plan tier once, but only in the first ten days of the semester. After that, it is locked.

Source: admin_meal_plan_changes.txt
```

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | This one takes a judgment call — I checked whether the retrieved set for each question included a chunk that stated the answer outright. All five did, in all three runs, comfortably past the 4-of-5 target. |
| 2 | Every answer names a source | MET | Attribution is mechanical, not judged — the run log either shows a source or it doesn't. It showed one every time: 5 of 5 across all three runs. |
| 3 | Gate stops out-of-corpus questions | MET | The gate's pass/refuse call is deterministic once the cutoff is set, so I read it straight off the run log: all five out-of-scope questions were refused, clearing the 4-of-5 target. |
| 4 | No chunk under 150 or over 600 characters | MET | Chunk lengths are fixed by the chunker, not by the run, so this is one measurement repeated three times, not three independent checks: 0 of 88 out of band. |
| 5 | Every answer supported, nothing unsupported | MET | This one needed a judgment call — I read all 15 answers (5 questions × 3 runs) against their cited source's text and found nothing that wasn't there. |

## Diagnoses

Nothing missed — all five hit their numbers in all three runs.

Criterion 1 was looser than it looked, though: the housing-lottery question only passed because the generator inferred a negation ("no, ... but juniors/seniors are ordered by credit hours") that `admin_housing_lottery.txt` never states — it attaches "number" only to the random draw for sophomores. Retrieval was fine (same chunk, every run, distance 0.3875); the criterion just couldn't distinguish "states this" from "implies this." Tightened in criteria.md — under that reading, this is the one genuine 4-of-5 case in the set.

## The Improvement

**What I changed:**

Added a rule to `GROUNDING_INSTRUCTION` in `generate.py`: the model must state only conclusions the documents assert directly, and explicitly flag ("The document doesn't say this outright, but...") any place it has to infer or negate something the text doesn't literally say, instead of presenting that inference as fact.

**Why I picked it:**

The Diagnoses section found the housing-lottery answer's flat "No" was the generator inferring a negation that `admin_housing_lottery.txt` never states, while retrieval pulled the same correct chunk every run — so the failure was at generation, not chunking or retrieval, which is what this prompt change targets.

### Run Log — After

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 4 of 5 | 4 of 5 | 4 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. No chunk under 150 or over 600 characters | 0 of 88 | 0 of 88 | 0 of 88 | 0 of 88 | MET |
| 5. Every answer supported, nothing unsupported | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |

Produced by `run_eval.py::main` and `run_eval.py::check_out_of_scope`; raw output in `results/run_2026-09-28_0039_after.md`. The prompt change in `generate.py::GROUNDING_INSTRUCTION` only touches generation, so retrieval and chunking are unchanged from the before log — criteria 1, 3, and 4 repeat their before numbers.

**Criterion 1** — the housing-lottery question is still the one miss: `admin_housing_lottery.txt` says a senior with summer courses "reliably beats" one without, but never attaches "number" to juniors/seniors — so "no, it doesn't get you a better *number*" is still a step the chunk itself doesn't state, in every run, e.g.:

```
The documents state that juniors and seniors are ordered by accumulated credit hours first, meaning a senior who took summer courses reliably beats a senior who didn't. (Source: admin_housing_lottery.txt)
```

**Did it help?**

Partly. The flat, unqualified "No" from the before log is gone — runs now hedge into language the source actually supports, so criterion 5 stayed a clean 5 of 5 with no fabricated details. But it didn't fix criterion 1: the chunk still never states the answer in quotable form, so that question stays a miss in all three after-runs (4 of 5, unchanged), and run 3 still opens with a bare "No." before its caveat, so the rule isn't applied consistently. Both criteria were already MET before the change, so no verdict moved — the improvement shows in the answer text, not the scoreboard.

## The Second Improvement

**What I changed:**

Raised `TOP_K` in `config.py` from 5 to 8 — a Milestone 4 retrieval change this time, not another generation-prompt edit.

**Why I picked it:**

The first improvement only touched generation. `advising_registration.txt` is the only other document mentioning credit-hour staggering, and it wasn't in the top-5 retrieved chunks — widening the window was the untried retrieval-side lever that might surface it.

### Run Log — After (second change)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 4 of 5 | 4 of 5 | 4 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. No chunk under 150 or over 600 characters | 0 of 88 | 0 of 88 | 0 of 88 | 0 of 88 | MET |
| 5. Every answer supported, nothing unsupported | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |

Produced by `run_eval.py::main`; raw output in `results/run_2026-10-03_0026_after2.md`. Only `TOP_K` changed (5 → 8) — everything else, including the generation prompt, is identical to the first improvement.

**Criterion 1** — the wider window did pull `advising_registration.txt` into the retrieved set, but it only corroborates the credit-hour ordering, it doesn't attach "number" to juniors/seniors any more directly than `admin_housing_lottery.txt` already does. The miss is unchanged, in every run:

```
No, taking summer courses does not get you a better lottery *number*; rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours with random tie-breaks, meaning a senior with more credit hours from summer courses reliably beats one who didn't.

Source: admin_housing_lottery.txt
```

**Did it help?**

No. Every criterion matches the first improvement's after-log exactly — a wider top-k can't move criterion 3's best distance (the nearest chunk is already inside any k ≥ 1), and criterion 1 stays at 4 of 5 since the fact simply isn't written down anywhere in the corpus. The only visible change is cosmetic: answers now cite a couple more of the eight retrieved sources, with no new fabrication. The housing-lottery gap is a corpus/chunking problem — not generation, and now, not retrieval coverage either.

## What's Still Broken

Every criterion is MET, but criterion 1's 4-of-5 still hides a real gap: `admin_housing_lottery.txt` never states the housing-lottery negation in quotable form, so it's a corpus/chunking problem, not a generation one — no prompt tweak fixes a fact that isn't in the text. The prompt fix isn't even fully consistent either; run 3 in the after log still opens with a bare "No." before hedging.

I stopped rather than edit the source document, since rewriting the corpus to make my own system pass feels like curating the test, not fixing the pipeline.

## What I'd Do Differently

**Criterion 1** — I'd set "directly quotable, not inferred" as the original target instead of a unit-2 revision. My own unit-1 "why" already flagged the housing-lottery question as the risky one; I had enough to predict this before running anything.

**Criterion 3** — 4 of 5 was too loose. The in-corpus/out-of-scope distance gap is 0.386 wide, and the gate hit 5 of 5 every run in both logs. 5 of 5 would've been the honest bar.

**Criterion 5** — I'd define "supported" up front as "near-verbatim in a retrieved chunk, else flagged as inference" — the same distinction I only reached after diagnosing the housing-lottery gap.
