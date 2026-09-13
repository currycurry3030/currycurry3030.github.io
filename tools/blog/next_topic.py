#!/usr/bin/env python3
"""다음 글 주제를 정하고 집필용 브리프를 만든다.

시리즈 로테이션:
    화요일 → stanford : stanford-ai-study/days/data/dayNN.json 중 아직 글이 없는 가장 이른 날
    목요일 → agentops : Hermes 운영 사례 (스킬/크론/세션) — 주제 풀에서 미사용 항목
    토요일 → data     : 데이터 파이프라인 방법론 — 주제 풀에서 미사용 항목

이미 발행/초안 상태인 주제는 tools/blog/state.json 으로 중복을 막는다.

사용:
    python3 tools/blog/next_topic.py             # 오늘 요일 기준
    python3 tools/blog/next_topic.py --series stanford
    python3 tools/blog/next_topic.py --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOG_DIR = Path(__file__).resolve().parent
STATE_PATH = BLOG_DIR / "state.json"
POOL_PATH = BLOG_DIR / "topic_pool.yml"
STUDY_DATA = REPO_ROOT / "stanford-ai-study" / "days" / "data"
POSTS = REPO_ROOT / "_posts"

WEEKDAY_SERIES = {1: "stanford", 3: "agentops", 5: "data"}  # 월=0
SERIES_META = {
    "stanford": {
        "label": "스탠포드 AI 학습노트",
        "categories": ["AI Engineering", "Study Notes"],
        "angle": "커리큘럼 내용을 그대로 옮기지 말고, 그날 개념 중 '실제로 시스템에 적용할 때 걸리는 지점' 하나를 골라 깊게 쓴다.",
    },
    "agentops": {
        "label": "에이전트 운영 실전",
        "categories": ["AI Engineering", "Agents"],
        "angle": "성공담보다 실패와 그 원인을 쓴다. 재현 가능한 구체적 설정/코드/수치를 반드시 포함한다.",
    },
    "data": {
        "label": "데이터로 보는 것",
        "categories": ["Data Engineering"],
        "angle": "실제 개인 데이터는 절대 쓰지 않는다. 파이프라인 설계 판단과 합성/익명화 예시만 쓴다.",
    },
}


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"used": {}}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def existing_slugs() -> set[str]:
    """_posts 에 이미 있는 슬러그(날짜 제외)."""
    out = set()
    for p in POSTS.glob("*.md"):
        m = re.match(r"\d{4}-\d{2}-\d{2}-(.+)\.md$", p.name)
        if m:
            out.add(m.group(1))
    return out


def next_stanford(state: dict) -> dict | None:
    used = set(state["used"].get("stanford", []))
    for path in sorted(STUDY_DATA.glob("day*.json")):
        key = path.stem                      # day01
        if key in used:
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        modules = d.get("modules", [])
        return {
            "series": "stanford",
            "key": key,
            "title_seed": f"{d.get('course','')} {d.get('title','')}",
            "slug_seed": re.sub(r"[^a-z0-9]+", "-", str(d.get("title", key)).lower()).strip("-"),
            "source_file": str(path.relative_to(REPO_ROOT)),
            "brief": {
                "course": d.get("course"),
                "topic": d.get("title"),
                "subtitle": d.get("subtitle"),
                "system_position": d.get("systemPosition"),
                "module_titles": [m.get("title") for m in modules],
                "core_points": [c for m in modules for c in (m.get("core") or [])][:12],
                "source_links": d.get("sourceLinks", []),
            },
        }
    return None


def next_from_pool(series: str, state: dict) -> dict | None:
    import yaml
    pool = yaml.safe_load(POOL_PATH.read_text(encoding="utf-8"))
    used = set(state["used"].get(series, []))
    for item in pool.get(series, []):
        if item["key"] in used:
            continue
        return {
            "series": series,
            "key": item["key"],
            "title_seed": item["title"],
            "slug_seed": item["key"],
            "source_file": item.get("source", ""),
            "brief": {
                "topic": item["title"],
                "question": item["question"],
                "must_include": item.get("must_include", []),
                "evidence_from": item.get("source", ""),
            },
        }
    return None


def build(series: str) -> dict | None:
    state = load_state()
    topic = next_stanford(state) if series == "stanford" else next_from_pool(series, state)
    if topic is None:
        return None
    meta = SERIES_META[series]
    topic["series_label"] = meta["label"]
    topic["categories"] = meta["categories"]
    topic["angle"] = meta["angle"]
    today = dt.date.today()
    slug = topic["slug_seed"][:60] or topic["key"]
    if slug in existing_slugs():
        slug = f"{slug}-{today:%m%d}"
    topic["target_path"] = f"_posts/{today:%Y-%m-%d}-{slug}.md"
    topic["branch"] = f"draft/{today:%Y-%m-%d}-{slug}"
    return topic


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", choices=list(SERIES_META))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--mark-used", metavar="KEY", help="해당 시리즈의 KEY를 사용 완료로 기록")
    args = ap.parse_args()

    series = args.series or WEEKDAY_SERIES.get(dt.date.today().weekday())
    if series is None:
        print("오늘은 발행 요일이 아닙니다 (화/목/토).")
        return 0

    if args.mark_used:
        state = load_state()
        state["used"].setdefault(series, [])
        if args.mark_used not in state["used"][series]:
            state["used"][series].append(args.mark_used)
        save_state(state)
        print(f"기록: {series}/{args.mark_used}")
        return 0

    topic = build(series)
    if topic is None:
        print(f"[{series}] 남은 주제가 없습니다. topic_pool.yml 을 보충하세요.")
        return 1

    if args.json:
        print(json.dumps(topic, ensure_ascii=False, indent=2))
    else:
        b = topic["brief"]
        print(f"시리즈 : {topic['series_label']} ({topic['series']})")
        print(f"키     : {topic['key']}")
        print(f"주제   : {topic['title_seed']}")
        print(f"관점   : {topic['angle']}")
        print(f"파일   : {topic['target_path']}")
        print(f"브랜치 : {topic['branch']}")
        print(f"카테고리: {', '.join(topic['categories'])}")
        print("\n--- 집필 재료 ---")
        print(json.dumps(b, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
