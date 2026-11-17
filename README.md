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

---

# Capstone

## What This Extends

This extends the Unofficial Guide RAG system I built in units 1 and 2 (the
`campus_life` corpus: chunking, Chroma retrieval, the 0.63 relevance gate and the
grounded Gemini prompt in `app.py::ask_pipeline`). What's new is the layer around
it, all in `serve.py` and `generate.py`: a per-request JSONL log, per-call token
usage from the Gemini response, a switchable forced-failure hook, an analysis
script (`analyze_log.py`), a driver (`capstone_test.py`) and a Capstone section in
`RUNNING.md`. The pipeline's behavior is unchanged.

## The Shape

Shape A (deploy and instrument), Path B (run locally, with logs). I'm adding an
operational layer to `serve.py` and leaving the pipeline underneath untouched:
every `POST /ask` writes exactly one JSONL record (timestamp, question, answer or
error, refused, sources, latency in ms, `cache_hit`, and token counts). `generate.py` will
return per-call token usage so I can compute cost per answered question from what
the Gemini response reports, not an estimate. I'll also add a way to force a
pipeline failure so the 500 path can be tested, and write a Capstone section in
RUNNING.md that gets a clean clone to a successful `POST /ask`. The acceptance
criteria for all of this (C1-C5) are in `criteria.md`, written before any results.

Size check: about 85 minutes of building (logging 25, token usage and cost 10,
failure switch 5, `analyze_log.py` 15, Capstone section 20), touching four files
with no new dependencies. If I'm running over, the first thing I cut is the cost
computation: I'd log raw token counts only and compute cost later in
`analyze_log.py`.

## Out of Scope

- **No real deployment.** Path B means the service runs on my machine; I'm not
  setting up a host, a domain, or a persistent disk for the index.
- **No changes to retrieval, chunking, the gate, or the prompt.** C5 exists to
  prove the HTTP and logging layers didn't change refusal behavior, so the
  pipeline stays as it is. The housing-lottery gap from unit 2 stays a known gap.
- **No dashboard, metrics server, or log aggregation.** The log is a JSONL file I
  read with a short script. No new interface either.

## Running It

Path B: it runs locally on my machine with `python serve.py` (port 5000), writing
`logs/requests.jsonl`. It is not deployed. The full clone-to-first-answer
procedure is the **Capstone** section of `RUNNING.md`, and the settings used for
the test runs (`AI201_CACHE=0`, `AI201_ALLOW_FORCE_FAIL=1`, `AI201_LOG`) are in the
table at the end of that section. The test driver is `capstone_test.py` (modes
`c1`, `c2`, `c5`) and the log reader is `analyze_log.py`.

## Instrumentation

Every `POST /ask` appends one JSON line to `logs/requests.jsonl`, written in a
`finally` block so the 400 and 500 paths can't skip it. The twelve records below
come from one session (`logs/capstone_c1.jsonl`, 20 requests): seven answered
questions, three refusals, one rejected empty question (400), and one forced
pipeline failure (500). Only the `answer` field is shortened (to 110 characters
with `…`); every other field is as logged.

