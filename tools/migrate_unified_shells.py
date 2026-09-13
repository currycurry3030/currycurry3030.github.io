"""One-off migration: merge per-day PC/mobile shells into a single responsive shell.

Run from the repo root:  python3 tools/migrate_unified_shells.py
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAYS = ROOT / "stanford-ai-study" / "days"
INDEX = ROOT / "stanford-ai-study" / "index.html"

SHELL = """<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
    <title>Day {day} · {title} 상세학습</title>
    <link rel="stylesheet" href="study_engine.css">
  </head>
  <body>
    <div id="study-app"></div>
    <script src="day{day:02d}_modules.js"></script>
    <script src="study_engine.js"></script>
  </body>
</html>
"""


def load(day: int) -> dict:
    text = (DAYS / f"day{day:02d}_modules.js").read_text(encoding="utf-8")
    match = re.fullmatch(r"\s*window\.STUDY_DAY\s*=\s*(\{.*\})\s*;?\s*", text, re.S)
    assert match, day
    return json.loads(match.group(1))


def main() -> None:
    index = INDEX.read_text(encoding="utf-8")
    removed: list[Path] = []

    for day in range(1, 37):
        modules = DAYS / f"day{day:02d}_modules.js"
        if not modules.exists():  # day 5 still uses the legacy layout
            continue

        data = load(day)
        date = data["date"]
        unified = f"day{day:02d}_{date}.html"

        (DAYS / unified).write_text(
            SHELL.format(day=day, title=data["title"]), encoding="utf-8"
        )

        for mode in ("pc", "mobile"):
            old = DAYS / f"day{day:02d}_{date}_{mode}.html"
            if old.exists():
                removed.append(old)

        # data no longer needs to know about sibling shells
        data.pop("pcFile", None)
        data.pop("mobileFile", None)
        data["file"] = unified
        modules.write_text(
            "window.STUDY_DAY=" + json.dumps(data, ensure_ascii=False) + ";\n",
            encoding="utf-8",
        )

        old_links = (
            f'<div class="links">'
            f'<a href="days/day{day:02d}_{date}_pc.html">💻 PC 학습</a>'
            f'<a href="days/day{day:02d}_{date}_mobile.html">📱 모바일 학습</a>'
            f"</div>"
        )
        new_links = f'<div class="links"><a href="days/{unified}">학습 시작 →</a></div>'
        assert old_links in index, f"index links not found for day {day}"
        index = index.replace(old_links, new_links)

    INDEX.write_text(index, encoding="utf-8")
    if removed:
        subprocess.run(
            ["git", "rm", "-q", *[str(p.relative_to(ROOT)) for p in removed]],
            cwd=ROOT,
            check=True,
        )
    print(f"unified shells written; removed {len(removed)} legacy shells")


if __name__ == "__main__":
    main()
