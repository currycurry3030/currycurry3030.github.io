# Stanford AI 30-Day Study

Public static learning site for a 30-day Stanford AI curriculum covering CS224N, CS336, CS329Z, and CS329A topics, plus 6 optional extension days, mapped to a generalized Process Memory / Recipe Advisor architecture.

## Structure

```
stanford-ai-study/
  index.html                 dashboard; renders day rows from days/data/*.json
  days/
    study_engine.css         shared styles (responsive; no per-day CSS)
    study_engine.js          shared renderer; fetches days/data/dayNN.json
    dayNN_YYYY-MM-DD.html    one shell per day (PC + mobile in one file)
    data/dayNN.json          all content for that day
```

To change a day's content, edit only `days/data/dayNN.json`. To change the
schedule or a course label, edit the same file — the dashboard reads it, so no
HTML needs touching. The only reason to edit a shell is a new day.

Because the pages `fetch()` their JSON, a day page must be served over http(s).
Opening the HTML from the filesystem will show a load error. Use `bash tools/run`
or any static server.

## Detailed learning format

Every mini-lecture module follows the same sequence:

1. 핵심
2. 쉬운 한국어 설명
3. 교수 설명 복원
4. AI/Agent 실무 연결
5. 핵심용어
6. Quiz

`sourceLabel` uses a numeric slide range only when the range has been verified from the source. Otherwise use a descriptive `Lecture Section`, `Topic`, `Reading`, or `Integration` label.

## Layout

PC and mobile share one file. The layout follows the viewport by default and can
be pinned with the header toggle (auto → PC → mobile) or a `?layout=pc|mobile`
query parameter; the choice persists in `stanford-study-layout`.

## Progress state

Module progress is the source of truth, stored per day in
`stanford-study-dayNN-progress-v3`. The engine derives two keys the dashboard
reads, so both views always agree:

- `stanford-day-N-summary` — `{done,total}`, shown as a "모듈 3/6" hint
- `stanford-day-N-done` — `"1"`/`"0"`, mirrored to the dashboard checkbox

Completing every module checks the day off automatically. Checking a day on the
dashboard is authoritative and clears that day's module state.

## Architecture used in the learning material

1. Knowledge Capture: Evaluation Event → Context Builder → Knowledge Extraction Harness → Evaluation Case → Process Memory
2. Recipe Decision: Current Context → Case Retrieval → Candidate ΔRecipe → ΔMetric Prediction → Constraint/OOD/Uncertainty → Top-k → Engineer Review
3. Learning / Improvement: Actual DOE Result → Prediction comparison → New Evaluation Case → Process Memory/Eval → system improvement

Process Memory is a shared source for both Human Knowledge Transfer and Agent Grounding.

## Validation

Run before publishing:

```bash
python3 tools/validate_stanford_study.py
```

The validator checks the module schema, quiz/term minimums, source URLs, shell
wiring, schedule sanity (unique, ordered, weekday-only dates), progress-key
uniqueness, orphan files, stale terminology, and common sensitive-string
patterns. Both GitHub workflows run it.

## Public-content constraints

Only generalized/synthetic educational examples are allowed. Do not add real internal data, server/account names, internal URLs, equipment/lot identifiers, proprietary recipe values, or local corporate paths. Use generic examples such as `LOT_A`, `EQP_X`, `CHAMBER_1`, `RECIPE_v1`, and `schema.table_a`.
