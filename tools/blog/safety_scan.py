#!/usr/bin/env python3
"""공개 글 초안 안전 스캐너.

tools/blog/policy.yml 의 규칙으로 마크다운 초안을 검사한다.

  BLOCK : 회사 기밀, 개인 금융, 자격증명 등 — 발행 차단
  WARN  : 검수자가 눈으로 확인해야 하는 항목
  QUALITY: 분량, frontmatter, 소제목, 면책 문구

사용:
    python3 tools/blog/safety_scan.py _posts/2026-09-15-foo.md
    python3 tools/blog/safety_scan.py --all
    python3 tools/blog/safety_scan.py --json draft.md

종료 코드: 0 = 통과(WARN 있어도 0), 1 = BLOCK/QUALITY 실패, 2 = 사용 오류
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = Path(__file__).resolve().parent / "policy.yml"

# 코드블록/인라인코드 안의 예시는 오탐이 많아 검사 대상에서 뺀다.
FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


@dataclass
class Finding:
    level: str          # BLOCK | WARN | QUALITY
    reason: str
    line: int
    excerpt: str


def load_policy() -> dict:
    import yaml
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


def split_frontmatter(text: str) -> tuple[dict, str, int]:
    """(frontmatter dict, body, body가 시작하는 줄번호) 반환."""
    import yaml
    if not text.startswith("---"):
        return {}, text, 1
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text, 1
    fm_raw, body = parts[1], parts[2]
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError:
        fm = {}
    offset = fm_raw.count("\n") + 2
    return fm, body, offset


def mask_code(body: str) -> str:
    """코드블록/인라인코드를 같은 줄 수의 공백으로 치환해 줄번호를 보존한다."""
    def blank(m: re.Match) -> str:
        return "\n" * m.group(0).count("\n")
    masked = FENCE_RE.sub(blank, body)
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), masked)


def scan_patterns(body: str, rules: list[dict] | None, level: str, line_offset: int) -> list[Finding]:
    findings: list[Finding] = []
    target = mask_code(body)
    for rule in rules or []:
        regex = re.compile(rule["pattern"])
        for m in regex.finditer(target):
            line_no = target[: m.start()].count("\n") + line_offset
            start = max(0, m.start() - 30)
            excerpt = target[start : m.end() + 30].replace("\n", " ").strip()
            findings.append(Finding(level, rule["reason"], line_no, excerpt))
    return findings


def check_quality(fm: dict, body: str, q: dict) -> list[Finding]:
    findings: list[Finding] = []
    text = body.strip()

    n = len(re.sub(r"\s", "", text))
    if n < q["min_chars"]:
        findings.append(Finding("QUALITY", f"본문이 너무 짧음 ({n}자 < {q['min_chars']}자)", 1, ""))
    if n > q["max_chars"]:
        findings.append(Finding("QUALITY", f"본문이 너무 김 ({n}자 > {q['max_chars']}자)", 1, ""))

    for key in q["require_frontmatter"]:
        if key not in fm or fm[key] in (None, "", []):
            findings.append(Finding("QUALITY", f"frontmatter 누락: {key}", 1, ""))

    headings = len(re.findall(r"^##+ ", body, re.MULTILINE))
    if headings < q["min_headings"]:
        findings.append(Finding("QUALITY", f"소제목 부족 ({headings}개 < {q['min_headings']}개)", 1, ""))

    cats = fm.get("categories") or []
    if isinstance(cats, str):
        cats = [cats]
    needs = {c.lower() for c in q["require_disclaimer_categories"]}
    if {str(c).lower() for c in cats} & needs:
        if q["disclaimer_text"] not in body:
            findings.append(Finding("QUALITY", "금융 카테고리인데 면책 문구 없음", 1, q["disclaimer_text"]))

    return findings


def scan_file(path: Path, policy: dict) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    fm, body, offset = split_frontmatter(text)
    findings: list[Finding] = []
    findings += scan_patterns(body, policy.get("blocked_patterns"), "BLOCK", offset)
    findings += scan_patterns(body, policy.get("warn_patterns"), "WARN", offset)
    findings += check_quality(fm, body, policy["quality"])
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", help="검사할 마크다운 파일")
    ap.add_argument("--all", action="store_true", help="_posts 전체 검사")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    args = ap.parse_args()

    targets: list[Path] = [Path(p) for p in args.paths]
    if args.all:
        targets += sorted((REPO_ROOT / "_posts").glob("*.md"))
    if not targets:
        ap.print_usage()
        return 2

    policy = load_policy()
    report: dict[str, list[dict]] = {}
    failed = False

    for path in targets:
        if not path.exists():
            print(f"파일 없음: {path}", file=sys.stderr)
            return 2
        findings = scan_file(path, policy)
        report[str(path)] = [asdict(f) for f in findings]
        if any(f.level in ("BLOCK", "QUALITY") for f in findings):
            failed = True

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for path, findings in report.items():
            blocks = [f for f in findings if f["level"] == "BLOCK"]
            quals = [f for f in findings if f["level"] == "QUALITY"]
            warns = [f for f in findings if f["level"] == "WARN"]
            status = "차단" if blocks or quals else ("확인필요" if warns else "통과")
            print(f"\n[{status}] {path}")
            for f in blocks + quals + warns:
                loc = f"L{f['line']}" if f["line"] else "-"
                print(f"  {f['level']:<7} {loc:<6} {f['reason']}")
                if f["excerpt"]:
                    print(f"          … {f['excerpt'][:100]}")
        print()

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
