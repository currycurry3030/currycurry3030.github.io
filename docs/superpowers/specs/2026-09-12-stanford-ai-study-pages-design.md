# Stanford AI Study GitHub Pages 배포 설계

## 목표

기존 공개 GitHub Pages 사이트 `currycurry3030.github.io`를 유지하면서, 이번에 만든 30일 Stanford AI 학습자료를 독립적인 하위 경로 `/stanford-ai-study/`에 배포한다.

최종 사용자 URL은 다음을 목표로 한다.

- `https://currycurry3030.github.io/stanford-ai-study/`

## 현재 사이트 제약

- 기존 레포는 Chirpy 기반 Jekyll 사이트다.
- `main` 브랜치 push 시 `.github/workflows/pages-deploy.yml`이 Jekyll build → htmlproofer → GitHub Pages deploy를 수행한다.
- 따라서 기존 root 홈페이지/테마 설정을 수정하지 않고, Jekyll이 그대로 copy하는 정적 하위 디렉터리를 추가하는 방식이 가장 안전하다.

## 배포 구조

```text
currycurry3030.github.io/
├── ...기존 Chirpy 사이트...
└── stanford-ai-study/
    ├── index.html
    ├── README.md
    └── days/
        ├── day01_2026-09-14_pc.html
        ├── day01_2026-09-14_mobile.html
        ├── ...
        ├── day30_2026-10-23_pc.html
        └── day30_2026-10-23_mobile.html
```

총 학습 HTML은 `index.html + PC 30개 + 모바일 30개 = 61개`다.

## 콘텐츠 원칙

학습자료는 공개 저장소에 올라가므로 다음 원칙을 유지한다.

- 실제 사내 데이터, 서버명, 계정, 내부 URL, 장비/LOT/Recipe 식별자 미포함
- synthetic/비식별 예시만 사용
- 실제 업무 연결은 일반화된 구조로만 표현
- 핵심 시스템 프레임은 다음 3-loop architecture를 유지
  - Loop 1: Knowledge Capture
  - Loop 2: Recipe Decision
  - Loop 3: Learning / Improvement
- Process Memory는 Human Knowledge Transfer와 Agent Grounding의 공통 source로 설명

## 링크 정책

- 마스터 페이지에서 각 날짜의 PC/모바일 HTML은 상대경로 `days/...`로 연결한다.
- 각 일별 HTML에서 마스터로 돌아가는 링크는 `../index.html`을 사용한다.
- PC ↔ 모바일 전환도 상대경로를 사용한다.
- Stanford/논문 링크만 외부 URL을 사용한다.

이렇게 하면 GitHub Pages의 `/stanford-ai-study/` 하위 경로에서도 별도 base URL 변경 없이 작동한다.

## 기존 사이트와의 격리

- `_config.yml`, 기존 post, tab, asset, theme 파일은 수정하지 않는다.
- `/stanford-ai-study/` 디렉터리만 새로 추가한다.
- 기존 Chirpy navigation에 링크를 추가하지 않는다. 필요하면 별도 후속 작업으로 한다.

## 배포 방식

1. `/stanford-ai-study/` 정적 파일을 `main` 브랜치에 추가한다.
2. 기존 `pages-deploy.yml`이 자동으로 Jekyll build를 실행한다.
3. `htmlproofer`가 내부 링크와 HTML 오류를 검사한다.
4. GitHub Pages artifact가 배포된다.
5. 배포 후 `/stanford-ai-study/` 및 대표 Day 페이지를 확인한다.

별도 Pages workflow나 새 Jekyll config는 추가하지 않는다.

## 검증 항목

배포 전/후 다음을 확인한다.

- 마스터 페이지가 `/stanford-ai-study/`에서 열림
- 30일 모두 PC/모바일 링크가 존재
- PC → 모바일, 모바일 → PC 전환 링크 정상
- 이전/다음 Day 링크 정상
- `localStorage` 기반 진행률/완료 상태 정상
- 외부 Stanford/Paper 링크가 새 탭에서 열림
- root 홈페이지가 기존대로 정상 동작
- GitHub Actions Pages workflow 성공

## 실패 시 대응

- Jekyll build 실패: 새 하위 디렉터리 내 HTML 문법/파일명을 우선 확인
- htmlproofer 실패: broken relative link를 수정
- 하위 경로 404: Jekyll output artifact에 `stanford-ai-study/`가 포함됐는지 확인
- 기존 사이트 영향 발생: 이번 변경은 새 디렉터리만 추가하므로 해당 디렉터리 commit을 revert하면 원복 가능

## 범위 밖

이번 배포에서는 다음은 하지 않는다.

- 별도 React/Vite 앱 전환
- 별도 repository 생성
- custom domain 설정
- analytics 추가
- 로그인/서버/database 추가
- 기존 Chirpy 홈페이지 redesign

정적 HTML을 가장 작은 변경으로 공개하는 것을 우선한다.
