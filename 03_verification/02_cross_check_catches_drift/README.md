# A cross-check catches a drifting sensor

> **No key needed.**

The same capture-and-verify as [`01_capture_and_verify`](../01_capture_and_verify/),
except the simulator gives `sim_diffbot`'s wheel odometry a 45% distance and
heading error. The fault goes in through the simulator target's `drift`
option, which [`sim_target.py`](sim_target.py) sets in the robot's
`.quatern.json`. Every stream still looks healthy on its own (right rate, no
dropouts), so only comparing wheel odometry with visual odometry reveals the
problem. Verification retries with a fresh capture, still sees the
disagreement, and refuses to call the stack ready.

## Run it

```sh
quatern init --robot sim_diffbot --no-sample --yes
python3 sim_target.py sim_diffbot sim '{"drift": {"wheel_odom": 0.45}}'
quatern capture --robot sim_diffbot --seconds 120 --label room --yes
quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"
```

`verify` exits non-zero here, and that's the expected result. `./run.sh`
checks for it.

To undo the fault, remove `"drift"` from the `sim` target in
`~/.quatern/robots/sim_diffbot.quatern.json`, or run
`quatern init --robot sim_diffbot --force --yes`.

## Expected output

Trimmed.

```text
sim_diffbot.quatern.json: target 'sim' options {"drift": {"wheel_odom": 0.45}, ...}
recorded sim_diffbot.default_2026-10-02_room_v1 (120.0 s)
  stream       verdict  health
  wheel_odom   ok       49.8 Hz, dropout 0%, noise 0.0040
  visual_odom  ok       29.4 Hz, dropout 2%, noise 0.0100
Verification of sim_diffbot.default — goal: Navigate around the island to reach (1.2, 2.0)
  capture: sim_diffbot.default_2026-10-02_sensor_recheck_v3
  localization (mapping mode), 3 iteration(s):
    base:wheel_odom vs visual_odom  116.1%  FAIL  over the 30% critical limit
    drift at end: 3.232 (FAIL; warn > 0.25, critical > 1.0)
    loop closures: 4, mean error 2.291
    (critical) drift: Trajectory drifted 3.23 by the end of the run, over the 1.00 critical threshold
  plan: not attempted (localization did not pass)
  next: recapture — wheel_odom and visual_odom disagree by 116% on base, over the 30% critical threshold: re-weighting alone will not recover it. The disagreeing sources cannot be told apart with the sources available. Inspect the capture for wheel_odom vs visual_odom, and recapture if the disagreement persists.
  verdict: NOT READY
    - localization health is 'fail': Localization failed verification: wheel_odom and visual_odom disagree by 116% on base, over the 30% critical threshold (+2 more critical) (base: 1 of 1 pairs disagree across wheel_odom and visual_odom).
    - no motion plan on record
```

## Reading the report

- Both streams pass their health check (`ok`, right rate). Stream health can't
  see this fault, but the cross-check can: 116% disagreement against a 30%
  critical line.
- `3 iteration(s)` and the capture id `..._sensor_recheck_v3`: verification
  recaptured to rule out a one-off before giving up. It doesn't loop forever
  (`thresholds.max_offline_iterations`).
- *"The disagreeing sources cannot be told apart"*: with only two sources,
  Quatern knows they disagree but not which one is wrong. A third source on the
  same channel would let it name the outlier.
- No plan is attempted on a localization that failed, so a stack like this one
  can never reach the gate.

## Docs

[quatern.co/docs/verification](https://quatern.co/docs/verification/#cross-checks): cross-checks
