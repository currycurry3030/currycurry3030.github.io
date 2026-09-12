# Stanford AI 30-Day Detailed Study Engine 설계

## 목적

현재 Day 5 CS224N Evaluation에서 확정한 상세 학습 형식을 나머지 Day 1~4, 6~30에도 일관되게 적용한다.

모든 학습 모듈은 다음 순서를 갖는다.

1. 핵심
2. 쉬운 한국어 설명
3. 교수 설명 복원
4. AI/Agent 실무 연결
5. 핵심용어
6. Quiz

단순 요약 카드가 아니라, 원문 슬라이드/강의/읽을거리의 논리적 흐름을 복원해 실제 강의를 따라가는 느낌의 학습자료를 만드는 것이 목표다.

## 범위

- 대상: Day 1~4, Day 6~30 총 29일
- Day 5는 이미 상세형 기준 템플릿으로 사용
- PC/모바일 URL은 기존 주소를 유지
- `stanford-ai-study/index.html`의 30일 마스터 링크 구조는 유지
- 공개 GitHub Pages이므로 synthetic/비식별 예시만 사용

## 핵심 설계 선택

### 채택안: 공통 Study Engine + Day별 Module Data

공통 렌더러와 스타일은 한 번만 유지하고, 각 Day는 학습 콘텐츠 데이터만 별도 파일로 가진다.

예상 구조:

```text
stanford-ai-study/
├── index.html
└── days/
    ├── study_engine.css
    ├── study_engine.js
    ├── day01_2026-09-14_pc.html
    ├── day01_2026-09-14_mobile.html
    ├── day01_modules.js
    ├── day02_2026-09-15_pc.html
    ├── day02_2026-09-15_mobile.html
    ├── day02_modules.js
    ├── ...
    ├── day30_2026-10-23_pc.html
    ├── day30_2026-10-23_mobile.html
    └── day30_modules.js
```

Day 5는 현재의 4개 module 파일을 그대로 둘 수 있으나, 공통 Study Engine과 인터페이스를 맞출 수 있으면 점진적으로 같은 구조에 맞춘다. Day 5 내용 자체는 변경하지 않는다.

## Day별 콘텐츠 구조

각 Day는 보통 4~6개 미니강의 모듈로 구성한다.

원문 강의가 길거나 주제가 명확히 여러 덩어리로 나뉘는 날은 6~8개까지 허용한다. 임의로 모듈 수를 맞추지 않는다.

각 Module data schema는 아래 필드를 갖는다.

```js
{
  id: 1,
  sourceLabel: "Slides 1–8" | "Topic 1" | "Reading · Section X",
  title: "...",
  core: ["...", "..."],
  easy: "...",
  professor: "...",
  practical: "...",
  terms: [["Term", "한국어 설명"], ...],
  quiz: [["질문", "정답"], ...]
}
```

### 필드 원칙

- `core`: 2~5개 핵심 포인트
- `easy`: 처음 보는 한국인이 이해할 수 있도록 비유/직관 포함
- `professor`: 앞뒤 슬라이드/주제의 연결과 강의자의 논리적 의도를 복원
- `practical`: 실제 AI/Agent/Recipe Advisor 시스템에서 이 개념이 어디에 쓰이는지 설명
- `terms`: 영문 원어 + 한국어 맥락 설명
- `quiz`: 최소 2개, 권장 3개 Active Recall

## 원문 매핑 원칙

### Slide 범위를 확실히 확인한 경우

`Slides xx–yy`를 표시한다.

예:

```text
Module 2 · Slides 9–18 · Multi-head Attention
```

### Slide 범위를 확인하지 못한 경우

슬라이드 번호를 추정하지 않는다.

대신 다음 중 하나를 사용한다.

```text
Topic 1 · Tokenization Basics
Lecture Section · Tool Use
Reading · Inference Fundamentals
```

즉, 실제 근거가 없는 slide 번호를 생성하지 않는다.

## 학습자료 깊이 기준

Day 5와 동일한 교육적 깊이를 기준으로 한다.

