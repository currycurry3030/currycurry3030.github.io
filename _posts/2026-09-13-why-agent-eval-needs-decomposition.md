---
title: "Agent를 점수 하나로 평가할 수 없는 이유"
date: 2026-09-13 20:00:00 +0900
categories: [AI Engineering, Evaluation]
tags: [agents, evaluation, benchmark, testing]
---

"우리 agent 성공률이 82%입니다"라는 말은 거의 아무 정보도 주지 않습니다. 무엇을 성공으로 봤는지, 어떤 환경에서 쟀는지, 언제 끝난 것으로 쳤는지가 빠져 있기 때문입니다. LLM benchmark를 재던 감각으로 agent를 재면 이런 숫자가 나옵니다.

## LM 평가와 agent 평가가 다른 지점

LM benchmark는 비교적 단순합니다. 입력이 있고 출력이 있고 정답이 있습니다. 같은 입력을 넣으면 같은 조건에서 채점됩니다.

agent는 **상호작용**합니다. 같은 요청이라도 환경 상태와 도구 동작에 따라 결과가 달라집니다. 그래서 agent task를 정의할 때는 요청만으로 부족하고 최소한 네 가지가 더 필요합니다.

| 요소 | 없으면 생기는 일 |
|---|---|
| Environment | 어제와 오늘 점수가 다른데 원인을 모름 |
| Tools | 도구 버전이 바뀌면 재현 불가 |
| Stopping criteria | 언제 실패로 볼지 판정이 흔들림 |
| Scorer | 최종 출력만 보고 side effect를 놓침 |

시험 문제만 정해놓고 시험 시간, 사용 가능한 도구, 종료 조건, 채점법을 정하지 않으면 성적을 비교할 수 없습니다. agent eval도 같습니다.

재현성을 위해 고정 fixture와 DB snapshot, 도구 버전을 함께 기록해야 합니다. 이걸 안 하면 "지난주보다 좋아졌다"를 증명할 수 없습니다.

> stopping criteria를 정의하지 않은 agent 평가는 채점 기준 없는 시험입니다. 점수는 나오지만 의미가 없습니다.
{: .prompt-warning }

## 계층으로 분해하기

전체 성공률 하나로는 무엇을 고쳐야 할지 알 수 없습니다. agent 파이프라인을 단계별로 쪼개서 각각 평가합니다. 제가 쓰는 구분은 이렇습니다.

**1. Capture — 정보를 제대로 구조화했는가**

가장 앞단이라 여기서 생긴 오류가 이후 전부로 전파됩니다. 두 가지를 분리해야 합니다.

- schema validity: 양식을 다 채웠는가
- field accuracy: 내용이 맞는가

양식을 완벽히 채웠지만 값이 틀린 경우가 흔합니다. 그리고 정보가 부족할 때 **모른다고 말했는지**(abstention)를 별도로 평가합니다. 빈칸을 그럴듯하게 채우는 것이 가장 위험한 실패 양식입니다.

**2. Retrieval / Tool safety — 맞는 것을 가져왔는가, 안전하게 썼는가**

검색 품질은 recall과 precision을 나눠 봅니다. 도구 사용은 성공 여부와 별개로 안전성을 봅니다. 되돌릴 수 없는 작업을 했는지, 권한 범위를 넘었는지는 결과가 맞았더라도 실패로 처리해야 합니다.

**3. Prediction / Candidate — 제안의 품질**

후보를 여러 개 내는 시스템이라면 상위 후보의 품질뿐 아니라 다양성도 봅니다. 상위 5개가 사실상 같은 제안이면 선택지를 준 게 아닙니다.

**4. Grounding / Human usefulness — 근거가 실재하고 쓸모 있는가**

인용한 근거가 실제로 존재하는지(citation correctness), 결론을 뒷받침하는지(evidence coverage)를 봅니다. 그리고 최종 질문은 **사람이 이걸로 실제 판단을 내릴 수 있는가** 입니다. 이건 자동 지표로 완전히 대체되지 않습니다. 사람이 수정한 내역(correction diff)이 좋은 신호가 됩니다.

## 고정 셋만 쓰면 그 시험에 과적합한다

평가 셋을 한 번 만들고 계속 쓰면 시스템이 그 benchmark에 최적화됩니다. 점수는 오르는데 실제 사용에서는 나아지지 않는 상태입니다.

두 가지를 같이 운영합니다.

1. **Regression set** — 20~100개 정도로 고정. 버전 간 비교용
2. **Fresh set** — 최근 실패, 사람과 의견이 갈린 사례, 낮은 확신도 사례를 계속 추가

매번 같은 기출문제로 기본 실력을 재면서, 새로 발견된 함정 문제도 계속 추가하는 방식입니다.

## contamination: 평가 셋을 agent가 읽으면 안 된다

메모리를 가진 agent를 평가할 때 특히 조심할 부분입니다. 평가 사례가 agent의 retrieval 대상에 들어가 있으면, agent는 문제를 푸는 게 아니라 **정답을 검색**합니다. 점수는 훌륭하게 나오고 실제 능력은 알 수 없습니다.

case store와 eval holdout 사이에 접근 경계를 두고, 정확히 일치하는 것뿐 아니라 의미적으로 겹치는 것도 주기적으로 검사해야 합니다.

## 정리

- agent task = 요청 + 환경 + 도구 + 종료 조건 + 채점자
- 전체 성공률 대신 capture / retrieval / prediction / grounding으로 분해
- schema validity와 field accuracy는 다른 지표다
- abstention(모른다고 말하기)을 별도로 평가한다
- 도구 안전성은 결과 정확도와 독립적으로 본다
- regression set + fresh set을 함께 운영한다
- 평가 데이터와 agent의 검색 대상을 분리한다

이 내용은 [30일 학습](/stanford-ai-study/) Day 20에 해당합니다. 관련 글로 [Agent Memory는 대화 기록이 아니다]({% post_url 2026-09-13-agent-memory-is-not-chat-history %})도 함께 보시면 좋습니다.
