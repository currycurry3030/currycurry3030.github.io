#!/usr/bin/env python3
"""초안 검수 요청 파이프라인.

에이전트가 초안 마크다운을 _posts/ 에 써 둔 뒤 이 스크립트를 호출한다.

    1. safety_scan.py 로 검사 → BLOCK/QUALITY 있으면 중단(발행 경로로 못 감)
    2. draft/<날짜>-<슬러그> 브랜치를 만들어 커밋·푸시
    3. 텔레그램으로 제목 + 요약 + diff 링크 + 승인 방법 발송
    4. next_topic 키를 사용 완료로 기록

승인은 사람만 한다. 이 스크립트는 절대 main 에 머지하지 않는다.

사용:
    python3 tools/blog/submit_draft.py _posts/2026-09-15-foo.md --topic-key day01 --series stanford
    python3 tools/blog/submit_draft.py ... --dry-run     # 푸시·발송 없이 검사만
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOG_DIR = Path(__file__).resolve().parent
SECRET_PATH = Path("/home/bjpark/.config/bjpark/secrets/telegram.env")
SETTINGS_PATH = Path("/home/bjpark/projects/finance-tracker/config/settings.yaml")
REPO_SLUG = "bjpark-lab/bjpark-lab.github.io"


def run(cmd: list[str], check: bool = True) -> str:
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} 실패:\n{r.stderr.strip()}")
    return r.stdout.strip()


def load_token() -> str:
    for line in SECRET_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            return line.partition("=")[2].strip().strip('"').strip("'")
    raise RuntimeError("telegram.env 에 TELEGRAM_BOT_TOKEN 이 없습니다")


def load_chat_id() -> str:
    import yaml
    return str(yaml.safe_load(SETTINGS_PATH.read_text(encoding="utf-8"))["telegram"]["chat_id"])


def send_telegram(text: str) -> None:
    import requests
    resp = requests.post(
        f"https://api.telegram.org/bot{load_token()}/sendMessage",
        json={"chat_id": load_chat_id(), "text": text, "disable_web_page_preview": True},
        timeout=20,
    )
    resp.raise_for_status()
    if not resp.json().get("ok"):
        raise RuntimeError(f"텔레그램 발송 실패: {resp.json()}")


def parse_post(path: Path) -> tuple[str, str, int]:
    """(제목, 첫 문단, 공백제외 글자수)"""
    import yaml
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    fm = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
    body = parts[2] if len(parts) >= 3 else text
    title = str((fm or {}).get("title", path.stem))
    paras = [p.strip() for p in body.strip().split("\n\n") if p.strip() and not p.startswith("#")]
    lead = paras[0] if paras else ""
    lead = re.sub(r"\s+", " ", lead)[:180]
    return title, lead, len(re.sub(r"\s", "", body))


def scan(path: Path) -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, str(BLOG_DIR / "safety_scan.py"), str(path)],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    return r.returncode == 0, r.stdout + r.stderr


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("post", help="초안 마크다운 경로")
    ap.add_argument("--topic-key", help="next_topic.py 의 키 (사용 완료 기록용)")
    ap.add_argument("--series", choices=["stanford", "agentops", "data"])
    ap.add_argument("--dry-run", action="store_true", help="검사만 하고 푸시·발송 안 함")
    args = ap.parse_args()

    post = Path(args.post)
    if not post.is_absolute():
        post = REPO_ROOT / post
    if not post.exists():
        print(f"초안 없음: {post}", file=sys.stderr)
        return 2

    ok, report = scan(post)
    print(report)
    if not ok:
        print("BLOCK/QUALITY 위반 — 검수 요청을 보내지 않습니다. 초안을 고치세요.", file=sys.stderr)
        return 1

    title, lead, nchars = parse_post(post)
    warns = [l.strip() for l in report.splitlines() if l.strip().startswith("WARN")]

    if args.dry_run:
        print(f"\n[dry-run] 통과. 제목={title} / {nchars}자 / WARN {len(warns)}건")
        return 0

    rel = post.relative_to(REPO_ROOT)
    branch = f"draft/{post.stem}"
    base = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])

    run(["git", "checkout", "-B", branch])
    run(["git", "add", str(rel)])
    status = run(["git", "status", "--porcelain", str(rel)])
    if status:
        run(["git", "commit", "-m", f"draft: {title}"])
    run(["git", "push", "-u", "origin", branch, "--force-with-lease"])
    run(["git", "checkout", base])

    compare = f"https://github.com/{REPO_SLUG}/compare/{base}...{branch}?expand=1"
    raw = f"https://github.com/{REPO_SLUG}/blob/{branch}/{rel}"

    lines = [
        "✍️ 블로그 초안 검수 요청",
        "",
        f"제목: {title}",
        f"분량: {nchars}자",
        f"시리즈: {args.series or '-'}",
        "",
        f"요약: {lead}",
        "",
        f"읽기: {raw}",
        f"PR열기: {compare}",
    ]
    if warns:
        lines += ["", f"⚠️ 확인 필요 {len(warns)}건:"] + [f"  {w}" for w in warns[:6]]
    lines += [
        "",
        "승인하시면 아래 중 하나:",
        f"  · GitHub에서 PR 열고 머지",
        f"  · 또는 저에게 '{post.stem} 승인' 이라고 말씀",
        "",
        "수정 요청도 그냥 말씀하시면 반영합니다.",
    ]
    send_telegram("\n".join(lines))
    print(f"\n검수 요청 발송 완료 → 브랜치 {branch}")

    if args.topic_key and args.series:
        subprocess.run(
            [sys.executable, str(BLOG_DIR / "next_topic.py"),
             "--series", args.series, "--mark-used", args.topic_key],
            cwd=str(REPO_ROOT), check=False,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