```jsonl
{"timestamp": "2026-11-15T07:15:09.145587+00:00", "question": "How late in the semester can I declare a pass/fail course?", "answer": "You can declare a course pass/fail as late as week eight, after you have seen your midterm. (Source: admin_pas…", "error": null, "refused": false, "sources": ["admin_add_drop_deadline.txt", "admin_declaring_a_major.txt", "admin_grade_appeals.txt", "admin_graduation_requirements.txt", "admin_pass_fail_option.txt", "course_biol_160.txt", "course_cs_340.txt", "course_stat_150.txt"], "latency_ms": 4334.1, "status": 200, "cache_hit": false, "prompt_tokens": 879, "output_tokens": 34, "thinking_tokens": 0, "best_distance": 0.2039}
{"timestamp": "2026-11-15T07:15:15.556794+00:00", "question": "Does the library stay open later during term or during reading week?", "answer": "The library stays open later during term, closing at 2am compared to 10pm during reading week. \n\nSource: *stud…", "error": null, "refused": false, "sources": ["admin_library_holds.txt", "housing_calder_annexe_noise.txt", "housing_morrow_house_noise.txt", "money_jobs.txt", "money_textbooks.txt", "orientation_what_matters.txt", "study_group_rooms.txt", "study_library_hours.txt"], "latency_ms": 735.7, "status": 200, "cache_hit": false, "prompt_tokens": 847, "output_tokens": 36, "thinking_tokens": 0, "best_distance": 0.4392}
{"timestamp": "2026-11-15T07:15:18.338641+00:00", "question": "Is there a waitlist for parking permits if I miss the sale window?", "answer": "According to `admin_parking_permits.txt`, there is no waitlist for parking permits.", "error": null, "refused": false, "sources": ["admin_parking_permits.txt", "advising_registration.txt", "dining_halden_hall_followup.txt", "dining_kestrel_commons_followup.txt", "dining_north_kitchen_followup.txt", "dining_the_atrium_followup.txt", "dining_verrill_street_grill_followup.txt", "transit_shuttle.txt"], "latency_ms": 696.8, "status": 200, "cache_hit": false, "prompt_tokens": 957, "output_tokens": 21, "thinking_tokens": 0, "best_distance": 0.3657}
{"timestamp": "2026-11-15T07:15:21.104992+00:00", "question": "What is the capital of Mongolia?", "answer": "I don't have enough information about that.", "error": null, "refused": true, "sources": [], "latency_ms": 87.5, "status": 200, "cache_hit": null, "prompt_tokens": null, "output_tokens": null, "thinking_tokens": null, "best_distance": 0.8246}
{"timestamp": "2026-11-15T07:15:23.241429+00:00", "question": "How do I change the oil in a diesel engine?", "answer": "I don't have enough information about that.", "error": null, "refused": true, "sources": [], "latency_ms": 73.6, "status": 200, "cache_hit": null, "prompt_tokens": null, "output_tokens": null, "thinking_tokens": null, "best_distance": 0.934}
{"timestamp": "2026-11-15T07:15:25.377021+00:00", "question": "", "answer": null, "error": "empty question", "refused": null, "sources": null, "latency_ms": 0.4, "status": 400, "cache_hit": null, "prompt_tokens": null, "output_tokens": null, "thinking_tokens": null, "best_distance": null}
{"timestamp": "2026-11-15T07:15:27.449921+00:00", "question": "Who won the 1994 World Cup?", "answer": "I don't have enough information about that.", "error": null, "refused": true, "sources": [], "latency_ms": 81.6, "status": 200, "cache_hit": null, "prompt_tokens": null, "output_tokens": null, "thinking_tokens": null, "best_distance": 0.8859}
{"timestamp": "2026-11-15T07:15:33.844099+00:00", "question": "forced failure test", "answer": null, "error": "RuntimeError: forced failure (X-Force-Failure)", "refused": null, "sources": null, "latency_ms": 0.5, "status": 500, "cache_hit": null, "prompt_tokens": null, "output_tokens": null, "thinking_tokens": null, "best_distance": null}
{"timestamp": "2026-11-15T07:15:35.917407+00:00", "question": "Can I change my meal plan tier after the semester starts?", "answer": "Yes, you can change your meal plan tier once, but only in the first ten days of the semester. After that, it i…", "error": null, "refused": false, "sources": ["admin_dining_dollars.txt", "admin_meal_plan_changes.txt", "dining_kestrel_commons.txt", "dining_kestrel_commons_followup.txt", "dining_north_kitchen_followup.txt", "dining_pellew_dining_hall_followup.txt", "dining_verrill_street_grill.txt", "money_jobs.txt"], "latency_ms": 739.3, "status": 200, "cache_hit": false, "prompt_tokens": 980, "output_tokens": 43, "thinking_tokens": 0, "best_distance": 0.1647}
{"timestamp": "2026-11-15T07:15:38.710608+00:00", "question": "Does taking summer courses for extra credit hours get me a better housing lottery number?", "answer": "No, taking summer courses for extra credit hours does not get you a better housing lottery number. Instead, ju…", "error": null, "refused": false, "sources": ["admin_add_drop_deadline.txt", "admin_campus_jobs_and_financial_aid.txt", "admin_housing_lottery.txt", "admin_meal_plan_changes.txt", "admin_pass_fail_option.txt", "advising_registration.txt", "dining_halden_hall.txt", "housing_aldridge_hall.txt"], "latency_ms": 677.1, "status": 200, "cache_hit": false, "prompt_tokens": 867, "output_tokens": 65, "thinking_tokens": 0, "best_distance": 0.3875}
{"timestamp": "2026-11-15T07:15:41.448059+00:00", "question": "How late in the semester can I declare a pass/fail course?", "answer": "You can declare a pass/fail option as late as week eight, after you've seen your midterm. (Source: admin_pass_…", "error": null, "refused": false, "sources": ["admin_add_drop_deadline.txt", "admin_declaring_a_major.txt", "admin_grade_appeals.txt", "admin_graduation_requirements.txt", "admin_pass_fail_option.txt", "course_biol_160.txt", "course_cs_340.txt", "course_stat_150.txt"], "latency_ms": 880.2, "status": 200, "cache_hit": false, "prompt_tokens": 879, "output_tokens": 35, "thinking_tokens": 0, "best_distance": 0.2039}
{"timestamp": "2026-11-15T07:15:44.386484+00:00", "question": "Does the library stay open later during term or during reading week?", "answer": "Based on the documents, the library stays open later during term (until 2am) than during reading week (until 1…", "error": null, "refused": false, "sources": ["admin_library_holds.txt", "housing_calder_annexe_noise.txt", "housing_morrow_house_noise.txt", "money_jobs.txt", "money_textbooks.txt", "orientation_what_matters.txt", "study_group_rooms.txt", "study_library_hours.txt"], "latency_ms": 744.1, "status": 200, "cache_hit": false, "prompt_tokens": 847, "output_tokens": 72, "thinking_tokens": 0, "best_distance": 0.4392}
```

