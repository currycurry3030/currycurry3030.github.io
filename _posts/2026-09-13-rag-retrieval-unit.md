---
title: "RAG의 검색 단위를 다시 생각하기: chunk가 아니라 사건"
date: 2026-09-13 09:30:00 +0900
categories: [AI Engineering, RAG]
tags: [rag, retrieval, reranking, evaluation, grounding]
---

RAG를 처음 붙일 때 대부분 문서를 일정 길이로 자르는 것부터 시작합니다. 그런데 실제로 답변 품질이 안 나올 때, 원인이 embedding 모델이 아니라 **검색 단위를 잘못 잡은 것**인 경우가 많습니다. CS329Z의 RAG 파트를 정리하면서 이 부분을 다시 생각해 봤습니다.

## chunk 500자의 문제

문서를 500자씩 기계적으로 자르면 이런 일이 생깁니다. 어떤 평가 기록이 "이런 조건에서 / 이렇게 바꿨더니 / 이런 결과가 나왔고 / 그래서 이렇게 해석했다"는 4단 구조를 갖고 있을 때, 조건과 결론이 서로 다른 chunk로 떨어집니다.

검색은 "결론" chunk를 잘 찾아줍니다. 그런데 그 결론이 **어떤 조건에서 성립하는지**가 함께 오지 않습니다. 모델은 조건 없는 결론을 받아서 그럴듯하게 일반화합니다. 이건 hallucination이라기보다 애초에 근거를 반쪽만 준 결과입니다.

그래서 chunk size를 조절하는 대신 질문을 바꿔야 합니다. "몇 자로 자를까"가 아니라 **"이 도메인에서 의미가 보존되는 최소 단위는 무엇인가"** 입니다.

제가 다루는 도메인에서는 그 단위가 "평가 1건"이었습니다. 그래서 retrieval unit을 Evaluation Case로 잡고, 하나의 case에 intent, conditions, delta, result, interpretation, conclusion, evidence reference를 함께 담았습니다. 임의 경계가 아니라 도메인의 사건 경계를 따르는 것입니다.

> chunking은 텍스트 처리 문제처럼 보이지만 실제로는 도메인 모델링 문제입니다.
{: .prompt-tip }

## dense만으로는 부족한 이유

semantic embedding은 "비슷한 뜻"을 잘 찾습니다. 그런데 실무 데이터에는 embedding이 약한 신호가 섞여 있습니다. 장비 코드, step 번호, recipe 버전, 사내 약어 같은 것들입니다. `EQP_X`와 `EQP_Y`는 embedding 공간에서 거의 같은 위치에 있지만 현업에서는 완전히 다른 것입니다.

그래서 셋을 나눠서 씁니다.

| 신호 | 담당 | 예시 |
|---|---|---|
| 의미 유사도 | dense retrieval | "수율이 떨어졌다" ↔ "yield 저하" |
| 정확한 토큰 | sparse/lexical | `RECIPE_v1`, step code |
| 명시적 조건 | structured filter | 공정, 기간, 제품군 |

비유하자면 뜻으로 찾는 사람과 번호로 찾는 사람을 같이 쓰는 것입니다.

## hard filter는 양날의 검

structured metadata로 검색 전에 후보를 좁히는 건 효과적입니다. 다른 공정 단계의 사례를 애초에 제외하면 정밀도가 올라갑니다.

문제는 metadata가 틀렸을 때입니다. 잘못 태깅된 좋은 사례가 검색 결과에 아예 등장하지 못하고, **그 사실을 아무도 모릅니다.** recall 손실은 조용히 일어납니다.

두 가지를 같이 둡니다.

1. filter를 적용한 이유를 trace에 남긴다. 나중에 "왜 이 case가 안 나왔지"를 추적할 수 있어야 합니다.
2. exact match가 없으면 fallback 범위를 단계적으로 넓힌다. 신규 공정처럼 과거 사례가 없는 경우 빈 결과보다 "조건이 다르지만 참고 가능한 사례"가 낫습니다.

## reranking: 유사도와 적용 가능성은 다르다

1차 retrieval은 넓게 가져오고, reranker가 정밀하게 고릅니다. 후보 50개를 모아 면접으로 5명을 뽑는 구조입니다.

여기서 중요한 건 **텍스트 유사도와 적용 가능성이 별개 점수**라는 것입니다. 어떤 과거 사례가 지금 질문과 표현이 매우 비슷해도, 조건이 달라서 적용하면 안 되는 경우가 있습니다. 오히려 "하지 말아야 할 사례"일 수도 있습니다.

rerank 단계에서 보는 feature를 분리해 둡니다.

- intent similarity — 무엇을 하려는지가 비슷한가
- condition match — 조건이 실제로 겹치는가
- delta overlap — 변경 내용이 유사한가
- metric target match — 목표 지표가 같은가
- recency — 최근 사례인가
- evidence completeness — 근거가 충분히 남아 있는가

top-k를 고를 때 diversity도 봅니다. 상위 5개가 전부 같은 패턴이면 후보를 5개 준 것 같지만 실질적으로는 1개를 준 것입니다.

## 결론만 주지 말고 근거로 내려갈 길을 남기기

case summary만 컨텍스트에 넣으면 "예전에 이렇게 했다"는 메모만 보는 셈입니다. 그 판단이 맞았는지 검증할 방법이 없습니다.

그렇다고 원천 데이터를 전부 프롬프트에 넣을 수도 없습니다. 절충안은 **provenance pointer**입니다. case에 evidence reference와 query key를 저장해 두고, 평소에는 결론과 요약만 쓰되 필요할 때 tool로 원천 집계를 다시 확인합니다.

on-demand load라고 부르는 이 방식은 토큰 예산과 검증 가능성을 동시에 잡습니다.

## retrieval을 어떻게 평가할까

가장 중요한 부분인데 가장 자주 생략됩니다. "RAG 품질"을 하나의 숫자로 보면 무엇을 고쳐야 할지 알 수 없습니다. 최소한 두 질문을 나눠야 합니다.

1. **정답 문서를 후보에 넣었는가** — Recall@k. 여기서 실패하면 reranker를 아무리 고쳐도 소용없습니다.
2. **상위 k개가 실제로 쓸 만한가** — Applicability precision. 여기서 실패하면 rerank feature를 봐야 합니다.

그 다음 단계로 evidence coverage와 citation correctness를 봅니다. 검색이 맞았어도 인용이 틀리면 grounding은 실패한 것입니다.

평가 셋을 만들 때는 각 상황마다 relevant / irrelevant / applicable / contraindicated 라벨을 붙여 뒀습니다. 특히 마지막 라벨이 중요합니다. "관련은 있지만 적용하면 안 되는 사례"를 구분하지 않으면 시스템이 위험한 추천을 해도 점수는 높게 나옵니다.

## 정리

- chunk size 튜닝보다 도메인의 사건 경계를 찾는 게 먼저다
- dense / sparse / structured 세 신호는 각각 담당이 다르다
- hard filter의 recall 손실은 조용하다. trace와 fallback을 같이 두자
- 유사도와 적용 가능성은 다른 점수다
- 결론과 함께 근거로 내려갈 포인터를 남기자
- retrieval 평가는 recall과 precision을 반드시 분리한다

이 내용은 [30일 학습](/stanford-ai-study/) Day 14에 해당합니다.
