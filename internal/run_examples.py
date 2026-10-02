"""Run every example headlessly and check its output.

An example is a directory holding a `run.sh`. Its first lines carry a header:

    # requires: none     runs with no sign-in and no key
    # requires: agent    needs `quatern login` (free) or an Anthropic key

Each example runs in a fresh, empty QUATERN_DATA_DIR, so examples never see
each other's robots or your own ~/.quatern. If the example has an
`expected.txt`, every non-blank, non-comment line in it must appear somewhere
in the combined stdout and stderr.

    python internal/run_examples.py                 # every no-key example
    python internal/run_examples.py --agent         # agent examples too
    python internal/run_examples.py 04_safety       # only paths matching

Agent examples are skipped unless --agent is given and QUATERN_API_KEY or
ANTHROPIC_API_KEY is set. Exit status is non-zero if any example failed.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRES = re.compile(r"^#\s*requires:\s*(none|agent)\s*$", re.MULTILINE)
KEY_VARS = ("QUATERN_API_KEY", "ANTHROPIC_API_KEY")


def discover(filters: list[str]) -> list[Path]:
    examples = sorted(p.parent for p in ROOT.glob("*/*/run.sh"))
    if filters:
        examples = [e for e in examples if any(f in str(e.relative_to(ROOT)) for f in filters)]
    return examples


def requirement(example: Path) -> str:
    match = REQUIRES.search((example / "run.sh").read_text())
    if match is None:
        raise SystemExit(f"{example.relative_to(ROOT)}/run.sh has no '# requires: none|agent' header")
    return match.group(1)


def expectations(example: Path) -> list[str]:
    path = example / "expected.txt"
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")]


def run(example: Path, timeout: int, logs: Path | None) -> tuple[bool, str]:
    env = dict(os.environ)
    with tempfile.TemporaryDirectory(prefix="quatern-example-") as data_dir:
        env["QUATERN_DATA_DIR"] = data_dir
        started = time.monotonic()
        try:
            proc = subprocess.run(
                ["bash", "run.sh"],
                cwd=example,
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output, code = proc.stdout + proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or b"").decode() + (exc.stderr or b"").decode()
            code = None
        elapsed = time.monotonic() - started
    if logs is not None:
        name = str(example.relative_to(ROOT)).replace("/", "__")
        (logs / f"{name}.log").write_text(output)
    if code is None:
        return False, f"timed out after {timeout}s"
    if code != 0:
        return False, f"exit {code} after {elapsed:.0f}s\n{_tail(output)}"
    missing = [line for line in expectations(example) if line not in output]
    if missing:
        return False, "missing from output:\n" + "\n".join(f"    {m}" for m in missing) + f"\n{_tail(output)}"
    return True, f"{elapsed:.0f}s"


def _tail(output: str, lines: int = 25) -> str:
    return "\n".join("    | " + line for line in output.splitlines()[-lines:])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("filters", nargs="*", help="Only run examples whose path contains one of these.")
    parser.add_argument("--agent", action="store_true", help="Also run examples that need sign-in or a key.")
    parser.add_argument("--timeout", type=int, default=900, help="Seconds per example.")
    parser.add_argument("--logs", type=Path, default=None, help="Write each example's full output here.")
    args = parser.parse_args()
    if args.logs is not None:
        args.logs.mkdir(parents=True, exist_ok=True)

    have_key = any(os.environ.get(var) for var in KEY_VARS)
    failed = 0
    for example in discover(args.filters):
        name = example.relative_to(ROOT)
        if requirement(example) == "agent" and not (args.agent and have_key):
            why = "pass --agent" if not args.agent else f"set {' or '.join(KEY_VARS)}"
            print(f"SKIP  {name}  (needs sign-in or a key; {why})", flush=True)
            continue
        ok, detail = run(example, args.timeout, args.logs)
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}", flush=True)
        failed += not ok
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
