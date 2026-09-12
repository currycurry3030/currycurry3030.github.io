# Stanford AI 30-Day Detailed Study Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Day 5에서 확정한 상세 학습 형식을 Day 1~4, 6~30 전체에 적용하고, 공통 Study Engine과 자동 schema/link/privacy 검증으로 유지보수 가능한 GitHub Pages 학습 사이트를 만든다.

**Architecture:** `study_engine.css`와 `study_engine.js`가 모든 상세 학습 페이지의 공통 UI/상태/렌더링을 담당한다. 각 Day의 콘텐츠는 `window.STUDY_DAY = {...}` 형태의 JSON-compatible `dayXX_modules.js`로 분리하며, PC/모바일 HTML은 얇은 shell로 유지한다. Day 5는 현재 상세 콘텐츠를 보존하고 이번 변경의 regression 기준으로 사용한다.

**Tech Stack:** Static HTML/CSS/JavaScript, GitHub Pages/Jekyll, Python 3 standard library validator, GitHub Actions/htmlproofer

**Spec:** `docs/superpowers/specs/2026-09-12-full-detailed-study-engine-design.md`

## Global Constraints

- Day 1~4, 6~30 총 29일을 상세 학습형으로 전환한다.
- 각 module은 `core/easy/professor/practical/terms/quiz`를 모두 가져야 한다.
- `quiz`는 최소 2개다.
- 근거가 확인되지 않은 slide 번호는 생성하지 않는다.
- PC/모바일 기존 공개 URL을 유지한다.
- PC와 모바일은 같은 Day progress key를 공유한다.
- Day 5의 기존 상세 콘텐츠와 progress key는 보존한다.
- 공개 페이지에는 실제 LOT/equipment/chamber/recipe/server/account/path/internal URL을 넣지 않는다.
- 실제 프로젝트 연결은 Knowledge Capture → Process Memory → Recipe Decision → Feedback/Improvement 3-loop architecture를 기준으로 한다.
- Transformer/GPU/KV cache 등은 억지로 recipe reasoning에 연결하지 않고 실제 runtime/backbone/context component에 매핑한다.
- 완료 시 Jekyll build, study-site htmlproofer, schema/privacy validator, GitHub Pages deploy가 모두 성공해야 한다.

---

## File Structure

### Create

- `stanford-ai-study/days/study_engine.css` — Day 1~4, 6~30 공통 responsive UI
- `stanford-ai-study/days/study_engine.js` — module rendering, navigation, quiz reveal, localStorage progress
- `stanford-ai-study/days/day01_modules.js` ... `day04_modules.js`, `day06_modules.js` ... `day30_modules.js` — Day별 상세 학습 데이터
- `tools/validate_stanford_study.py` — schema, link target, privacy, stale terminology 정적 검증

### Modify

- `stanford-ai-study/days/day01_2026-09-14_pc.html` ... `day30_2026-10-23_mobile.html` 중 Day 5 제외 58개 — 공통 engine을 로드하는 thin shell로 교체
- `.github/workflows/pages-deploy.yml` — Jekyll build 뒤 validator 실행 추가
- `stanford-ai-study/README.md` — detailed module schema와 수정 방법 문서화

### Preserve

- `stanford-ai-study/days/day05_2026-09-18_pc.html`
- `stanford-ai-study/days/day05_2026-09-18_mobile.html`
- `stanford-ai-study/days/day05_modules_1.js` ... `day05_modules_4.js`
- `stanford-ai-study/days/day05_app.js`
- `stanford-ai-study/days/day05_detailed.css`

---

### Task 1: Common Study Engine + Validator

**Files:**
- Create: `stanford-ai-study/days/study_engine.css`
- Create: `stanford-ai-study/days/study_engine.js`
- Create: `tools/validate_stanford_study.py`
- Modify: `.github/workflows/pages-deploy.yml`

**Interfaces:**
- Consumes: a browser global `window.STUDY_DAY` object loaded before `study_engine.js`
- Produces: `window.StudyEngine.render()` side effect at DOMContentLoaded; per-day localStorage key `stanford-study-dayNN-progress-v3`
- Validator consumes `dayXX_modules.js` files containing `window.STUDY_DAY = <JSON object>;`

- [ ] **Step 1: Write validator first**

Create `tools/validate_stanford_study.py` with these exact checks:

