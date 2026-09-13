---
title: "학습 사이트 리팩토링: 중복 파일 70개를 지우며 배운 것"
date: 2026-09-13 11:00:00 +0900
categories: [Engineering, Refactoring]
tags: [jekyll, static-site, refactoring, ci]
---

30일 학습 사이트를 만들고 나서 정리를 한 번 했습니다. 기능 추가가 아니라 순수하게 구조만 손봤는데, 결과적으로 배포 버그 하나를 같이 잡았습니다. 과정에서 나온 판단들을 남깁니다.

## 1. 같은 파일을 두 번 쓰고 있었다

날짜마다 `dayNN_..._pc.html`과 `dayNN_..._mobile.html`이 따로 있었습니다. 36일치면 72개입니다. 그런데 두 파일의 차이를 실제로 비교해 보니 이게 전부였습니다.

```html
<body data-layout="pc">
<body data-layout="mobile">
```

CSS에는 이미 `@media(max-width:780px)`가 있어서 반응형은 진작 동작하고 있었습니다. 즉 두 파일 체제는 아무 일도 하지 않으면서 "날짜를 하나 추가하려면 파일을 두 개 만들어야 한다"는 비용만 만들고 있었습니다.

다만 그냥 지우면 기능이 하나 사라집니다. PC에서 모바일 레이아웃을 강제로 보는 용도였을 테니까요. 그래서 미디어 쿼리 대신 body 클래스로 레이아웃을 통일하고, 헤더에 토글을 뒀습니다.

```javascript
const LAYOUTS = ['auto', 'pc', 'mobile'];

const readLayout = () => {
  const fromQuery = new URLSearchParams(location.search).get('layout');
  if (LAYOUTS.includes(fromQuery)) return fromQuery;
  const stored = localStorage.getItem(LAYOUT_KEY);
  return LAYOUTS.includes(stored) ? stored : 'auto';
};

const isMobile = () => (layout === 'auto' ? NARROW.matches : layout === 'mobile');
```

레이아웃 판정을 미디어 쿼리에서 JS로 옮긴 게 핵심입니다. CSS 미디어 쿼리만 쓰면 "뷰포트는 넓지만 모바일 레이아웃을 보고 싶다"를 표현할 방법이 없습니다.

HTML 파일 70개가 사라졌고, 기능은 오히려 늘었습니다.

> 중복을 지울 때는 그 중복이 지탱하던 기능이 무엇이었는지 먼저 찾으세요. 없으면 삭제, 있으면 더 싼 방식으로 재구현입니다.
{: .prompt-tip }

## 2. 진행률이 두 곳에 따로 저장되고 있었다

이건 구조 문제가 아니라 그냥 버그였습니다.

- 대시보드 체크박스: `stanford-day-20-done`
- 학습 페이지 모듈 완료: `stanford-study-day20-progress-v3`

두 키가 서로를 전혀 모릅니다. 그래서 학습 페이지에서 모듈 6개를 전부 완료해도 대시보드는 여전히 미완료로 표시했습니다. 학습 동기를 유지하려고 만든 진행률이 오히려 "다 했는데 왜 0이지"라는 경험을 주고 있었던 셈입니다.

해결은 단일 방향으로 정리하는 것이었습니다. 모듈 상태를 source of truth로 두고, 거기서 대시보드용 값을 파생시킵니다.

```javascript
function persistProgress() {
  const total = D.modules.length;
  localStorage.setItem(D.progressKey, JSON.stringify([...done]));
  localStorage.setItem(summaryKey, JSON.stringify({ done: done.size, total }));
  localStorage.setItem(doneKey, done.size === total ? '1' : '0');
}
```

덤으로 대시보드에 "모듈 3/6" 같은 부분 진행률이 생겼습니다. 파생 데이터를 만들고 나니 표시할 수 있는 정보가 늘어난 것입니다.

역방향도 정의해야 합니다. 대시보드에서 직접 체크하면 그쪽을 authoritative로 보고 모듈 상태를 지웁니다. 양쪽이 서로를 덮어쓰면 어느 쪽도 믿을 수 없게 되므로, 방향을 명시적으로 정하는 게 중요합니다.

## 3. 데이터가 JS 안에 들어 있었다

각 날짜의 콘텐츠는 이렇게 저장돼 있었습니다.

```javascript
window.STUDY_DAY={"day":20,"date":"2026-10-09", ... };
```

사실상 JSON인데 JS 파일로 위장하고 있었습니다. 증거는 검증 스크립트에 있었습니다.

```python
match = re.fullmatch(r"\s*window\.STUDY_DAY\s*=\s*(\{.*\})\s*;?\s*", text, re.S)
return json.loads(match.group(1))
```

