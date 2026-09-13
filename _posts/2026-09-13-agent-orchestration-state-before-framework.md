---
title: "Agent Orchestration: 프레임워크보다 State Schema가 먼저다"
date: 2026-09-13 13:00:00 +0900
categories: [AI Engineering, Agents]
tags: [agents, orchestration, state, workflow, evaluation]
---

여러 도구를 호출하고, 중간에 사람 검토를 받고, 실패하면 이어서 실행해야 하는 agent를 만들면 곧 framework를 고르게 됩니다. 하지만 먼저 결정할 것은 라이브러리가 아니라 **workflow가 공유하는 state의 계약**입니다.

DSPy는 LM pipeline을 text transformation graph와 선언적 module로 표현하고, 목표 metric에 맞춰 pipeline을 최적화하는 방식을 제안합니다.[1] 이 관점에서 중요한 것은 graph를 그리는 문법이 아니라, 각 단계가 어떤 입력을 받고 무엇을 갱신하는지입니다.

## 대화 기록을 state로 쓰면 생기는 일

처음에는 messages 배열 하나로 시작하기 쉽습니다. 요청, 검색 결과, 도구 출력, 판단 근거를 모두 대화에 붙이면 구현은 빠릅니다.

하지만 실행이 길어질수록 세 가지 질문에 답하기 어려워집니다.

1. 지금 이 결정은 어떤 데이터에 근거하는가
2. 다음 node가 실제로 읽어도 되는 값은 무엇인가
3. 실패 후 어디에서 다시 시작해도 되는가

대화 기록은 읽기 좋은 로그일 수 있지만, workflow의 data model은 아닙니다. 로그에는 순서가 있고 state에는 의미가 있습니다. 둘을 같은 구조로 두면 오래된 관찰과 현재 결정이 섞이고, node의 side effect 범위도 불명확해집니다.

## 먼저 state를 명사로 나누기

framework를 고르기 전에 domain의 명사를 적어 봅니다. 예를 들어 조사와 추천을 하는 agent라면 다음 정도가 출발점이 됩니다.

| State field | 의미 | 갱신 주체 |
|---|---|---|
| `request` | 사용자의 원래 목표와 제약 | 입력 node만 |
| `context` | 현재 상황을 설명하는 검증된 사실 | context builder |
| `candidates` | 비교 가능한 선택지 | retrieval / generation |
| `evidence_refs` | 원천으로 돌아갈 수 있는 포인터 | retrieval / verifier |
| `decision` | 사람이 읽을 제안과 이유 | decision node |
| `status` | 실행 단계와 종료 상태 | orchestrator |
| `trace` | 관찰·호출·오류의 append-only 기록 | 모든 node |

여기서 핵심은 `trace`와 나머지를 분리하는 것입니다. `trace`는 무슨 일이 일어났는지 남기고, 나머지 state는 다음 단계가 무엇을 해도 되는지 제한합니다. 한 node가 `request`를 임의로 바꾸지 못하게 하고, evidence 없이 `decision`을 완료 상태로 만들지 못하게 하는 식입니다.

> state schema는 데이터 저장 형식이 아니라, agent의 권한 경계를 드러내는 설계 문서다.
{: .prompt-tip }

## node는 작은 read/write 계약이어야 한다

"검색한다"는 node는 사실 여러 책임을 섞기 쉽습니다. query를 만들고, 후보를 가져오고, filter를 적용하고, 결과를 해석하고, 답변까지 작성하면 실패 원인을 찾기 어렵습니다.

대신 node마다 read/write field를 작게 잡습니다.

- `retrieve`: `request`, `context`를 읽고 `candidates`, `evidence_refs`를 쓴다
- `verify`: `candidates`, `evidence_refs`를 읽고 `verification`을 쓴다
- `decide`: 검증된 후보만 읽고 `decision`을 쓴다
- `publish`: `decision`을 읽고 외부 side effect를 수행한다

이 계약이 있으면 testing도 달라집니다. `retrieve`는 후보와 근거 포인터를 만들었는지, `verify`는 근거가 없는 후보를 통과시키지 않았는지 각각 검사할 수 있습니다. 전체 agent 성공률 하나를 보지 않고 실패 지점을 node 단위로 찾게 됩니다.

## Checkpoint는 재시작 기능이 아니라 판단 보존 장치다

긴 workflow에서는 중간 결과를 저장해야 합니다. 실제 orchestration 도구도 thread별 graph-state snapshot과 장기 store를 구분해, 중단 후 재개·복구와 thread를 넘는 지식 보존을 각각 다룹니다.[2]

다만 checkpoint가 있다고 무조건 resume하면 안 됩니다. 검색 결과, 권한, 외부 데이터가 바뀌었다면 예전 state가 현재의 판단 근거로 유효한지 다시 확인해야 합니다. 그래서 checkpoint에 state만 저장하지 말고 다음도 함께 남깁니다.

- state schema version
- 입력과 retrieval의 시각
- 사용한 tool과 model의 version
- 외부 조회 결과의 snapshot 또는 재조회 방법
- 재개 전에 다시 검증해야 하는 field

이 정보가 없으면 checkpoint는 복구 지점이 아니라 오래된 결정을 재생하는 버튼이 됩니다.

## Framework는 마지막에 고른다

이제야 framework를 비교할 수 있습니다. 질문도 더 구체적입니다.

- state를 명시적으로 inspect하고 versioning할 수 있는가
- node의 read/write 경계를 코드와 trace에서 확인할 수 있는가
- deterministic code, model call, human review를 같은 workflow에 넣을 수 있는가
- checkpoint와 retry가 외부 데이터의 freshness 정책과 충돌하지 않는가
- framework를 바꿔도 state schema와 eval set을 유지할 수 있는가

framework가 workflow를 정의하면 나중에 abstraction의 제약이 domain 모델이 됩니다. 반대로 state와 node 계약을 먼저 정하면, framework는 실행을 편하게 만드는 교체 가능한 구현 선택지가 됩니다.

## 정리

- 대화 기록은 로그이고, state는 workflow의 계약이다
- `trace`와 현재 판단 state를 분리한다
- node마다 작은 read/write 범위를 둔다
- checkpoint에는 state 외에 freshness와 재검증 조건을 남긴다
- framework 선택은 state·trace·testability를 기준으로 마지막에 한다

이 내용은 [30일 학습](/stanford-ai-study/) Day 18의 orchestration 주제와 연결됩니다. 관련 글로 [Agent를 점수 하나로 평가할 수 없는 이유]({% post_url 2026-09-13-why-agent-eval-needs-decomposition %})도 함께 보시면 좋습니다.

## Sources

[1] https://arxiv.org/abs/2310.03714
[2] https://docs.langchain.com/oss/python/langgraph/persistence
