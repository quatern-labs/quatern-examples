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
.claude/skills/             procedures for adding and refreshing examples
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
`pip install -e`. Until it is on PyPI, develop against Quatern main and
record its commit (see `refresh-example-output`). READMEs always tell readers `pipx install quatern`.

## Procedures

Step-by-step procedures live in `.claude/skills/`, as Claude Code skills that
people can read too:

- `add-example`: add, renumber or remove an example or concept folder
  (`run.sh` header, `expected.txt`, README from a real run, index rows).
- `refresh-example-output`: re-run examples after Quatern's output changes,
  update README output and `expected.txt` together, and the pin policy.
- `diagnose-case-study`: add or update a `07_debugging` case.
- `readme-conventions.md`: the example README sections and trimming rules.

In short: every example README has a title and a key callout, **What it
shows**, **Run it**, **Expected output** (real, trimmed, numbers unedited,
paths shown as `~/.quatern/...`), **What to look for in the run record**,
and **Docs**. Write plainly. No personal names, usernames, emails or local
paths anywhere, including pasted output (`quatern whoami` prints the account
name, so replace it). `python internal/run_examples.py <folder>` must pass.

## Never commit API keys

- No API keys, Quatern tokens or `credentials` files, ever. Keys belong in
  your environment (`ANTHROPIC_API_KEY`, `QUATERN_API_KEY`) or in
  `~/.quatern/credentials` via `quatern login`, never in this repository.
- CI reads the key from the `QUATERN_API_KEY` repository secret only.
- The pre-commit hooks block `sk-ant-` keys, private keys and `credentials`
  files. Install them with `pre-commit install`.
- Don't commit `.quatern/` data directories, logs, or local agent tooling
  state (anything in `.claude/` except `settings.json`, `hooks/` and
  `skills/`);
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
  `.claude/settings.json`, `settings.local.json`, `hooks/`, `agents/` and
  `commands/`. To change them, start Claude Code with `QUATERN_ALLOW_HARNESS_EDIT=1`.
