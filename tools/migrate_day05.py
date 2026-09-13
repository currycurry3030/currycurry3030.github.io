"""One-off migration: move Day 5 onto the shared study engine.

Day 5 predates the engine and still uses day05_modules_1..4.js + day05_app.js +
day05_detailed.css with its own short field names. This converts it to the
standard window.STUDY_DAY schema and a unified shell.

Run from the repo root:  python3 tools/migrate_day05.py
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAYS = ROOT / "stanford-ai-study" / "days"
INDEX = ROOT / "stanford-ai-study" / "index.html"

DATE = "2026-09-18"
SHELL_NAME = f"day05_{DATE}.html"

LEGACY = [
    "day05_app.js",
    "day05_detailed.css",
    "day05_modules_1.js",
    "day05_modules_2.js",
    "day05_modules_3.js",
    "day05_modules_4.js",
    f"day05_{DATE}_pc.html",
    f"day05_{DATE}_mobile.html",
]

SHELL = """<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
    <title>Day 5 · Benchmarking &amp; Evaluation 상세학습</title>
    <link rel="stylesheet" href="study_engine.css">
  </head>
  <body>
    <div id="study-app"></div>
    <script src="day05_modules.js"></script>
    <script src="study_engine.js"></script>
  </body>
</html>
"""


def load_legacy_modules() -> list[dict]:
    modules: list[dict] = []
    for part in range(1, 5):
        text = (DAYS / f"day05_modules_{part}.js").read_text(encoding="utf-8")
        match = re.fullmatch(
            r"\s*window\.DAY5_MODULES=\(window\.DAY5_MODULES\|\|\[\]\)\.concat\((\[.*\])\)\s*;?\s*",
            text,
            re.S,
        )
        assert match, f"unexpected legacy module file shape: part {part}"
        modules.extend(json.loads(match.group(1)))
    return modules


def convert(module: dict) -> dict:
    """Legacy keys: s=slides, t=title, k=core, e=easy, p=professor, w=practical, q=quiz."""
    return {
        "sourceLabel": f"Slides {module['s']}",
        "title": module["t"],
        "core": module["k"],
        "easy": module["e"],
        "professor": module["p"],
        "practical": module["w"],
        "terms": module["terms"],
        "quiz": module["q"],
    }


def main() -> None:
    modules = [convert(m) for m in load_legacy_modules()]

    data = {
        "day": 5,
        "date": DATE,
        "course": "CS224N",
        "title": "Benchmarking & Evaluation",
        "subtitle": "LLM Evaluation을 점수가 아니라 benchmark·metric·judge·신뢰성으로 이루어진 평가 시스템 설계로 이해한다.",
        "systemPosition": "Cross-loop · Evaluation Foundation",
        "systemMapping": "Benchmark 설계와 metric 선택이 Knowledge Capture·Recipe Decision·Learning 세 loop의 평가 기준을 모두 규정한다.",
        "progressKey": "stanford-study-day05-progress-v3",
        "file": SHELL_NAME,
        "sourceLinks": [
            {
                "label": "원본 PDF",
                "url": "https://web.stanford.edu/class/cs224n/slides_w26/cs224n-2026-lecture11-evaluation.pdf",
            },
            {"label": "CS224N", "url": "https://web.stanford.edu/class/cs224n/"},
        ],
        "modules": modules,
    }

    (DAYS / "day05_modules.js").write_text(
        "window.STUDY_DAY=" + json.dumps(data, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    (DAYS / SHELL_NAME).write_text(SHELL, encoding="utf-8")

    index = INDEX.read_text(encoding="utf-8")
    old_links = (
        f'<div class="links">'
        f'<a href="days/day05_{DATE}_pc.html">💻 PC 학습</a>'
        f'<a href="days/day05_{DATE}_mobile.html">📱 모바일 학습</a>'
        f"</div>"
    )
    new_links = f'<div class="links"><a href="days/{SHELL_NAME}">학습 시작 →</a></div>'
    assert old_links in index, "day 5 index links not found"
    INDEX.write_text(index.replace(old_links, new_links), encoding="utf-8")

    existing = [str((DAYS / name).relative_to(ROOT)) for name in LEGACY if (DAYS / name).exists()]
    if existing:
        subprocess.run(["git", "rm", "-q", *existing], cwd=ROOT, check=True)
    print(f"day 5 migrated: {len(modules)} modules, removed {len(existing)} legacy files")


if __name__ == "__main__":
    main()
