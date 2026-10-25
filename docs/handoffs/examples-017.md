# examples-017: CI fails on a missing pin (issue #2), attempt 3

Base sha: 82cd634 (origin/main). Content is identical to examples-015 (see docs/handoffs/examples-015.md for what changed, fail-without evidence and OWNER STEPS).

## Why attempt 3
- The try2 push was refused: "FAILED claims checker: -1 mismatch(es)". The claims report (reports/claims/2026-10-25-142709-quatern-examples.md) says only "Not logged in · Please run /login" (measured): the checker agent errored on auth, it did not find a mismatch. All other gate checks, including the security reviewer, passed.
- No code change made; this branch is try2 fast-forwarded plus this note. Nothing was weakened or skipped.
- Re-run on branch (measured): `make test` -> 9 tests OK.

## OWNER STEPS
- Claims checker login on the coordinator needs refreshing (`/login`) before the push can pass; I can't do it from the lane.
- Create the `broken-example` label in GitHub; keep the PR unmerged until quatern 0.3.0 is on PyPI.