```python
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAYS = ROOT / "stanford-ai-study" / "days"
TARGET_DAYS = [d for d in range(1, 31) if d != 5]
REQUIRED_MODULE_KEYS = {"sourceLabel", "title", "core", "easy", "professor", "practical", "terms", "quiz"}
FORBIDDEN = ["Process RCA Agent", "process-rca-agent"]


def load_day(day: int) -> dict:
    path = DAYS / f"day{day:02d}_modules.js"
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"\s*window\.STUDY_DAY\s*=\s*(\{.*\})\s*;?\s*", text, re.S)
    assert match, f"{path}: expected JSON-compatible window.STUDY_DAY assignment"
    return json.loads(match.group(1))


def validate_day(day: int, data: dict) -> None:
    assert data["day"] == day
    assert len(data["modules"]) >= 4
    assert data["progressKey"] == f"stanford-study-day{day:02d}-progress-v3"
    for i, module in enumerate(data["modules"], start=1):
        missing = REQUIRED_MODULE_KEYS - module.keys()
        assert not missing, f"day {day} module {i}: missing {sorted(missing)}"
        assert len(module["core"]) >= 2
        assert len(module["terms"]) >= 3
        assert len(module["quiz"]) >= 2
        assert module["easy"].strip()
        assert module["professor"].strip()
        assert module["practical"].strip()


def main() -> None:
    for day in TARGET_DAYS:
        data = load_day(day)
        validate_day(day, data)
    for path in (ROOT / "stanford-ai-study").rglob("*"):
        if path.is_file() and path.suffix in {".html", ".js", ".md"}:
            text = path.read_text(encoding="utf-8")
            for token in FORBIDDEN:
                assert token not in text, f"{path}: forbidden token {token}"
    print("Stanford study validation passed")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run validator and verify RED**

Run:

```bash
python tools/validate_stanford_study.py
```

Expected: FAIL because `day01_modules.js` does not exist yet.

- [ ] **Step 3: Implement shared CSS**

`study_engine.css` must define: desktop 260px sticky sidebar, max-width 920px main content, mobile single-column layout, `.hero`, `.module`, `.card`, `.core`, `.easy`, `.prof`, `.work`, `.terms`, `.quiz`, `.progress`, `.module-nav`, `.source-links`, `.course-mode`. It must not depend on Jekyll theme CSS.

- [ ] **Step 4: Implement shared renderer**

`study_engine.js` must:

```js
const D = window.STUDY_DAY;
const done = new Set(JSON.parse(localStorage.getItem(D.progressKey) || "[]"));
let current = Math.max(0, Math.min(D.modules.length - 1, Number(location.hash.replace("#m", "")) || 0));
```

Required behaviors:

```text
render sidebar/select from D.modules
render one module at a time
render six sections in order: core → easy → professor → practical → terms → quiz
quiz answers hidden until button click
module completion toggles Set and persists to D.progressKey
PC/mobile use identical data and progress
hash #mN selects module N
previous/next buttons clamp at bounds
master link uses ../index.html
counter displays done.size / D.modules.length
```

- [ ] **Step 5: Add validator to Pages workflow**

Modify `.github/workflows/pages-deploy.yml` immediately after `Build site`:

```yaml
      - name: Validate Stanford study data
        run: python tools/validate_stanford_study.py