**Fields added after the three runs.** Records from the later timing sessions also
carry `model_call_ms` (the successful `generate_content` call alone), `attempts`
(1 means no retry) and `generate_ms` (all of `generate.py`: limiter sleep, retries,
backoff and the call). The records pasted above and the three official runs predate
them.

**Failed runs.** Both left a record rather than an absence:

- Record 6, status `400`: the empty question was rejected before the pipeline ran.
- Record 10, status `500`: I forced this one on purpose with the
  `AI201_ALLOW_FORCE_FAIL=1` test hook and the `X-Force-Failure: 1` header, to
  prove the error path is logged. No real pipeline error, timeout or Gemini
  failure happened in any of my runs.

## What It Costs

**Number:** about **$0.00037 per answered question**. A refused question costs $0.

**How I measured it.** I started `serve.py` fresh with `AI201_CACHE=0` and sent 21
answered questions, cycling through six of my test questions. The first request
of that run was the cold one (2729 ms) and is excluded. For the remaining 20, the
token counts are the ones the Gemini response reported for that call
(`prompt_tokens`, `output_tokens`, plus `thinking_tokens`, which are billed as
output and were 0 on every call). I multiplied them by the model's published
price, $0.30 per million input tokens and $2.50 per million output tokens
(`gemini-3.5-flash-lite`, standard tier, recorded 2026-11-14 in `criteria.md`),
and averaged. So the token counts are measured, but the price per token comes
from the pricing page. I did not read a dollar figure off a bill.

| | n | mean | p95 | max |
|---|---|---|---|---|
| Latency, warm | 20 | 1297 ms | 2052 ms | 8281 ms |
| Cost per answered question | 20 | $0.00037 | | $0.00042 |

One warm request took 8,281 ms, the only one over 5 s. I don't know why. This run
predates the timing fields and the limiter was still at 30, so it wasn't a limiter
sleep; a 429 retry (7 s of backoff) would fit, but I can't confirm it.

**At a hundred questions a day.** Using the measured $0.00037 per answered
question: 100 × $0.00037 = **$0.037 a day**, or about **$1.11 over 30 days**. Even
at the worst single answer I measured ($0.00047), that is $0.047 a day. This
assumes every question is answered; refused questions cost nothing, so real
traffic would cost less. The three test runs below measured $0.00038 each, which
rounds to the same arithmetic.

Note that the latency row above is from an earlier session. The three official
runs below, made later with no code changes, measured a warm p95 of 5981, 8671 and
8223 ms, so the 2052 ms figure does not hold up (see C2 below).

## Run Log and Verdicts

