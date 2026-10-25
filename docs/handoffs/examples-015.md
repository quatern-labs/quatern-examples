# examples-015 (was examples-011): CI no longer skips green on a missing pin (issue #2)

Base sha: 82cd634.

## What changed
- `internal/check_pin.py`: reads the `quatern==` pin, checks PyPI, exits 1 with a `::error` if absent.
- `examples.yml`: the examples job runs it, then installs `quatern==<pin>` (was `pip install --upgrade quatern`, i.e. latest, which could differ from the pin); every `available == 'true'` guard is gone, so a missing pin fails the job. Lint job also runs the new unit tests.
- README: "continuously tested against the latest release" replaced with what CI does (pin, Python 3.11, push/PR/weekly, agent examples only with `QUATERN_API_KEY`, not on fork PRs).
- `.github/labels.md` documents the `broken-example` label the issue form applies.
- `tests/test_ci_pin.py` (9 tests, stdlib unittest): `python -m unittest discover -s tests`.

## Evidence
- Fail-without (measured): tests copied into a `git archive` of 82cd634 -> `ModuleNotFoundError: No module named 'check_pin'`, FAILED (errors=1). (Workflow/README assertions would also fail there; the import error hides them.)
- On the branch (measured): 9 tests OK; ruff check and format clean.
- Not measured: the real workflow run on GitHub; PyPI lookup in `check_pin.main()` (no network test). Fork PRs lacking secrets is inferred from GitHub docs.

## OWNER STEPS
- Create the `broken-example` label in GitHub (Issues > Labels); needs repo access, not done here. GitHub does not create it from the form.
- Until quatern 0.3.0 is on PyPI this CI will be red by design: keep the PR unmerged until then.
- `tomllib` needs Python 3.11+, but pyproject says `>=3.10`; check_pin.py only runs in CI (3.11). Consider raising `requires-python` (not changed).

## Retry note (examples-015, base 82cd634)
The earlier gate failed only because the repo had no `make test` target. This branch adds a `Makefile` (`test`, `test-fast` -> `python3 -m unittest discover -s tests`); `make test` passes (measured, 9 tests). If `examples-test-target` lands first with a different Makefile, drop this one on rebase.
