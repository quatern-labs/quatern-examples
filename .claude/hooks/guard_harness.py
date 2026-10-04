"""Claude Code PreToolUse hook: keep the agent from editing its own harness.

Blocks Edit, Write and MultiEdit on .claude/settings.json,
.claude/settings.local.json, .claude/hooks/, .claude/agents/ and
.claude/commands/, and Bash commands that write to them
(sed -i, perl -i, redirects, tee, mv, cp, rm, truncate, python -c open(..., 'w'),
git checkout/restore). Set QUATERN_ALLOW_HARNESS_EDIT=1 in the environment
Claude Code runs in to allow it.

This catches honest mistakes, not a determined adversary.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]).resolve()
PROTECTED = re.compile(r"(^|/)\.claude(/(settings(\.local)?\.json|hooks|agents|commands)(/|$)|/?$)")
EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}
WRITERS = {"mv", "rm", "truncate", "tee", "install", "ln", "chmod"}
PY_WRITE = re.compile(r"open\([^)]*['\"][wax+]|write_text|write_bytes|unlink|rmtree|rename|replace\(")


def protected(path: str, cwd: Path = ROOT) -> bool:
    path = os.path.expanduser(path.strip("\"'"))
    if not path:
        return False
    full = Path(path) if os.path.isabs(path) else cwd / path
    try:
        rel = Path(os.path.normpath(full)).relative_to(ROOT).as_posix()
    except ValueError:
        return False
    return rel != "." and bool(PROTECTED.search(rel))


def segments(command: str) -> list[tuple[list[str], list[str]]]:
    """Split a shell command into simple commands: (argv, redirect targets)."""
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        tokens = command.replace("\n", " ; ").split()
    out, argv, targets, redirect = [], [], [], False
    for tok in tokens:
        if redirect:
            targets.append(tok)
            redirect = False
        elif tok and set(tok) <= set(";&|()"):
            out.append((argv, targets))
            argv, targets = [], []
        elif tok and set(tok) <= set("<>&|") and ">" in tok:
            redirect = True
        else:
            argv.append(tok)
    out.append((argv, targets))
    return out


def bash_writes_protected(command: str, cwd: Path) -> str | None:
    for argv, targets in segments(command):
        for target in targets:
            if protected(target, cwd):
                return f"redirect into {target}"
        while argv and (re.fullmatch(r"\w+=.*", argv[0]) or argv[0] in {"sudo", "env", "command"}):
            argv = argv[1:]
        if not argv:
            continue
        cmd, args = os.path.basename(argv[0]), argv[1:]
        if cmd == "cd":
            cwd = (cwd / os.path.expanduser(args[0])) if args else Path.home()
            continue
        if re.fullmatch(r"python[\d.]*", cmd) and "-c" in args:
            code = " ".join(args[args.index("-c") + 1 :])
            paths = [q for q in re.findall(r"['\"]([^'\"]+)['\"]", code) if protected(q, cwd)]
            if paths and PY_WRITE.search(code):
                return f"python -c writing {paths[0]}"
            continue
        hits = [a for a in args if protected(a, cwd)]
        if not hits:
            continue
        if cmd in WRITERS:
            return f"{cmd} on {hits[0]}"
        if cmd == "cp" and protected(args[-1], cwd):
            return f"cp onto {args[-1]}"
        if cmd in {"sed", "gsed"} and any(re.fullmatch(r"-[a-zA-Z]*i.*|--in-place.*", a) for a in args):
            return f"sed -i on {hits[0]}"
        if cmd == "perl" and any(re.fullmatch(r"-[a-zA-Z]*i.*", a) for a in args):
            return f"perl -i on {hits[0]}"
        if cmd == "git" and args and args[0] in {"checkout", "restore", "rm", "mv"}:
            return f"git {args[0]} on {hits[0]}"
    return None


def main() -> int:
    if os.environ.get("QUATERN_ALLOW_HARNESS_EDIT") == "1":
        return 0
    payload = json.loads(sys.stdin.read() or "{}")
    tool, tool_input = payload.get("tool_name"), payload.get("tool_input") or {}
    reason = None
    if tool in EDIT_TOOLS and protected(tool_input.get("file_path", "")):
        reason = f"{tool} on {tool_input['file_path']}"
    elif tool == "Bash":
        reason = bash_writes_protected(tool_input.get("command", ""), Path(payload.get("cwd") or ROOT))
    if reason is None:
        return 0
    print(
        f"Blocked: {reason}. The agent harness "
        "(.claude/settings.json, settings.local.json, hooks, agents, commands) is protected. "
        "Ask the user to make this change, or to restart Claude Code with QUATERN_ALLOW_HARNESS_EDIT=1.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