```

Keep the existing `_site/stanford-ai-study` htmlproofer step unchanged.

- [ ] **Step 6: Commit engine/validator scaffold**

```bash
git add stanford-ai-study/days/study_engine.css stanford-ai-study/days/study_engine.js tools/validate_stanford_study.py .github/workflows/pages-deploy.yml
git commit -m "feat: add shared Stanford study engine and validator"
```

---

### Task 2: CS224N Detailed Modules — Day 1~4

**Files:**
- Create: `stanford-ai-study/days/day01_modules.js`
- Create: `stanford-ai-study/days/day02_modules.js`
- Create: `stanford-ai-study/days/day03_modules.js`
- Create: `stanford-ai-study/days/day04_modules.js`
- Modify: eight Day 1~4 PC/mobile HTML shells

**Interfaces:**
- Each data file defines exactly one `window.STUDY_DAY` JSON-compatible object.
- Each shell loads `study_engine.css`, then its `dayXX_modules.js`, then `study_engine.js`.

- [ ] **Step 1: Create Day 1 data with 5 modules**

Modules:

```text
1. Attention motivation · sequence bottleneck and direct token interaction
2. Q/K/V and scaled dot-product attention
3. Multi-head attention and representation subspaces
4. Causal mask, positional information, autoregressive constraint
5. Transformer block: residual, normalization, MLP, context implications
```

Use the official 2026 Transformers slide URL already present in the existing Day 1 page as the primary source. Only include numeric slide ranges after verifying them; otherwise use `Lecture Section · ...`.

Practical mapping: LLM Backbone / long Evaluation Case context. Explicitly state that attention weights are not process causal explanations.

- [ ] **Step 2: Create Day 2 data with 5 modules**

Modules:

```text
1. Language-model pretraining objective
2. Data mixture, quality and scale
3. Scaling behavior and capability emergence caveats
4. Domain adaptation vs retrieval grounding
5. Pretraining limits: freshness, provenance, private knowledge
```

Practical mapping: distinguish model-weight knowledge from Process Memory/RAG grounding.

- [ ] **Step 3: Create Day 3 data with 5 modules**

Modules:

```text
1. Why post-training exists
2. Supervised fine-tuning and instruction data
3. Preference learning / reward modeling / RLHF
4. DPO and direct preference optimization intuition
5. Alignment, schema compliance, abstention and evidence behavior
```

Practical mapping: Knowledge Extraction Harness must enforce schema, evidence, abstention; not merely “fine-tune a model”.

- [ ] **Step 4: Create Day 4 data with 6 modules**

Modules:

```text
1. Why retrieval/tool use is needed
2. RAG pipeline: index → retrieve → rerank → context
3. Tool calling and structured interfaces
4. Agent loop: observe → decide → act → observe
5. Grounding, provenance and failure modes
6. Recipe Advisor mapping: retrieve_cases + process context + verifier
```

- [ ] **Step 5: Replace Day 1~4 shells**

Each PC shell must be no more than a lightweight structure equivalent to:

```html
<!doctype html><html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Day 1 · Transformers 상세학습</title>
<link rel="stylesheet" href="study_engine.css">
</head><body data-layout="pc"><div id="study-app"></div>
<script src="day01_modules.js"></script><script src="study_engine.js"></script></body></html>
```

Mobile shell differs only in `body data-layout="mobile"`, title, and device-switch URL generated from metadata.

- [ ] **Step 6: Run partial validator**

Temporarily invoke direct functions for Days 1~4 or run:

```bash
python - <<'PY'
from tools.validate_stanford_study import load_day, validate_day
for d in [1,2,3,4]: validate_day(d, load_day(d))
print("CS224N detailed modules OK")
PY
```

Expected: PASS.

- [ ] **Step 7: Commit CS224N batch**

```bash
git add stanford-ai-study/days/day0[1-4]_modules.js stanford-ai-study/days/day0[1-4]_2026-*_*.html
git commit -m "feat: expand CS224N days 1 to 4 into detailed modules"
```

---

### Task 3: CS336 Detailed Modules — Day 6~12

**Files:**
- Create: `day06_modules.js` ... `day12_modules.js`
- Modify: Day 6~12 PC/mobile shells

**Interfaces:** same Study Engine schema as Task 2.

- [ ] **Step 1: Day 6 Tokenization — 5 modules**

```text
1. Why tokenization exists
2. BPE merge intuition and vocabulary trade-offs
3. Multilingual/domain token fragmentation
4. Sequence length, token budget and cost
5. Process acronyms/recipe names and tokenizer diagnostics
```

- [ ] **Step 2: Day 7 Resource Accounting — 5 modules**

```text
1. Parameter/activation/optimizer memory
2. FLOPs and training compute
3. Memory bandwidth vs arithmetic throughput
4. Batch/sequence length cost scaling
5. Agent total cost = model + DB scan + network + tool result
```

- [ ] **Step 3: Day 8 Architecture & Hyperparameters — 5 modules**

```text
1. depth/width/head choices
2. residual stream and normalization choices
3. context length and position methods
4. training stability/hyperparameters
5. architecture knowledge as serving constraint, not domain reasoning
```

- [ ] **Step 4: Day 9 GPU & Parallelism — 5 modules**

```text
1. GPU execution/memory hierarchy intuition
2. data parallelism
3. tensor/model parallelism
4. pipeline/communication overhead
5. measure LLM vs retrieval/query bottleneck first
```

- [ ] **Step 5: Day 10 Inference — 6 modules**

```text
1. autoregressive decoding cost
2. prefill vs decode
3. KV cache
4. batching and continuous batching
5. quantization/latency-throughput trade-off
6. long Process Memory context: pruning, retrieval top-k, context budgeting
```

- [ ] **Step 6: Day 11 Mid/Post-training — 5 modules**

Focus on continued pretraining, SFT, data quality, domain behavior, and Evaluation Case extraction harness.

- [ ] **Step 7: Day 12 RLVR — 5 modules**

Focus on verifiable rewards, deterministic validators, reward hacking, subjective-vs-verifiable boundaries, Recipe constraint/schema checks.

- [ ] **Step 8: Replace 14 shells and run Days 6~12 validator**

```bash
python - <<'PY'
from tools.validate_stanford_study import load_day, validate_day
for d in range(6,13): validate_day(d, load_day(d))
print("CS336 detailed modules OK")
PY
```

- [ ] **Step 9: Commit CS336 batch**

```bash
git add stanford-ai-study/days/day0[6-9]_* stanford-ai-study/days/day1[0-2]_*
git commit -m "feat: expand CS336 days into detailed modules"
```

---

### Task 4: CS329Z Detailed Modules — Day 13~20

**Files:**
- Create: `day13_modules.js` ... `day20_modules.js`
- Modify: Day 13~20 PC/mobile shells

- [ ] **Step 1: Day 13 Compound AI Systems — 6 modules**

Cover model-vs-system, decomposition, data/tool/eval loops, three-loop Process Memory architecture, human transfer vs agent grounding, component contracts.

- [ ] **Step 2: Day 14 RAG — 6 modules**

Cover chunking/indexing, dense+sparse retrieval, reranking, metadata/hard filters, provenance, Evaluation Case as retrieval unit rather than arbitrary document chunks.

- [ ] **Step 3: Day 15 Tool Use & MCP — 5 modules**

Cover tool schema, interface contracts, MCP mental model, semantic/domain tools, least-privilege read-only operations.

- [ ] **Step 4: Day 16 Error Handling & Query Guardrails — 6 modules**

Must include exact operational pattern:

```text
estimate → summarize → sample → expand only if necessary
```

Also cover row/byte/time limits, retryable vs non-retryable errors, result truncation, idempotency/observability.

- [ ] **Step 5: Day 17 ReAct — 5 modules**

Cover Thought/Action/Observation concept without exposing chain-of-thought; use observable plan/action/observation state. Map to Recipe Decision pipeline.

- [ ] **Step 6: Day 18 Orchestration — 5 modules**

Cover state machine, dispatcher, parallelism, retries/checkpoints, framework choice based on observability/control rather than convenience.

- [ ] **Step 7: Day 19 Process Memory — 6 modules**

Must encode:

```text
Evidence → Evaluation Event → Evaluation Case (episodic source of truth) → validated Semantic Process Knowledge
```

Explain why Human Knowledge Transfer and Agent Grounding are two consumers of the same validated memory.

- [ ] **Step 8: Day 20 Agent Evaluation — 6 modules**

Separate Capture, Retrieval, Tool/Query, Prediction, Recommendation, Grounding/Human usefulness eval layers.

- [ ] **Step 9: Replace 16 shells and validate Days 13~20**

```bash
python - <<'PY'
from tools.validate_stanford_study import load_day, validate_day
for d in range(13,21): validate_day(d, load_day(d))
print("CS329Z detailed modules OK")
PY
```

- [ ] **Step 10: Commit CS329Z batch**

```bash
git add stanford-ai-study/days/day1[3-9]_* stanford-ai-study/days/day20_*
git commit -m "feat: expand CS329Z days into Process Memory modules"
```

---

### Task 5: CS329A Detailed Modules — Day 21~30

**Files:**
- Create: `day21_modules.js` ... `day30_modules.js`
- Modify: Day 21~30 PC/mobile shells

- [ ] **Step 1: Day 21 Test-time Compute — 5 modules**

Cover candidate sampling, search/reranking, compute-quality trade-off, verifier allocation, Recipe candidate Top-k.

- [ ] **Step 2: Day 22 Robust Verification — 6 modules**

Cover rule/model/tool verification, uncertainty/OOD, evidence consistency, abstention, hard safety constraints.

- [ ] **Step 3: Day 23 Execution Feedback — 5 modules**

Cover execution as evidence, prediction-vs-actual comparison, new Evaluation Event capture, feedback into Process Memory.

- [ ] **Step 4: Day 24 Multi-step Planning — 5 modules**

Cover plan decomposition, dependency ordering, re-planning after observations, stop conditions, engineer-review package.

- [ ] **Step 5: Day 25 Train-time Scaling / RL — 5 modules**

Cover data curation, expert-approved trajectories, reward/model pitfalls, avoiding self-generated contamination.

- [ ] **Step 6: Day 26 Open-ended Self-Improvement — 5 modules**

Cover improvement targets across model/retrieval/query/prompt/harness/verifier, offline eval gate, rollback.

- [ ] **Step 7: Day 27 Search & Deep Research — 5 modules**

Cover hypothesis branching, evidence gathering, pruning, contradiction handling, multiple Δrecipe/DOE candidates rather than single “root cause”.

- [ ] **Step 8: Day 28 Coding Agent & Harness — 6 modules**

Cover harness role, safe domain tools, Knowledge Extraction Harness/Compiler, schema validator, evidence linker, trace/checkpoints.

- [ ] **Step 9: Day 29 Long-horizon Evaluation — 5 modules**

Cover end-to-end success, failure taxonomy, memory pollution, context/retrieval/query/prediction/safety/grounding/human-interface failures.

- [ ] **Step 10: Day 30 Project Integration — 6 modules**

Cover the three loops end-to-end, component contracts, evaluation cases, Top-k output contract, feedback, v1 success criteria as decision support rather than autonomous recipe execution.

- [ ] **Step 11: Replace 20 shells and validate Days 21~30**

```bash
python - <<'PY'
from tools.validate_stanford_study import load_day, validate_day
for d in range(21,31): validate_day(d, load_day(d))
print("CS329A detailed modules OK")
PY
```

- [ ] **Step 12: Commit CS329A batch**

```bash
git add stanford-ai-study/days/day2[1-9]_* stanford-ai-study/days/day30_*
git commit -m "feat: expand CS329A days into detailed modules"
```

---

### Task 6: Full Regression, Documentation, and Deployment

**Files:**
- Modify: `stanford-ai-study/README.md`
- Verify: all `stanford-ai-study/days/*`
- Verify: `.github/workflows/pages-deploy.yml`

- [ ] **Step 1: Extend validator with HTML shell checks**

For each Day except 5 assert both PC/mobile files exist and contain:

```text
study_engine.css
dayXX_modules.js
study_engine.js
```

Also assert every `sourceLinks[].url` starts with `https://` and every module `sourceLabel` is non-empty.

- [ ] **Step 2: Add suspicious internal identifier scan**

Validator must fail on explicit examples of prohibited output patterns such as:

```python
SUSPICIOUS = [
    re.compile(r"/home/[A-Za-z0-9_.-]+/"),
    re.compile(r"(?:server|host)[-_]?[A-Za-z0-9]{3,}", re.I),
]
```

Do not fail on generic anonymized examples `server-a`, `schema.table_a`, `LOT_A`, `EQP_X`, `CHAMBER_1`, `RECIPE_v1`.

- [ ] **Step 3: Run full validator**

```bash
python tools/validate_stanford_study.py
```

Expected: `Stanford study validation passed`.

- [ ] **Step 4: Build Jekyll locally/CI-equivalent**

```bash
bundle exec jekyll b -d _site
bundle exec htmlproofer _site/stanford-ai-study --disable-external --check-html --allow_hash_href
```

Expected: both exit 0.

- [ ] **Step 5: Update README**

Document exact module schema, progress-key policy, source-label policy, and the command:

```bash
python tools/validate_stanford_study.py
```

- [ ] **Step 6: Search stale terminology**

```bash
grep -RniE 'Process RCA Agent|process-rca-agent' stanford-ai-study || true
```

Expected: no output.

- [ ] **Step 7: Commit regression/docs**

```bash
git add tools/validate_stanford_study.py stanford-ai-study/README.md
git commit -m "test: validate detailed Stanford study curriculum"
```

- [ ] **Step 8: Open PR and inspect changed files**

Expected scope: shared engine, validator/workflow, README, 29 module data files, 58 shells. Day 5 content files should be unchanged.

- [ ] **Step 9: Merge after PR is mergeable and checks pass**

Use squash merge to keep the public repo history concise.

- [ ] **Step 10: Verify GitHub Pages workflow**

Required successful steps:

```text
Build site
Validate Stanford study data
Test site
Upload site artifact
Deploy to GitHub Pages
```

- [ ] **Step 11: Verify representative deployed pages**

Check:

```text
Day 1 PC
Day 1 mobile
Day 5 PC (regression)
Day 13 PC
Day 19 mobile
Day 30 PC
master index
```

Each detailed page must expose all six section headings and module navigation.

- [ ] **Step 12: Final completion evidence**

Report:

```text
29 converted days
58 converted shells
module count by course
validator PASS
htmlproofer PASS
Pages build/deploy PASS
public URL
PR URL
```

Do not claim completion until all evidence is current-turn verified.
