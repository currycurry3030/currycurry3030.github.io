from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "stanford-ai-study"
DAYS = PUBLIC / "days"
TARGET_DAYS = [d for d in range(1, 37) if d != 5]
EXTENSION_DAYS = range(31, 37)
REQUIRED_MODULE_KEYS = {"sourceLabel", "title", "core", "easy", "professor", "practical", "terms", "quiz"}
FORBIDDEN = ("Process RCA Agent", "process-rca-agent")
SUSPICIOUS = (
    re.compile(r"/home/[A-Za-z0-9_.-]+/"),
    re.compile(r"(?i)password\s*[=:]"),
    re.compile(r"(?i)api[_-]?key\s*[=:]"),
)


def load_day(day: int) -> dict:
    path = DAYS / f"day{day:02d}_modules.js"
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"\s*window\.STUDY_DAY\s*=\s*(\{.*\})\s*;?\s*", text, re.S)
    assert match, f"{path}: expected JSON-compatible window.STUDY_DAY assignment"
    return json.loads(match.group(1))


def validate_day(day: int, data: dict) -> None:
    assert data["day"] == day
    assert len(data["modules"]) >= 4
    assert data["progressKey"] == f"stanford-study-day{day:02d}-progress-v3"
    assert data["pcFile"].endswith("_pc.html")
    assert data["mobileFile"].endswith("_mobile.html")

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

    for mode in ("pc", "mobile"):
        shell = DAYS / f'day{day:02d}_{data["date"]}_{mode}.html'
        assert shell.exists(), shell
        text = shell.read_text(encoding="utf-8")
        for token in ("study_engine.css", f"day{day:02d}_modules.js", "study_engine.js"):
            assert token in text, (shell, token)
        assert f'data-layout="{mode}"' in text


def validate_extension_index() -> None:
    index = (PUBLIC / "index.html").read_text(encoding="utf-8")
    for day in EXTENSION_DAYS:
        data = load_day(day)
        assert f'data-day="{day}" data-extension="1"' in index, f"missing extension checkbox for day {day}"
        for mode in ("pc", "mobile"):
            link = f'days/day{day:02d}_{data["date"]}_{mode}.html'
            assert link in index, f"missing extension index link: {link}"
    assert 'id="extPt"' in index
    assert 'id="extBar"' in index


def scan_public_content() -> None:
    for path in PUBLIC.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".css", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN:
            assert token not in text, f"{path}: forbidden stale term"
        for pattern in SUSPICIOUS:
            assert not pattern.search(text), f"{path}: suspicious internal identifier pattern"


def validate_course_currency() -> None:
    index = (PUBLIC / "index.html").read_text(encoding="utf-8")
    for marker in (
        "CS329A · Spring 2027",
        "확장 수업 · 선택형 6일 · 최신 확인 학기",
        "CS146S · Fall 2026",
        "CS229 · Summer 2026",
        "CS234 · Winter 2026",
        "CS231N · Spring 2026",
        "CS25 · Spring 2026",
        "CS230 · 공개 사이트 2025 · 영상 Fall 2018",
    ):
        assert marker in index, f"missing course currency marker: {marker}"


def main() -> None:
    keys: list[str] = []
    total_modules = 0
    for day in TARGET_DAYS:
        data = load_day(day)
        validate_day(day, data)
        keys.append(data["progressKey"])
        total_modules += len(data["modules"])
    assert len(keys) == len(set(keys)), "duplicate progress keys"
    assert (DAYS / "study_engine.css").exists()
    assert (DAYS / "study_engine.js").exists()
    validate_course_currency()
    validate_extension_index()
    scan_public_content()
    print(
        f"Stanford study validation passed: {len(TARGET_DAYS)} engine days, "
        f"{total_modules} detailed modules, {len(TARGET_DAYS) * 2} shells"
    )


if __name__ == "__main__":
    main()
