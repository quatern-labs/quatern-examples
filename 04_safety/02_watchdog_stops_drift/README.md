# The watchdog stops a drifting run

> **No key needed.**

A stack is verified on a healthy simulated `sim_diffbot`. Then the *same*
stack is deployed on a second simulator target, `sim_drift`, whose wheel
odometry is 45% wrong. The gate has no reason to refuse, because the stack is
ready. So the robot moves, falls behind its plan, and the **watchdog** (a
separate process attached to the same robot) stops it. The run ends
`ABORTED`, and the receipt says which check fired, when, and how far the robot
went after the stop. [`sim_target.py`](sim_target.py) adds the target, and
[`read_receipt.py`](read_receipt.py) prints the parts of the receipt that
explain the abort.

## Run it

```sh
quatern init --robot sim_diffbot --no-sample --yes
quatern capture --robot sim_diffbot --seconds 120 --label room --yes
quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"
python3 sim_target.py sim_diffbot sim_drift '{"drift": {"wheel_odom": 0.45}}'
quatern deploy --robot sim_diffbot --stack <stack id from verify> --target sim_drift --yes
python3 read_receipt.py sim_diffbot
```

`deploy` exits non-zero because the run didn't complete. `./run.sh` checks for
that.

## Expected output

Trimmed. The gate is as in [`01_the_gate`](../01_the_gate/), with `target:
sim_drift (sim2d, not hardware)`. Which deviation trips first (`base` in
metres or `base/rad` in radians) varies from run to run.

```text
gate confirmed; deploying...
  t=  0.0s  deviation base 0.104
  t=  1.0s  deviation base/rad 0.563
  t=  2.1s  deviation base/rad 0.460
  t=  3.4s  deviation base 0.753
RECEIPT rcpt_sim_diffbot.default_20261002T063434759729: ABORTED (STOP_OBSERVED)
  e-stop: not declared (software stop layers only)
  abort: deviation_state:base — the robot reports base 0.585 from the plan (limit 0.500)
  stop: observed 0.25s after the stop request, travel after stop 0.222 (by watchdog)
  max deviation base: 0.753
  max deviation base/rad: 0.676
```

`read_receipt.py`:

```text
receipt:        rcpt_sim_diffbot.default_20261002T063434759729
target:         sim_drift (hardware: False, evidence: SIMULATION)
final_state:    ABORTED
acknowledgement: STOP_OBSERVED
transitions:
  REQUEST_ACCEPTED     preconditions passed
  COMMAND_DISPATCHED   first command sent
  EFFECT_OBSERVED      base/x responded 0.050s after the first command
  STOP_OBSERVED        stop observed by watchdog 0.25s after the stop
  ABORTED              deviation_state:base
abort:
  check:      deviation_state
  reason:     deviation_state:base
  detail:     the robot reports base 0.585 from the plan (limit 0.500)
  stopped_by: watchdog
stop:
  observed: True after 0.247s, travel after stop 0.2219 m
  bounded travel promised at the gate: 0.4 m worst case
deviation_max:  {"base": 0.7531, "base/rad": 0.6762}
live_checks.fired: deviation_state at t=4.163s
```

## Reading an ABORTED run record

The receipt is at
`~/.quatern/receipts/sim_diffbot.default/<stack id>/rcpt_*.json`. It's
write-once and plain JSON.

- **`final_state`**: `COMPLETED` needs the goal reached *and* the stop
  observed. `ABORTED` means a check stopped the run. A stop that was requested
  but never seen is `UNKNOWN`: nothing confirmed the robot stopped.
- **`acknowledgement: STOP_OBSERVED`**: the stop was confirmed from the
  robot's state, not just sent.
- **`transitions`**: the run's timeline. Here the effect of the first command
  was seen 0.05 s after dispatch, and the stop 0.25 s after it was requested.
- **`abort`**: which watchdog check fired (`check`), the machine-readable
  `reason`, a human `detail`, and `stopped_by`. `deviation_state` means the
  robot's *own* reported state left the plan. `deviation` (no suffix) means
  the localizer's estimate did. Other reasons include `stale:<source>`,
  `limit:<dof>`, `residual:<source>` and `sandbox:<why>`.
- **`stop.travel_after_stop`** vs **`bounded_travel.stopping_distance`**: how
  far the robot actually went after the stop, against the worst case the gate
  promised. Check this one on every abort.
- **`live_checks`**: the evidence behind the abort. `fired` is the check and
  its sim time. `series` holds the time series, and `warnings` holds anything
  that came close without aborting.

## Docs

[quatern.co/docs/safety](https://quatern.co/docs/safety/#the-watchdog): the watchdog, [how a run stops](https://quatern.co/docs/safety/#how-a-run-stops), [run records](https://quatern.co/docs/safety/#run-records)
