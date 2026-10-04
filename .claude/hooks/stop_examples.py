"""Claude Code Stop hook: re-run the no-key examples whose folders changed.

A folder counts as changed when its content (tracked and untracked files,
minus gitignored ones) differs from the last green run recorded in
.claude/.last-green, or from HEAD if it has never gone green. Agent examples
are skipped by the runner, since they need a key.

Exits 2 with the runner's output when an example fails, so the agent keeps
working. Skips when nothing changed or the turn ended with a question, and
lets the turn end after 3 consecutive blocks.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
LAST_GREEN = ROOT / ".claude" / ".last-green"
BLOCKS = ROOT / ".claude" / ".stop-blocks"
MAX_BLOCKS = 3


def git(*args: str, env: dict | None = None) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, env=env, capture_output=True, text=True).stdout.strip()


def folder_hashes() -> dict[str, str]:
    """Tree hash of every example folder in the working tree."""
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        git("add", "-A", ".", env=env)
        tree = git("write-tree", env=env)
    folders = sorted(str(p.parent.relative_to(ROOT)) for p in ROOT.glob("*/*/run.sh"))
    return {f: git("rev-parse", f"{tree}:{f}") for f in folders}


def baseline(folder: str, recorded: dict[str, str]) -> str:
    return recorded.get(folder) or git("rev-parse", "--verify", "-q", f"HEAD:{folder}")


def last_message(payload: dict) -> str:
    if payload.get("last_assistant_message"):
        return payload["last_assistant_message"]
    try:
        lines = Path(payload["transcript_path"]).read_text().splitlines()
    except (KeyError, OSError):
        return ""
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content", [])
        text = "".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
        if text.strip():
            return text
    return ""


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    if last_message(payload).rstrip().rstrip("`*_ ").endswith("?"):
        return 0

    blocks = int(BLOCKS.read_text()) if payload.get("stop_hook_active") and BLOCKS.exists() else 0

    recorded = {}
    if LAST_GREEN.exists():
        recorded = dict(line.split(maxsplit=1)[::-1] for line in LAST_GREEN.read_text().splitlines() if line.strip())
    current = folder_hashes()
    changed = [f for f, h in current.items() if h != baseline(f, recorded)]
    if not changed:
        BLOCKS.unlink(missing_ok=True)
        return 0

    venv = ROOT / ".venv" / "bin"
    env = {**os.environ, "PATH": f"{venv}{os.pathsep}{os.environ['PATH']}"} if venv.is_dir() else None
    proc = subprocess.run(
        [sys.executable, "internal/run_examples.py", *changed],
        cwd=ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        recorded.update({f: current[f] for f in changed})
        LAST_GREEN.write_text("".join(f"{recorded[f]} {f}\n" for f in sorted(recorded) if f in current))
        BLOCKS.unlink(missing_ok=True)
        return 0

    blocks += 1
    if blocks > MAX_BLOCKS:
        BLOCKS.unlink(missing_ok=True)
        print(json.dumps({"systemMessage": f"Examples still failing after {MAX_BLOCKS} retries; stopping."}))
        return 0
    BLOCKS.write_text(str(blocks))
    print(
        f"Examples failed in changed folders ({blocks}/{MAX_BLOCKS}). Fix them, or re-run real output into "
        f"README and expected.txt if the output legitimately changed.\n{proc.stdout}{proc.stderr}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