각 모듈은 최소한 다음 질문에 답해야 한다.

- 이 부분에서 꼭 알아야 하는 것은 무엇인가?
- 처음 접하는 사람에게 어떻게 설명할 것인가?
- 왜 이 내용이 앞 내용 다음에 나오는가?
- 다음 내용과 어떻게 이어지는가?
- 실제 AI 시스템에서 어디에 쓰이는가?
- 어떤 용어를 영어 그대로 기억해야 하는가?
- 읽고 난 뒤 스스로 설명할 수 있는가?

### 금지 패턴

다음 수준의 요약으로 끝내지 않는다.

```text
"KV cache는 이전 key/value를 저장해 inference를 빠르게 한다."
```

대신 왜 autoregressive decoding에서 반복 계산이 발생하는지, prefill/decode가 어떻게 다른지, memory-bandwidth trade-off가 무엇인지, Recipe Advisor처럼 긴 context를 쓰는 시스템에서 어떤 영향을 주는지까지 연결한다.

## 실제 프로젝트 연결 구조

실무 연결은 현재 프로젝트의 다음 시스템 구조를 기준으로 통일한다.

```text
Loop 1 · Knowledge Capture
Evaluation Event
→ Context Builder
→ Knowledge Extraction Harness
→ Evaluation Case
→ Process Memory

Loop 2 · Recipe Decision
Current Context
→ Process Memory Retrieval
→ Candidate ΔRecipe
→ ΔMetric Prediction
→ Constraint / OOD / Uncertainty
→ Verifier / Rank Top-k
→ Engineer Review

Loop 3 · Learning / Improvement
Actual DOE Result
→ Prediction vs Actual
→ New Evaluation Case
→ Process Memory / Eval Set
→ Model / Retrieval / Harness / Verifier Improvement
```

### 직접적인 Agent 기능이 아닌 주제

Transformer, GPU parallelism, KV cache 등은 억지로 recipe reasoning에 연결하지 않는다.

다음과 같은 실제 시스템 component로 연결한다.

- LLM Backbone
- Model Runtime
- Context Builder
- Token Budget
- Inference / Serving
- Tool Runtime
- Eval Harness
- Process Memory

## Day별 실무 연결 방향

### CS224N · Day 1~5

언어모델 자체, pre/post-training, RAG/tool use, evaluation이 Process Memory와 Knowledge Extraction Harness의 기반이 되는 흐름으로 연결한다.

### CS336 · Day 6~12

Tokenizer, compute/memory, architecture, GPU, inference, post-training, RLVR를 모델 serving 및 실제 agent runtime 비용/검증 구조와 연결한다.

특히 수십 GB~수억 row의 공정 DB를 직접 LLM context에 넣는 방식과 구분하고, DB scan/query cost와 LLM token/serving cost를 별도로 다룬다.

### CS329Z · Day 13~20

Compound AI System, RAG, MCP/tools, error handling, ReAct, orchestration, Process Memory, Agent Evaluation을 실제 3-loop Recipe Advisor architecture에 직접 매핑한다.

### CS329A · Day 21~30

Test-time compute, verifier, execution feedback, planning, RL/self-improvement, search, harness, long-horizon eval을 안전한 Top-k DOE candidate 생성 및 feedback loop와 연결한다.

## PC / 모바일 UX

### 공통

- 한 번에 한 Module을 집중해서 보여줌
- 현재 module 번호/제목/원문 범위를 표시
- 모듈별 완료 상태 저장
- Quiz 정답은 기본 숨김
- 이전/다음 module navigation
- 30일 Master로 돌아가기
- 원문 강의/PDF 링크 유지

### PC

- 좌측: module navigation + 진행률
- 중앙: 상세 module 본문
- 필요 시 우측: 오늘의 실제 시스템 위치 / source links / cheat sheet

### 모바일

- 상단 select 또는 compact module navigator
- 본문은 단일 column
- tap target 최소 크기 확보
- 긴 교수 설명/용어/quiz도 가독성을 해치지 않도록 카드 분리