Three separate runs, nothing changed between them. Each mode (C1, C2/C3, C5)
started `serve.py` fresh with `AI201_CACHE=0` and `AI201_ALLOW_FORCE_FAIL=1`, and
wrote its own log, so the first request was always the cold one. Raw output for
every run is in `results/capstone_run1/` to `capstone_run3/`. The real output
below is from Run 1: log files are `logs/capstone_<mode>_run1.jsonl`, and the
analyzer and driver output is in `results/capstone_run1/`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| C1. Every request leaves one complete log record | 20 of 20 | 20/20 | 20/20 | 20/20 | MET |
| C2. Warm p95 latency under 5 s (20 warm, non-cached) | p95 < 5000 ms | 5981 ms | 8671 ms | 8223 ms | MISSED |
| C3. Mean cost per answered question under $0.002 | < $0.002 | $0.00038 | $0.00038 | $0.00038 | MET |
| C4. Clean checkout runs from RUNNING.md alone | first attempt, each time | pass (HTTP 200) | pass (HTTP 200) | pass (HTTP 200) | MET |
| C5. Gate holds through `POST /ask` | 5 of 5, each of 3 trials | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 | MET |

**C1.** Every request is logged by `serve.py::ask` (record written in its
`finally` block by `serve.py::write_log`); records are counted by
`analyze_log.py::main`, on requests sent by `capstone_test.py::c1`.
`results/capstone_run1/analyze_c1.txt`:

```
C1  one complete record per request (target 20 of 20)
    records: 20  unparseable lines: 0  duplicate timestamps: 0  statuses: {200: 18, 400: 1, 500: 1}
    -> MET
```

From `logs/capstone_c1_run1.jsonl`: the empty question (record 6, 400) and the
forced failure (record 10, 500). A refusal record is shown under C5.

```
{"timestamp": "2026-11-16T05:17:47.186189+00:00", "question": "", "answer": null, "error": "empty question", "refused": null, "sources": null, "latency_ms": 1.3, "status": 400, "cache_hit": null, "prompt_tokens": null, "output_tokens": null, "thinking_tokens": null, "best_distance": null}
{"timestamp": "2026-11-16T05:17:56.213254+00:00", "question": "forced failure test", "answer": null, "error": "RuntimeError: forced failure (X-Force-Failure)", "refused": null, "sources": null, "latency_ms": 0.2, "status": 500, "cache_hit": null, "prompt_tokens": null, "output_tokens": null, "thinking_tokens": null, "best_distance": null}
```

**C2.** `latency_ms` is measured in `serve.py::ask` around the whole request; p95
(nearest-rank) is computed by `analyze_log.py::p95` over warm, non-cached answered
records, excluding the first (cold) one. `results/capstone_run1/analyze_c2.txt`
(the C1 section it also prints is meaningless for this log, which has no 400 or
500 by design):

```
C2  warm p95 latency under 5000 ms
    n=20  p95=5981 ms  max=6580 ms  mean=2464 ms
    -> NOT MET
```

A slow warm record from `logs/capstone_c2_run1.jsonl` (record 2, 5671.8 ms):

```
{"timestamp": "2026-11-16T05:19:07.810663+00:00", "question": "Does the library stay open later during term or during reading week?", "answer": "The library stays open later during term, closing at 2am compared to 10pm during reading week. \n\nSource: *study_library_hours.txt*", "error": null, "refused": false, "sources": ["admin_library_holds.txt", "housing_calder_annexe_noise.txt", "housing_morrow_house_noise.txt", "money_jobs.txt", "money_textbooks.txt", "orientation_what_matters.txt", "study_group_rooms.txt", "study_library_hours.txt"], "latency_ms": 5671.8, "status": 200, "cache_hit": false, "prompt_tokens": 847, "output_tokens": 36, "thinking_tokens": 0, "best_distance": 0.4392}
```

**C3.** Token counts come from the Gemini response via `generate.py` and are
logged by `serve.py::ask`; cost is computed by `analyze_log.py::cost`.
`results/capstone_run1/analyze_c2.txt`:

```
C3  mean cost per answered question under $0.002
    n=20  mean=$0.00038  max=$0.00047  thinking tokens total=0
    -> MET
```

**C5.** Requests sent by `capstone_test.py::c5` (3 trials × 5 `OUT_OF_SCOPE`
questions); the refusal is decided in `app.py::ask_pipeline` and returned by
`serve.py::ask`. `results/capstone_run1/driver_c5.txt`:

```
trial 1: 5 of 5 refused
trial 2: 5 of 5 refused
trial 3: 5 of 5 refused
C5: MET
```

From `logs/capstone_c5_run1.jsonl` (record 1):

```
{"timestamp": "2026-11-16T05:20:50.884575+00:00", "question": "What is the capital of Mongolia?", "answer": "I don't have enough information about that.", "error": null, "refused": true, "sources": [], "latency_ms": 1004.7, "status": 200, "cache_hit": null, "prompt_tokens": null, "output_tokens": null, "thinking_tokens": null, "best_distance": 0.8246}
```