데이터를 읽으려고 정규식으로 JS를 뜯어내고 있다면, 그건 데이터를 잘못된 파일 형식에 넣어뒀다는 신호입니다.

`days/data/dayNN.json`으로 분리하고 엔진이 `fetch`하도록 바꿨습니다. 검증 스크립트는 `json.load` 한 줄이 됐습니다. 트레이드오프는 있습니다. `file://`로 열면 CORS 때문에 동작하지 않으므로 로컬에서도 정적 서버가 필요합니다. GitHub Pages 배포가 전제라 받아들였고, README에 명시했습니다.

더 큰 소득은 따로 있었습니다. 대시보드가 36개 날짜를 HTML에 하드코딩하고 있었는데, 날짜·제목·과목이 JSON과 HTML 양쪽에 중복돼 있었습니다. 둘이 어긋나도 아무도 모릅니다. JSON에서 행을 생성하도록 바꿔서 중복을 없앴습니다.

## 4. 검증 스크립트가 오히려 취약했다

원래 검증에는 이런 게 있었습니다.

```python
for marker in ("CS329A · Spring 2027", "CS230 · 공개 사이트 2025 · 영상 Fall 2018", ...):
    assert marker in index
```

학기 표기를 하나만 다듬어도 CI가 깨집니다. 이런 테스트는 버그를 잡는 게 아니라 리팩토링을 방해합니다.

문자열 매칭을 걷어내고 구조적 불변식을 검사하도록 바꿨습니다.

```python
def validate_schedule(days):
    """Dates must be unique, ordered, and on weekdays (the plan is 평일 1시간)."""
    dates = [datetime.date.fromisoformat(d["date"]) for d in days]
    assert len(set(dates)) == len(dates), "duplicate study dates"
    assert dates == sorted(dates), "study dates are out of order"
    weekend = [d.isoformat() for d in dates if d.weekday() >= 5]
    assert not weekend, f"weekend study dates: {weekend}"
```

"평일 30일 계획"이라는 약속을 코드로 옮긴 것입니다. 문구가 바뀌어도 안 깨지고, 날짜를 잘못 넣으면 반드시 깨집니다. orphan 파일 검사도 추가했습니다. 마이그레이션 때 파일을 남겨두는 실수를 CI가 대신 잡아줍니다.

## 5. 청소하다 발견한 진짜 버그

이 저장소는 Chirpy 테마를 fork해서 시작해서, 테마 배포용 파일이 그대로 남아 있었습니다. gem 릴리즈 워크플로, 이슈 템플릿 4종, commitlint, husky, 24KB짜리 CHANGELOG… 개인 블로그에는 전부 불필요합니다.

지우는 김에 워크플로를 읽다가 이걸 발견했습니다.

{% raw %}
```
.gitignore:        assets/js/dist
pages-deploy.yml:  (npm run build 없음)
js-selector.html:  <script defer src="/assets/js/dist/{{ js }}.min.js">
```
{% endraw %}

빌드 산출물이 gitignore인데 배포 워크플로가 빌드를 하지 않습니다. 즉 **배포된 모든 페이지가 404 나는 스크립트를 요청하고 있었습니다.** 테마의 JS가 전혀 로드되지 않는 상태였던 겁니다.

학습 사이트는 자체 JS라 멀쩡해서 눈치채기 어려웠습니다. 두 워크플로 모두에 에셋 빌드를 넣고, 액션 버전도 최신으로 올렸습니다.

> 정리 작업의 진짜 가치는 지운 파일 수가 아니라, 노이즈를 걷어내야 비로소 보이는 문제에 있습니다.
{: .prompt-tip }

## 순서에 대해

다섯 가지를 이 순서로 진행했습니다: 셸 통합 → 진행률 버그 → 레거시 마이그레이션 → 업스트림 정리 → 데이터 분리.

효과가 크고 위험이 낮은 것부터 배치했습니다. 셸 통합은 대상 파일이 72개로 많지만 변경 내용 자체는 기계적이라 위험이 낮습니다. 반대로 데이터 분리는 검증 스크립트와 대시보드를 동시에 건드려야 해서 마지막으로 미뤘습니다. 앞 단계에서 파일 구조가 이미 단순해진 뒤라 실제로 훨씬 쉬웠습니다.

각 단계마다 검증 스크립트를 돌리고 브라우저에서 실제 동작을 확인한 뒤 커밋했습니다. 커밋 5개가 각각 독립적으로 되돌릴 수 있는 상태입니다.

## 남긴 것

Ruby가 로컬에 없어서 Jekyll 빌드와 htmlproofer를 실행할 수 없었습니다. 그래서 `Gemfile`의 `gemspec` 의존(테마 잔재)과 오래된 `html-proofer ~> 3.18`은 손대지 않았습니다. 검증할 수 없는 변경은 하지 않는 편이 낫습니다.
