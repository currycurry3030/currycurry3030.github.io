---
title: "AI Engineering Notes를 시작하며: 30일 학습 설계"
date: 2026-09-13 12:00:00 +0900
categories: [Learning, Curriculum]
tags: [llm, agents, evaluation, study-plan]
---

이 사이트는 AI 엔지니어링을 공부하고 실험한 내용을 장기적으로 축적하기 위한 개인 지식베이스입니다. 첫 글에서는 왜 이 순서로 공부하는지, 그리고 학습 자체를 어떻게 시스템으로 만들었는지 정리합니다.

## 강의 요약이 아니라 설계 연습으로

강의를 들으면 이해한 것 같지만, 며칠 뒤에 남는 건 용어뿐인 경우가 많습니다. 원인은 대체로 두 가지입니다.

1. 내 언어로 다시 설명해 본 적이 없다.
2. 내가 실제로 만들 시스템의 어느 부분에 해당하는지 연결하지 않았다.

그래서 모든 학습 단위를 다음 6단계로 고정했습니다.

1. 핵심 — 그 주제에서 반드시 남겨야 할 명제
2. 쉬운 한국어 설명 — 비유를 써서 다시 설명
3. 교수 설명 복원 — 강의가 왜 그 순서로 전개됐는지
4. AI/Agent 실무 연결 — 내 시스템의 어느 컴포넌트인지
5. 핵심용어
6. Quiz — active recall

3번과 4번이 핵심입니다. 3번은 개별 사실이 아니라 논증의 구조를 붙잡기 위한 것이고, 4번은 지식을 설계 결정으로 바꾸기 위한 것입니다.

## 왜 CS224N → CS336 → CS329Z → CS329A인가

순서에는 의도가 있습니다. 아래로 내려갈수록 추상화 수준이 올라가고, 앞 단계가 뒤 단계의 제약 조건이 됩니다.

| 과목 | 다루는 층위 | 이 층에서 답하는 질문 |
|---|---|---|
| CS224N | 모델 자체 | Transformer, pretraining, post-training은 무엇을 하는가 |
| CS336 | 모델을 만드는 비용 | FLOPs, 메모리, 병렬화, inference는 어떤 제약을 만드는가 |
| CS329Z | 모델을 쓰는 시스템 | RAG, tool use, memory, orchestration을 어떻게 조립하는가 |
| CS329A | 스스로 나아지는 시스템 | test-time scaling, verification, closed-loop improvement |

Agent를 먼저 공부하고 싶은 유혹이 크지만, CS336의 자원 회계를 건너뛰면 "context를 더 넣으면 되지 않나" 같은 판단을 비용 감각 없이 내리게 됩니다. inference 비용과 메모리 제약을 먼저 손에 익혀야 agent 설계에서 현실적인 선택지가 보입니다.

여기에 확장 6일(CS146S, CS229, CS234, CS231N, CS25, CS230)을 선택형으로 붙였습니다. 본 30일과 같은 규격이지만 완료율은 따로 집계합니다.

## 전체를 관통하는 하나의 아키텍처

30일 내내 같은 3-loop 아키텍처에 새 지식을 얹습니다. 매일 다른 주제를 배워도 붙일 자리가 정해져 있으면 지식이 흩어지지 않습니다.

1. **Knowledge Capture** — Evaluation Event → Context Builder → Knowledge Extraction Harness → Evaluation Case → Process Memory
2. **Recipe Decision** — Current Context → Case Retrieval → Δrecipe 후보 → ΔMetric 예측 → Constraint/OOD/Uncertainty → Top-k → Engineer Review
3. **Learning / Improvement** — 실제 결과 → 예측과 비교 → 새 Evaluation Case → Process Memory/Eval → 시스템 개선

예를 들어 RAG는 "문서 검색 기법"이 아니라 loop 2의 case retrieval 단계로 들어옵니다. evaluation은 별도 챕터가 아니라 세 loop 전부를 가로지르는 관심사가 됩니다.

## 학습 자체를 작은 시스템으로

계획만 세우고 3일 만에 끊기는 걸 여러 번 겪어서, 학습 진행 상황을 추적하는 정적 사이트를 같이 만들었습니다. 현재 36일 × 총 196개 모듈이 들어 있습니다.

- 날짜별 학습 페이지 하나 (PC/모바일 동일 파일, 레이아웃은 반응형)
- 모듈 단위 완료 체크와 진행률
- 오늘 학습할 날짜를 대시보드 상단에 자동 표시
- 모든 콘텐츠는 `days/data/dayNN.json` 한 곳에

구현과 리팩토링 과정은 [별도 글]({% post_url 2026-09-13-static-study-site-refactor %})에 정리했습니다.

[30일 학습 대시보드 열기](/stanford-ai-study/){: .btn .btn-primary }

> 이 사이트에는 공개 가능한 일반화된 내용과 synthetic 예시만 기록합니다.
{: .prompt-info }
