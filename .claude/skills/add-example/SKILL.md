---
name: add-example
description: Add a new quatern-examples example or concept folder (NN_concept/NN_example) with run.sh, expected.txt, a README taken from a real run, and the index rows. Also covers renumbering or removing examples in a concept.
---

# Add an example

For a `07_debugging` case, use `diagnose-case-study`, which builds on this.
README rules: `.claude/skills/readme-conventions.md`.

## Steps

1. **Pick the folder.** Use the concept that fits (`01_getting_started` ...
   `11_hardware_profile`), else `misc/`. Name it `NN_short_name`, numbered in
   the order a reader should take them. For a new concept, use the next
   `NN_concept` number.

2. **Check the commands exist** in the Quatern build you develop against
   (see "Which Quatern" below): `quatern <command> --help` for every command
   and flag you use. Only real commands and flags.

3. **Write `run.sh`.** The first lines must be exactly:
   ```bash
   #!/usr/bin/env bash
   # requires: none        # or: agent
   set -euo pipefail
   ```
   A comment block saying what the example shows may sit between `# requires:`
   and `set -euo pipefail` (every existing script does this). Then:
   - `requires: agent` if any command needs sign-in or an API key.
   - Install the robot the example needs (`quatern init --robot ... --no-sample
     --yes`, `quatern capture ... --yes`). The runner gives each example a
     fresh, empty `QUATERN_DATA_DIR`; never rely on another example.
   - Prefer one command. Pass `--yes` so nothing waits for a terminal.
   - A failure the example *means* to show is asserted:
     `if quatern deploy ...; then exit 1; fi`. Note which commands exit 1 on
     success-of-the-check (`diagnose` and `bringup` exit 1 while a cause
     remains, `--write` included; `profile check` exits 1 while refused).
   - If anything writes files (`--write`, `firmware build --out`), work on a
     copy so the repo never changes:
     ```bash
     work=$(mktemp -d)
     trap 'rm -rf "$work"' EXIT
     cp input.yaml other.log "$work"
     cd "$work"
     ```
     Otherwise `cd "$(dirname "$0")"` so local inputs resolve.
   - Files from the data dir go through
     `"${QUATERN_DATA_DIR:-$HOME/.quatern}"`, never a fixed path.
   - Agent commands: pipe through `tee agent.out` and fail on
     `usage for this month is used up` (the agent exits 0 when usage runs out).

4. **Helpers and inputs** (`*.py`, `*.urdf`, `*.yaml`, logs) live next to
   `run.sh`. Python is stdlib only and passes `ruff check` / `ruff format`.
   Hand-written inputs say so at the top of the README.

5. **Run it** and keep the log:
   ```sh
   python internal/run_examples.py <NN_concept/NN_example> --logs logs
   ```
   (`--agent` too for agent examples; needs a key in the environment.)
   Copy the **real** output from `logs/<concept>__<example>.log` into the
   README. Never write expected output by hand.

6. **Write `expected.txt`**: lines that prove it worked, one per line. Stable
   ones only: verdicts, states, cause labels, labels like
   `verified on recording`, diff lines (`+    scan_topic: /tb3_1/scan`).
   No ids, recording names (they carry the date: `..._2026-10-03_room_v1`),
   timestamps, timings, measured values or paths. Each line must appear
   verbatim (substring) in combined stdout+stderr.

7. **Write the README** per `readme-conventions.md`.

8. **Index rows.**
   - Add a row to the concept README table: `| [\`NN_name\`](NN_name/) | what it shows | Needs |`.
   - New concept: write its `README.md` (concept paragraph + table), add a
     row to the top-level `README.md` tour table, and extend the range in
     the AGENTS.md layout line (`01_getting_started ... NN_last`), as
     `fe4351f` did.
   - If the concept's summary in the top-level table lists cases (07 does),
     update it.

9. **Verify and commit** (see "Done when").

## Renumbering or removing examples

As in `d354898`:
- `git mv` the folders so history follows.
- Fix every cross-reference: the concept README table and prose (for
  example "as in `02`"), the top-level README row, other examples' READMEs
  (`grep -rn "NN_old_name" .`), and `run.sh` comments.
- Re-run every renumbered example; folder names can appear in output.

## Which Quatern

Same policy as `refresh-example-output`: until the release is on PyPI, run
against a local development install of quatern
(`pip install -e <path-to-quatern-source>`), and record "development build"
plus the version from `pip show quatern` in the README ("Trimmed. From a run
against a development build of quatern (`0.3.0`).") and the commit message.
Never write source-repo commit SHAs. Once the release is published, run
against it and record only the published version, or bump the pin
everywhere if the example needs newer.

## Files touched

- `NN_concept/NN_example/{run.sh,expected.txt,README.md}` and any inputs
- `NN_concept/README.md` (table row, prose that names cases)
- `README.md` (new concept, or a concept summary that lists cases)
- `AGENTS.md` layout line (only when the concept range grows)

## Done when

- `python internal/run_examples.py <NN_concept/NN_example>` passes (for
  agent examples, with `--agent` and a key; say so in the report if no key
  was available and it was not run).
- `bash -n run.sh` is clean and `run.sh` starts with the exact header.
- `git status` shows no changed repo inputs after the run (the copy worked)
  and no `logs/`, `.quatern/` or credentials staged.
- `pre-commit run --all-files` passes.
- `grep -rn` for the old name finds nothing after a renumber.
- The commit message lists each example with what it shows and the Quatern
  build it ran against, e.g. "real output from runs against a development
  build of quatern (0.3.0)", or the published version after release.

## Gotchas from history

- The Stop hook runs only no-key examples; agent examples are your job to run.
- A loaded machine can abort a simulated deploy with `stale:estimate`
  (localizer misses its 0.5 s sim-time deadline). Check load before calling
  an example broken.
- Runner paths look like `/var/folders/.../quatern-example-XXXX/`; rewrite
  to `~/.quatern/...` in the README.
- `quatern whoami` and sign-in banners print the account name; replace it.
- A case Quatern stops reproducing (it turns into a Quatern regression test)
  is removed, not left failing (`d354898`).
