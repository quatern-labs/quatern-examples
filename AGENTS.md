# Working on quatern-examples

Instructions for anyone, person or coding agent, changing this repository.

## Layout

```
NN_concept/                 a step of the guided tour (01_getting_started ... 11_hardware_profile), plus misc/
  README.md                 the concept, and a table of its examples
  NN_example/
    README.md               what it shows, the commands, expected output, the run record, a docs link
    run.sh                  exactly the commands the README shows, run headlessly
    expected.txt            lines that must appear in the output (checked by CI)
    *.py, *.urdf            small helpers or inputs the example needs; stdlib only
internal/run_examples.py    runs examples and checks their output (CI uses it)
```

Every example is self-contained. It installs the robot it needs and doesn't
rely on any other example having run. The runner gives each one a fresh, empty
`QUATERN_DATA_DIR`.

## Run an example

```sh
python3 -m venv .venv && .venv/bin/pip install quatern   # or: pip install -e ../Quatern
export PATH="$PWD/.venv/bin:$PATH"

bash 01_getting_started/01_simulator_tour/run.sh          # one example, in your ~/.quatern
python internal/run_examples.py                           # every no-key example, each in a scratch data dir
python internal/run_examples.py 04_safety                 # only paths containing "04_safety"
python internal/run_examples.py --agent                   # agent examples too (needs a key in the environment)
python internal/run_examples.py --logs logs               # keep each example's full output
```

The examples are written for the Quatern version pinned in `pyproject.toml`.
Develop against that version, from PyPI or from a local checkout with
`pip install -e`. READMEs always tell readers `pipx install quatern`.

## Add an example

1. Pick the concept folder. If none fits, use `misc/`. Name the folder
   `NN_short_name`, numbered in the order a reader should take them.
2. Write `run.sh`. The first lines must be:
   ```bash
   #!/usr/bin/env bash
   # requires: none        # or: agent
   set -euo pipefail
   ```
   Use `requires: agent` if any command needs sign-in or an API key. Prefer one
   command. Use only real `quatern` commands and flags (check
   `quatern <command> --help`). Pass `--yes` so nothing waits for a terminal.
   When an example is *meant* to fail (a refused gate, an aborted run), assert
   that in the script: `if quatern deploy ...; then exit 1; fi`.
3. Run it, and copy the **real** output into the README. Never write expected
   output by hand.
4. Put the lines that prove the example worked in `expected.txt`, one per line.
   Choose stable lines (verdicts, states, labels), not ids, timestamps,
   timings or measured values.
5. Add a row to the concept folder's README table and, if it's a new concept,
   to the top-level README.
6. `python internal/run_examples.py <your folder>` must pass.

## README conventions

Each example README has, in this order:

1. A title, then a callout saying what it needs: **No key needed.** or
   **Needs sign-in (free) or an Anthropic key.**
2. **What it shows**: one paragraph.
3. **Run it**: the exact commands, one command where possible.
4. **Expected output**: real output, trimmed. Say "Trimmed." Cut machine
   paths (show `~/.quatern/...`), toolchain lines and progress noise. Keep the
   lines a reader needs to compare against. Don't edit the numbers.
5. **What to look for in the run record**: the receipt fields (or stack, or
   config) that show the result, with their real names.
6. **Docs**: links to the matching page at https://quatern.co/docs/, with an
   anchor that exists.

Write plainly. No personal names, usernames, emails or local paths anywhere.
That includes pasted output: `quatern whoami` prints the account name, so
replace it.

## Expected output going stale

When a Quatern release changes output, CI fails on the `expected.txt` lines.
Re-run the example, update the README's output block and `expected.txt`
together, and bump the pinned version in `pyproject.toml`.

Simulated deploys run at 5x real time and judge timing in sim time. On a
heavily loaded machine, the localizer can miss its 0.5 s deadline and a run
aborts with `stale:estimate`. Check machine load before deciding an example is
broken.

## Never commit API keys

- No API keys, Quatern tokens or `credentials` files, ever. Keys belong in
  your environment (`ANTHROPIC_API_KEY`, `QUATERN_API_KEY`) or in
  `~/.quatern/credentials` via `quatern login`, never in this repository.
- CI reads the key from the `QUATERN_API_KEY` repository secret only.
- The pre-commit hooks block `sk-ant-` keys, private keys and `credentials`
  files. Install them with `pre-commit install`.
- Don't commit `.quatern/` data directories, logs, or local agent tooling
  state (anything in `.claude/` except `settings.json` and `hooks/`);
  `.gitignore` covers them.

## Lint

```sh
pre-commit run --all-files     # or: ruff check . && ruff format --check .
```

## Coding agents

- READMEs show real output only, pasted from actual runs.
- Commit as `Quatern <hello@quatern.co>`, with no `Co-Authored-By` lines.
- No personal names, anywhere.
- Keep the quatern version pin consistent across all folders (`pyproject.toml`
  and any pin inside an example).
- Agent examples (`requires: agent`) need a key and aren't run by hooks.
- In Claude Code, a Stop hook (`.claude/hooks/stop_examples.py`) runs the
  no-key examples in folders changed since the last green run.
- A PreToolUse hook (`.claude/hooks/guard_harness.py`) blocks agent edits to
  `.claude/settings.json`, `hooks/`, `agents/` and `commands/`. To change
  them, start Claude Code with `QUATERN_ALLOW_HARNESS_EDIT=1`.
