from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "stanford-ai-study"
DAYS = PUBLIC / "days"
DATA = DAYS / "data"
CORE_DAYS = 30
EXTENSION_DAYS = 6
TARGET_DAYS = list(range(1, CORE_DAYS + EXTENSION_DAYS + 1))
REQUIRED_MODULE_KEYS = {"sourceLabel", "title", "core", "easy", "professor", "practical", "terms", "quiz"}
FORBIDDEN = ("Process RCA Agent", "process-rca-agent")
SUSPICIOUS = (
    re.compile(r"/home/[A-Za-z0-9_.-]+/"),
    re.compile(r"(?i)password\s*[=:]"),
    re.compile(r"(?i)api[_-]?key\s*[=:]"),
)


def load_day(day: int) -> dict:
    return json.loads((DATA / f"day{day:02d}.json").read_text(encoding="utf-8"))


def validate_day(day: int, data: dict) -> None:
    assert data["day"] == day
    assert len(data["modules"]) >= 4
    assert data["progressKey"] == f"stanford-study-day{day:02d}-progress-v3"
    assert data["file"] == f'day{day:02d}_{data["date"]}.html'
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", data["date"]), (day, data["date"])

    # The dashboard renders these, so an empty value would ship a blank row.
    for key in ("course", "courseLabel", "title", "subtitle", "systemPosition", "systemMapping"):
        assert str(data.get(key, "")).strip(), (day, key)
    # Both strings are shown to the reader (sidebar vs dashboard), so they must
    # at least agree on the course code.
    code = data["course"].split("·")[0].strip()
    assert data["courseLabel"].startswith(code), (day, code, data["courseLabel"])

    for link in data["sourceLinks"]:
        assert link["url"].startswith("https://"), (day, link)
        assert link["label"].strip()

    for index, module in enumerate(data["modules"], start=1):
        missing = REQUIRED_MODULE_KEYS - module.keys()
        assert not missing, f"day {day} module {index}: missing {sorted(missing)}"
        assert len(module["core"]) >= 2
        assert len(module["terms"]) >= 3
        assert len(module["quiz"]) >= 2
        for key in ("easy", "professor", "practical", "sourceLabel", "title"):
            assert str(module[key]).strip(), (day, index, key)
        for term in module["terms"]:
            assert isinstance(term, list) and len(term) == 2 and all(str(x).strip() for x in term)
        for quiz in module["quiz"]:
            assert isinstance(quiz, list) and len(quiz) == 2 and all(str(x).strip() for x in quiz)

    shell = DAYS / data["file"]
    assert shell.exists(), shell
    text = shell.read_text(encoding="utf-8")
    for token in ("study_engine.css", "study_engine.js", f'data-day="{day:02d}"'):
        assert token in text, (shell, token)
    for obsolete in ("_pc.html", "_mobile.html", "data-layout", "_modules.js"):
        assert obsolete not in text, (shell, obsolete)


def validate_schedule(days: list[dict]) -> None:
    """Dates must be unique, ordered, and on weekdays (the plan is 평일 1시간)."""
    import datetime

    dates = [datetime.date.fromisoformat(d["date"]) for d in days]
    assert len(set(dates)) == len(dates), "duplicate study dates"
    assert dates == sorted(dates), "study dates are out of order"
    weekend = [d.isoformat() for d in dates if d.weekday() >= 5]
    assert not weekend, f"weekend study dates: {weekend}"


def validate_index() -> None:
    """The dashboard renders rows from JSON, so only its scaffolding is checked."""
    index = (PUBLIC / "index.html").read_text(encoding="utf-8")
    for marker in ('id="coreDays"', 'id="extDays"', 'id="pt"', 'id="bar"', 'id="extPt"', 'id="extBar"'):
        assert marker in index, f"missing dashboard element: {marker}"
    markup = index.split("<script>")[0]
    assert '<article class="day"' not in markup, (
        "day rows must come from days/data/*.json, not hardcoded HTML"
    )
    assert f"CORE_DAYS={CORE_DAYS}" in index
    assert f"EXTENSION_DAYS={EXTENSION_DAYS}" in index


def scan_public_content() -> None:
    for path in PUBLIC.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".css", ".md", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN:
            assert token not in text, f"{path}: forbidden stale term"
        for pattern in SUSPICIOUS:
            assert not pattern.search(text), f"{path}: suspicious internal identifier pattern"


def validate_no_orphans() -> None:
    """Every shell and data file should belong to a known day."""
    expected_shells = {f'day{d:02d}_{load_day(d)["date"]}.html' for d in TARGET_DAYS}
    actual_shells = {p.name for p in DAYS.glob("*.html")}
    assert actual_shells == expected_shells, f"orphan shells: {sorted(actual_shells ^ expected_shells)}"

    expected_data = {f"day{d:02d}.json" for d in TARGET_DAYS}
    actual_data = {p.name for p in DATA.glob("*.json")}
    assert actual_data == expected_data, f"orphan data: {sorted(actual_data ^ expected_data)}"

    stale = sorted(p.name for p in DAYS.glob("*_modules*.js"))
    assert not stale, f"legacy module files still present: {stale}"


def main() -> None:
    keys: list[str] = []
    days: list[dict] = []
    total_modules = 0
    for day in TARGET_DAYS:
        data = load_day(day)
        validate_day(day, data)
        keys.append(data["progressKey"])
        days.append(data)
        total_modules += len(data["modules"])
    assert len(keys) == len(set(keys)), "duplicate progress keys"
    assert (DAYS / "study_engine.css").exists()
    assert (DAYS / "study_engine.js").exists()
    validate_schedule(days)
    validate_index()
    validate_no_orphans()
    scan_public_content()
    print(
        f"Stanford study validation passed: {len(TARGET_DAYS)} days, "
        f"{total_modules} detailed modules, {len(TARGET_DAYS)} unified shells"
    )


if __name__ == "__main__":
    main()