## localStorage

Day별로 key를 분리한다.

예:

```text
stanford-study-day01-progress-v3
stanford-study-day02-progress-v3
...
```

PC와 모바일은 같은 Day의 완료 상태를 공유한다.

Day 5의 기존 progress key는 가능한 한 유지해 기존 사용자의 완료 상태를 보존한다.

## 학습 시간에 대한 해석

기존 1시간/day 계획은 유지하되, 상세자료 전체를 반드시 1시간 안에 모두 읽는다는 뜻으로 강제하지 않는다.

각 Day 페이지에 다음 학습 모드를 지원한다.

- `1시간 핵심 코스`: 핵심 + 쉬운 설명 + Quiz 중심
- `Deep Dive`: 교수 설명 복원 + 용어 + 실무 연결까지 모두 읽기

UI를 과도하게 복잡하게 만들 필요는 없으며, 우선 섹션 배지/설명 수준으로 구현 가능하다.

## 데이터/보안 원칙

공개 GitHub Pages에 게시되므로 다음을 금지한다.

- 실제 LOT ID
- 실제 equipment/chamber ID
- 실제 recipe 값
- 사내 DB/table/server/account/path
- 내부 URL
- 비공개 프로젝트 코드/문서 표현

예시는 다음처럼 일반화한다.

- `LOT_A`
- `EQP_X`
- `CHAMBER_1`
- `RECIPE_v1`
- `schema.table_a`

## 구현 전략

### Phase 1 · Study Engine

- 공통 CSS
- 공통 JS renderer
- 공통 Module schema
- Day 1에 적용하여 Day 5와 UX/depth 비교

### Phase 2 · CS224N / CS336

- Day 1~4 상세화
- Day 6~12 상세화

### Phase 3 · CS329Z

- Day 13~20 상세화
- Process Memory / 3-loop 실무 연결을 가장 강하게 반영

### Phase 4 · CS329A

- Day 21~30 상세화
- candidate generation / verifier / feedback / long-horizon eval 연결

### Phase 5 · Regression / Deployment

- PC/mobile 전체 링크 검사
- module schema 검사
- privacy string 검사
- GitHub Pages build
- htmlproofer
- 대표 페이지 수동 확인

## 검증 기준

### 콘텐츠 검증

Day 1~30 각각:

- module 수 >= 4 (특수한 짧은 주제 제외 시 명시)
- 모든 module에 `core/easy/professor/practical/terms/quiz` 존재
- quiz >= 2
- practical section 존재
- source label 존재
- 근거 없는 slide 번호 없음

### 기능 검증

- PC → 모바일 링크 정상
- 모바일 → PC 링크 정상
- Master 링크 정상
- 이전/다음 Module 정상
- localStorage 진행률 정상
- Day 간 progress key 충돌 없음
- 원문 링크 유지

### 프로젝트/보안 검증

검색 결과 다음 문자열 0건을 목표로 한다.

```text
Process RCA Agent
process-rca-agent
실제 사내 식별자
```

공정 예시는 synthetic/generalized 형태만 사용한다.

### 배포 검증

GitHub Actions에서 다음 모두 성공해야 완료로 간주한다.

1. Jekyll build
2. `/stanford-ai-study` htmlproofer
3. artifact upload
4. GitHub Pages deploy

배포 후 대표 확인 페이지:

- Day 1
- Day 5
- Day 13
- Day 19
- Day 30
- PC / mobile 각각 최소 1개

## 완료 정의

다음 조건을 모두 만족하면 전체 재구성이 완료된 것으로 본다.

- Day 5를 제외한 29일이 상세 모듈형으로 전환됨
- Day 5와 동일한 6단계 학습 흐름을 가짐
- 기존 URL 유지
- 실제 프로젝트 연결이 3-loop architecture와 일관됨
- 공개 보안 원칙 준수
- GitHub Pages build/deploy 성공
- 대표 페이지가 실제 공개 URL에서 정상 렌더링됨
