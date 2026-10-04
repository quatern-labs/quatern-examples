---
name: refresh-example-output
description: Re-run examples after a Quatern release or development build alters their output, and update each README output block and expected.txt together from the real output.
---

# Refresh example output

Use when CI fails on `expected.txt` lines, or a Quatern change (a release or a
development build) alters what examples print. README rules:
`.claude/skills/readme-conventions.md`.

## Pin policy

First check whether the release pinned in `pyproject.toml` (0.3.0) is on
PyPI:

```sh
curl -s https://pypi.org/pypi/quatern/json | python3 -c "import json,sys; print(sorted(json.load(sys.stdin)['releases']))"
```

- **Until the release is on PyPI:** run against a local development install
  of quatern (`pip install -e <path-to-quatern-source>`). Leave the pin in
  `pyproject.toml` (`quatern==0.3.0`) alone. Record "development build" plus
  the quatern version string (`pip show quatern`) in each README you refresh
  and in the commit message. Never write source-repo commit SHAs into
  READMEs or commit messages; the source repo is private.
- **0.3.0 (or later) on PyPI:** run against a published release and bump
  the pin to it in `pyproject.toml` and in any pin inside an example
  (`grep -rn "quatern==" .`). Every refresh then requires a pin bump; a
  refresh that leaves the pin behind the version it ran against is not done.
  Record only the published version; replace the "development build" README
  lines as you refresh each one.

## Steps

1. **Fix the build.**
   - Development build: `pip install -e <path-to-quatern-source>` from a
     clean source tree (no local edits), then `pip show quatern` →
     `<version>`.
   - Release: `pip install quatern==<version>`.
   - Confirm the venv uses it: `pip show quatern` (version, and for a
     development build the location of your source tree) and `which quatern`
     points into `.venv`.

2. **Check load.** `uptime`. A loaded machine can abort simulated deploys
   (5x real time, judged in sim time) with `stale:estimate` when the
   localizer misses its 0.5 s deadline. Close load or re-run before calling
   an example broken.

3. **Run and keep logs.**
   ```sh
   python internal/run_examples.py --logs logs              # all no-key examples
   python internal/run_examples.py <path> --logs logs       # just the affected ones
   python internal/run_examples.py <path> --agent --logs logs   # agent examples, needs a key
   ```
   Agent examples need `QUATERN_API_KEY` or `ANTHROPIC_API_KEY` in the
   environment; the Stop hook never runs them. If no key is available, list
   them as not refreshed.

4. **For each example whose output changed**, from the **same run's** log
   (`logs/<concept>__<example>.log`):
   - Replace the README's output block(s). Trim by the conventions: keep the
     numbers as printed, `~/.quatern/...` for paths, replace the account
     name.
   - Set the line under "Trimmed." to the build:
     `Trimmed. From a run against a development build of quatern (\`<version>\`).`
     (development build only).
   - Update `expected.txt` from that same log. Keep lines stable (verdicts,
     states, labels); never add ids, recording names, timestamps or measured
     values.
   - Update the prose that explains the output (what each line means, which
     check passed, thresholds like "warn > 0.12, fail > 0.25"), and the
     "What to look for in the run record" field names if they changed.
   - If a verdict or label changed (`unverified` → `verified on recording`,
     a new outlier), update the concept README's prose and the top-level
     README row if it describes it.

5. **An example that now fails** because Quatern changed behaviour: fix
   `run.sh` to real current commands and flags (`quatern <cmd> --help`), or,
   if the case no longer reproduces, stop and ask whether to remove it.
   Don't weaken `expected.txt` just to make it pass.

6. **Re-run** the changed examples once more to confirm `expected.txt`
   passes against a second run (catches unstable lines).

## Files touched

- `NN_concept/NN_example/README.md` and `expected.txt` (always together)
- `NN_concept/README.md`, top-level `README.md` when a verdict changed
- `run.sh` only when a command or flag changed
- `pyproject.toml` (and any in-example pin) once the release is on PyPI

## Done when

- `python internal/run_examples.py <each refreshed path>` passes (agent ones
  with `--agent`, or reported as not run for lack of a key).
- `grep -rn "/Users/\|/home/\|/var/folders\|/tmp/" */*/README.md` finds no
  machine paths.
- Every README you touched has the build line (development build) or the pin matches the
  release you ran (PyPI): `grep -rn "quatern==" .` shows one version.
- `pre-commit run --all-files` passes.
- The commit message names the build, as every refresh did:
  "Output, expected.txt and the explanations are from new runs against a
  development build of quatern (0.3.0)", then one bullet per example on
  what changed. No source-repo commit SHAs.

## Gotchas from history

- `615c495`, `ddcd0dd`, `c640b75`, `a537eaf`: each followed a development-build change,
  2 to 15 examples, and each touched the explanations, not just the output.
  `a537eaf` changed the meaning of drift lines; the hallway and room READMEs
  had to say where the limits come from.
- An example can start passing *or* failing on a new build (`a537eaf`:
  `02_your_robot/01_from_urdf` failed before the change). Run them all, not
  just the ones CI flagged.
- Recording names include the run date, so they change every refresh; they
  belong in README output, never in `expected.txt`.
- Agent transcripts change wording every run; refresh them, but compare on
  the diff and labels.
- `logs/` is gitignored; don't force-add it.
