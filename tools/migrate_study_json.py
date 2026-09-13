"""One-off migration: split day content out of JS into plain JSON.

Each `dayNN_modules.js` is really a JSON blob wrapped in `window.STUDY_DAY=...`.
This extracts it to `days/data/dayNN.json`, lifts the dashboard's course label
into the data, and points the shells at the fetching engine.

Run from the repo root:  python3 tools/migrate_study_json.py
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "stanford-ai-study"
DAYS = PUBLIC / "days"
DATA = DAYS / "data"
INDEX = PUBLIC / "index.html"

SHELL = """<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
    <title>Day {day} · {title} 상세학습</title>
    <link rel="stylesheet" href="study_engine.css">
  </head>
  <body>
    <div id="study-app">불러오는 중…</div>
    <script src="study_engine.js" data-day="{day:02d}"></script>
  </body>
</html>
"""

ROW = re.compile(
    r'<article class="day" data-date="(?P<date>[\d-]+)">'
    r"<div><b>Day (?P<day>\d+)</b><span>[\d-]+ · (?P<label>.*?)</span>"
    r"<h3>(?P<title>.*?)</h3></div>"
)


def index_labels() -> dict[int, str]:
    """The dashboard shows a richer course label (with term) than data['course']."""
    text = INDEX.read_text(encoding="utf-8")
    labels = {int(m.group("day")): m.group("label") for m in ROW.finditer(text)}
    assert len(labels) == 36, f"expected 36 dashboard rows, found {len(labels)}"
    return labels


def main() -> None:
    labels = index_labels()
    DATA.mkdir(exist_ok=True)
    removed: list[str] = []

    for day in range(1, 37):
        legacy = DAYS / f"day{day:02d}_modules.js"
        text = legacy.read_text(encoding="utf-8")
        match = re.fullmatch(r"\s*window\.STUDY_DAY\s*=\s*(\{.*\})\s*;?\s*", text, re.S)
        assert match, legacy
        data = json.loads(match.group(1))

        data["courseLabel"] = labels[day]
        # Ordered for readable diffs: metadata first, bulk content last.
        ordered = {
            key: data[key]
            for key in (
                "day",
                "date",
                "course",
                "courseLabel",
                "title",
                "subtitle",
                "systemPosition",
                "systemMapping",
                "progressKey",
                "file",
                "sourceLinks",
                "modules",
            )
        }

        (DATA / f"day{day:02d}.json").write_text(
            json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (DAYS / ordered["file"]).write_text(
            SHELL.format(day=day, title=ordered["title"]), encoding="utf-8"
        )
        removed.append(str(legacy.relative_to(ROOT)))

    subprocess.run(["git", "rm", "-q", *removed], cwd=ROOT, check=True)
    print(f"extracted {len(removed)} day files to days/data/*.json")


if __name__ == "__main__":
    main()
