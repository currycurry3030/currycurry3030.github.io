# Stanford AI 30-Day Study

Public static learning site for a 30-day Stanford AI curriculum covering CS224N, CS336, CS329Z, and CS329A topics, mapped to a generalized Process Memory / Recipe Advisor architecture.

## Detailed learning format

Day 5 is the hand-curated reference. Day 1–4 and 6–30 use the shared `days/study_engine.css` + `days/study_engine.js` renderer and one JSON-compatible `dayXX_modules.js` data file per day.

Every mini-lecture module follows the same sequence:

1. 핵심
2. 쉬운 한국어 설명
3. 교수 설명 복원
4. AI/Agent 실무 연결
5. 핵심용어
6. Quiz

`sourceLabel` uses a numeric slide range only when the range has been verified from the source. Otherwise use a descriptive `Lecture Section`, `Topic`, `Reading`, or `Integration` label.

## Progress state

Day 1–4 and 6–30 use `stanford-study-dayNN-progress-v3`. PC and mobile variants of the same day share the same key. Day 5 keeps its existing progress key for backward compatibility.

## Architecture used in the learning material

1. Knowledge Capture: Evaluation Event → Context Builder → Knowledge Extraction Harness → Evaluation Case → Process Memory
2. Recipe Decision: Current Context → Case Retrieval → Candidate ΔRecipe → ΔMetric Prediction → Constraint/OOD/Uncertainty → Top-k → Engineer Review
3. Learning / Improvement: Actual DOE Result → Prediction comparison → New Evaluation Case → Process Memory/Eval → system improvement

Process Memory is a shared source for both Human Knowledge Transfer and Agent Grounding.

## Validation

Run before publishing:

```bash
python tools/validate_stanford_study.py
```

The validator checks module schema, quiz/term minimums, source URLs, PC/mobile shells, progress-key uniqueness, stale terminology, and common sensitive-string patterns. GitHub Pages CI runs it before htmlproofer.

## Public-content constraints

Only generalized/synthetic educational examples are allowed. Do not add real internal data, server/account names, internal URLs, equipment/lot identifiers, proprietary recipe values, or local corporate paths. Use generic examples such as `LOT_A`, `EQP_X`, `CHAMBER_1`, `RECIPE_v1`, and `schema.table_a`.
