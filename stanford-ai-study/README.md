# Stanford AI 30-Day Study

Public static learning site for a 30-day Stanford AI curriculum covering CS224N, CS336, CS329Z, and CS329A topics, mapped to a generalized Process Memory / Recipe Advisor architecture.

## Site

- Public URL: https://currycurry3030.github.io/stanford-ai-study/
- Master page: `index.html`
- Daily pages: `days/`
- Each day has separate PC and mobile HTML pages.

## Architecture used in the learning material

The practical examples are organized around three loops:

1. Knowledge Capture: Evaluation Event → Context Builder → Knowledge Extraction Harness → Evaluation Case → Process Memory
2. Recipe Decision: Current Context → Case Retrieval → Candidate ΔRecipe → ΔMetric Prediction → Constraint/OOD/Uncertainty → Top-k → Engineer Review
3. Learning / Improvement: Actual DOE Result → Prediction comparison → New Evaluation Case → Process Memory/Eval → system improvement

Process Memory is described as a shared source for both Human Knowledge Transfer and Agent Grounding.

## Public-content constraints

This repository contains generalized/synthetic educational examples only. Do not add real internal data, server/account names, internal URLs, equipment/lot identifiers, or proprietary recipe values.

## Updating

Keep all links inside this subtree relative:

- Master → daily page: `days/<file>.html`
- Daily page → master: `../index.html`
- PC ↔ mobile: sibling relative path

The existing repository GitHub Pages workflow builds the root Jekyll site and copies this static subtree into the deployed site.