**C4.** Each attempt was a new `git clone` of this repo into an empty directory,
then only the Capstone steps of `RUNNING.md` in order (venv, `pip install -r
requirements.txt`, `.env` with my key, `python app.py index`, `python serve.py`,
then the health and ask calls). Every attempt used an empty home directory, so the
~80 MB embedding model downloaded for real each time. Each ran at commit 0060110,
and each took 879–996 s, of which `pip install` was about 11 minutes. No step
needed anything from outside the document. Driven by a PowerShell script of mine
(not in the repo); full output is in `results/capstone_c4_attempt1.txt` to
`attempt3.txt`. Attempt 1:

```
=== STEP: 4 build index
  stored   88 chunks in 28.5s
Ready. Try: python app.py ask "your question here"

=== STEP: 6 health + ask
{"corpus":"campus_life","detail":"ready","index_ready":true,"status":"ok"}
HTTP 200
```

The answer field was non-empty each time. In attempts 1 and 3 it began "The housing
lottery is not entirely random in the way most people assume" and cited
`admin_housing_lottery.txt`; attempt 2 began "According to `admin_housing_lottery.txt`, ...".

**C2, the miss: stage and mechanism.** Two things are established and one is not.

- *Not retrieval or my code.* After the three runs I added timing to the log
  (`model_call_ms`, `attempts`, `generate_ms`; see Instrumentation). In four later
  sessions of the same C2 test, everything outside `generate.py` (embedding, search,
  gate, Flask) took at most 422 ms, and the model call was 82–85% of the total
  latency in the clean sessions (`results/timing/`).
- *One cause of slow requests is the free-tier rate limit.* In two of those sessions
  the service answered 429: "Generate content requests per minute limit exceeded on
  Free Tier ... limit: 15". `config.py` had `REQUESTS_PER_MINUTE = 30` (changed to 14
  in The Improvement, below), twice the real limit, so the local limiter never slows the burst and `generate.py` retries with
  1 s / 2 s / 4 s backoff instead. Those retried requests took about 3.5–4 s while the
  successful call itself took about 0.5 s, and in session 2 one request failed
  outright with a 500 after 15.7 s.
- *Not established: why the official runs were slow.* They sent only 10–15 requests in
  any 60 s window, logged no rate-limit message, and still had 4, 10 and 14 warm
  requests over 3 s. So the rate limit does not explain them. The non-model stages
  were never slower than about 0.4 s in the later sessions, so the model call itself
  is the likely place, but the official runs predate the timing fields and I did not
  measure it there. Four later sessions measured p95 of 4012, 1077, 1944 and 1490 ms,
  so the tail comes and goes with the hosted service.

## The Improvement

**The change (one).** In `config.py`, `REQUESTS_PER_MINUTE` from 30 to 14. **Why:**
the C2 diagnosis found the free tier allows 15 model calls a minute but my local
limiter allowed 30, so a burst never waited locally and instead drew 429s that
`generate.py` retried with 1 s / 2 s / 4 s backoff (and, once, failed with a 500).
At 14 the limiter waits on purpose before the service has to push back. Nothing
else changed: the same targets, the same test drivers, the same burst of 20 warm
requests, three runs each on a fresh server.

**Before and after, side by side.** "Before" is the three runs above; "after" is
three new runs of the same test (`results/capstone_after_run1/` to `run3/`,
`logs/capstone_after_*_run*.jsonl`).

| Criterion | Target | Before 1 / 2 / 3 | Before | After 1 / 2 / 3 | After |
|---|---|---|---|---|---|
| C1. Every request leaves one complete log record | 20 of 20 | 20 / 20 / 20 | MET | 20 / 20 / 20 | MET |
| C2. Warm p95 latency under 5 s | p95 < 5000 ms | 5981 / 8671 / 8223 ms | MISSED | 1346 / 4006 / 2174 ms | MET |
| C3. Mean cost per answered question under $0.002 | < $0.002 | $0.00038 / $0.00038 / $0.00038 | MET | $0.00037 / $0.00038 / $0.00038 | MET |
| C4. Clean checkout runs from RUNNING.md alone | first attempt | pass / pass / pass | MET | pass / pass / pass | MET |
| C5. Gate holds through `POST /ask` | 5 of 5, each of 3 trials | 3 trials of 5/5 in each run | MET | 3 trials of 5/5 in each run | MET |

