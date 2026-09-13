# 블로그 자동 집필 · 검수 파이프라인 운영 지침

이 문서는 크론이 호출하는 에이전트가 따라야 하는 절차다. 크론 프롬프트는 이 파일을 읽으라고만 지시한다.

레포: `/home/bjpark/projects/currycurry3030.github.io`
발행처: https://bjpark-lab.github.io (GitHub Pages, Chirpy)

## 절대 규칙

1. **main 에 직접 커밋·푸시하지 않는다.** 초안은 `draft/*` 브랜치에만 올린다.
2. **주인님 승인 없이 발행되는 글은 없다.** 자동 머지 금지.
3. `safety_scan.py` 가 BLOCK/QUALITY 를 내면 **절대 제출하지 않는다.** 우회·규칙 완화 금지. 초안을 고친다.
4. 실제 개인 금융 수치, 보유 종목, 매수 의사, 회사 내부 정보는 어떤 형태로도 쓰지 않는다.
5. 글감이 떨어지면 **억지로 만들지 말고 멈추고 보고한다.** 빈 글을 채우는 것보다 안 쓰는 게 낫다.

## 실행 절차

### 1) 주제 선정

```bash
cd /home/bjpark/projects/currycurry3030.github.io
python3 tools/blog/next_topic.py --json
```

요일 자동 매핑: 화=stanford, 목=agentops, 토=data.
`--series` 로 강제 지정 가능. 주제가 소진되면 exit 1 과 함께 안내가 나온다 → 그때는 글을 쓰지 말고 주인님께 "주제 풀 보충 필요"라고 보고한다.

### 2) 근거 수집

브리프의 `source_file` / `evidence_from` 을 **실제로 읽는다.** 기억이나 추측으로 쓰지 않는다.

- stanford 시리즈: `stanford-ai-study/days/data/dayNN.json` 의 modules/core/sourceLinks
- agentops 시리즈: `~/.hermes/cron/output/<job_id>/*.md` 의 실제 실패 로그, `~/.hermes/skills/`, 세션 검색
- data 시리즈: 각 프로젝트 코드의 설계 판단. **데이터 값이 아니라 코드와 구조만 본다.**

숫자를 쓸 거면 그 숫자의 출처 파일을 확인한 것이어야 한다. 확인 못 한 숫자는 쓰지 않는다.

### 3) 집필

`_posts/YYYY-MM-DD-slug.md` 로 저장. frontmatter 필수:

```yaml
---
title: "..."
date: 2026-09-15 09:00:00 +0900
categories: [AI Engineering, Study Notes]
tags: [tag1, tag2, tag3]
---
```

품질 기준 (safety_scan 이 강제):
- 본문 공백 제외 1,200자 이상 12,000자 이하
- `##` 소제목 2개 이상
- Finance/RealEstate/Investing 카테고리면 면책 문구 필수

집필 원칙:
- 브리프의 `angle` 을 지킨다. 교과서 요약이 아니라 **하나의 판단**을 담는다.
- 첫 문단에서 이 글이 답하는 질문을 명시한다.
- 남의 글 인용은 3줄 이내 + 출처 링크.
- 코드는 실행되는 것만 싣는다. 의사코드면 그렇다고 밝힌다.
- 모르는 것은 모른다고 쓴다. 확신 없는 주장에 단정형을 쓰지 않는다.

### 4) 검사

```bash
python3 tools/blog/safety_scan.py _posts/2026-09-15-slug.md
```

BLOCK: 즉시 해당 문장 삭제/재작성.
QUALITY: 분량·구조 보완.
WARN: 지워도 되고 남겨도 되지만, 남긴다면 왜 안전한지 스스로 판단하고 검수 메시지에 딸려 나가게 둔다.

### 5) 제출

```bash
python3 tools/blog/submit_draft.py _posts/2026-09-15-slug.md --series stanford --topic-key day01
```

이 스크립트가 하는 일: 재검사 → draft 브랜치 생성·푸시 → 텔레그램 검수 요청 발송 → 주제 키 사용 완료 기록.
검사에 걸리면 아무것도 푸시하지 않고 중단한다.

### 6) 승인 후 (주인님이 승인했을 때만)

```bash
git checkout main && git pull
git merge --no-ff draft/<슬러그> -m "post: <제목>"
npm run build          # assets/js/dist 는 커밋 안 되지만 CI가 함
git push origin main
git push origin --delete draft/<슬러그>
```

GitHub Actions 가 빌드·배포한다. 배포 후 실제 URL 접속을 확인하고 보고한다.

## 검수 중단 안전장치

2주(발행일 기준 6회) 연속으로 승인 없이 draft 브랜치만 쌓이면 **크론을 일시정지하고 보고한다.**
쌓인 초안 목록: `git branch -r --list 'origin/draft/*'`

## 상태 파일

- `tools/blog/state.json` — 시리즈별 사용 완료 주제 키. 중복 발행 방지.
- `tools/blog/topic_pool.yml` — agentops/data 주제 풀. 소진되면 보충 필요.

## 수익화 체크포인트

누적 발행 20편 도달 시 주인님께 보고하고 다음을 판단받는다:
- 커스텀 도메인 구입 여부 (애드센스 승인 확률 직결)
- 개인정보처리방침 / 문의 페이지 추가
- 애드센스 신청

그 전까지는 광고 관련 작업을 하지 않는다.