Other C2 numbers, same sessions (p95 is in the table above):

| | Before 1 / 2 / 3 | After 1 / 2 / 3 |
|---|---|---|
| Warm max | 6580 / 8838 / 8720 ms | **20256 / 23122 / 16394 ms** |
| Requests that needed a 429 retry | not logged | 0 / 1 / 0 |

**Did it help? Partly, and I can't claim the credit for the C2 pass.**

- *What it fixed:* the retry-and-fail behavior. Across the 60 warm requests in the
  three after-runs, one needed a 429 retry (run 2, which took 4006 ms) and none
  failed with a 500. C1, C3 and C5 stayed MET with the same numbers.
- *What it made worse:* the worst single request. The limiter now sleeps when a
  burst passes 14 calls in a minute, so each after-session had one warm request that
  took 16–23 s (the maximum row; e.g. record 15 of `capstone_after_c2_run3.jsonl`:
  16,394 ms total, 652 ms model call, 1 attempt). p95 doesn't show that: with 20 samples the
  nearest-rank p95 is the 19th value, so one outlier per session is invisible to the
  criterion as written. The C2 verdict is MET, but a user hitting that request would
  not call it fast.
- *Why I can't say the change caused the C2 pass:* before I made the change, two
  timing sessions (3 and 4) with the old limiter of 30 already measured a p95 of
  1944 and 1490 ms (`results/timing/`). The slow tail in the official before-runs
  had no retries in it, so a change to retry behavior could not have removed it. The
  tail comes and goes with the hosted service, and the after-runs landed in a good
  period.
- *C4 was re-run after pushing the change, and passed 3 of 3.* Three new clean
  clones of the pushed code each built the index and returned HTTP 200 with a
  non-empty answer, in 673–772 s (`results/capstone_c4_rerun1.txt` to
  `rerun3.txt`, which record the commit tested). The change touches `config.py`
  only, so this is a regression check, and there was no regression.

## What's Still Broken

- **C2 (met after the change, not understood).** p95 is under 5 s in all three
  after-runs, but see above for why that isn't credit to the change. First thing I'd do: run the 20-request
  test five more times on each limiter setting (30 and 14), alternating, so the
  comparison isn't between two different times of day. I stopped because that is
  the experiment that separates my change from the service's good and bad periods,
  and it needs more calls against a 15-a-minute quota than I wanted to spend.
- **If I tightened a target.** Everything except C2 was met, and two targets are
  loose: C3 is $0.002 against a measured $0.00038 (about 5× headroom), so I'd tighten
  it to $0.0005, which the measured mean and max ($0.00047) would still clear. For C2
  I'd keep the p95 line and add "no warm request over 10 s", because p95 over 20
  samples cannot see a single 16–23 s wait. These are additions for next time, not
  edits to the criteria above.
- **C4 passed 3 of 3, twice** (before the change, and again after it),
  but the first request after start is slow (12.4 s in attempt 1, cold, before the
  change; 5.5–18.4 s in the re-run) and the install takes 6–11 minutes. That is not
  a miss, only something a new reader should expect.
- **What It Costs** quotes a 2052 ms warm p95 from an earlier session that the
  three official runs don't reproduce. Don't rely on it.

## How I Used AI

**1.** I proposed a 15 s warm p95 (C2) and $0.01 per answer (C3) and asked Claude
if they would work. It called both too easy and suggested 5 s and $0.002, and told
me to exclude cached responses from both. I took its numbers. C3 had about 5x
headroom (measured $0.00038). C2 was missed (p95 5981, 8671, 8223 ms): its 1-3 s
estimate fit typical requests, not the slow group. I kept the targets and
diagnosed the miss.

**2.** After the C2 miss I told Claude to start by timing the model call, since I
had written that it was the slow stage but had only inferred it. Claude added a
`model_call_ms` timer and ran 21 requests. The model call never took over 916 ms,
even on requests that took 3.5–4 s, which contradicted my claim. The server log
showed the missing time was 429 retries: `config.py` allowed 30 requests a minute
and the free tier allows 15. I had it add `attempts` and `generate_ms` to measure
retries and backoff, ran three more sessions, and rewrote the C2 paragraph to say
what was established (retries cause some slow requests) and what wasn't (why the
official runs, which had no retries, were slow).
