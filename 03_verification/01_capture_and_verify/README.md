# Record a capture and verify against it

> **No key needed.**

`quatern capture` records a sensor session. In the simulator, an operator
drives the world's loop and stops where it started, and Quatern only records:
it never commands motion during a capture. `quatern verify` then runs the
localizer and planner modules in the sandbox against that recording and writes
a report in plain English. This example uses `sim_diffbot` because it has
**four** sources on its base. Wheel odometry and visual odometry estimate it,
and the lidar (through a scan-to-map matcher) and the IMU (heading only) check
it. Every pair is cross-checked, which is the signal that catches a sensor
that's quietly wrong.

## Run it

```sh
quatern init --robot sim_diffbot --no-sample --yes
quatern capture --robot sim_diffbot --seconds 120 --label room --yes
quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"
```

`--label` names the scenario. `verify --label room` reuses the newest capture
with that label rather than recording a new one (`--no-reuse` forces a fresh
one). `verify` exits non-zero when the verdict isn't READY.

## Expected output

Trimmed.

```text
recorded sim_diffbot.default_2026-10-03_room_v1 (120.0 s)
  stream       verdict  health
  wheel_odom   ok       49.8 Hz, dropout 0%, noise 0.0040
  visual_odom  ok       29.4 Hz, dropout 2%, noise 0.0100
  imu          ok       99.8 Hz, dropout 0%, noise 0.0040
  scan         ok       10.0 Hz, dropout 0%, noise 0.0100
  depth_cloud  ok       6.0 Hz, dropout 0%, noise 0.0045
Verification of sim_diffbot.default — goal: Navigate around the island to reach (1.2, 2.0)
  localizer: python module, build none, run `python3 node.py`, sandbox tier none
  calibration: fresh (0 min old, cal_sim_diffbot.default_20261003T075451396541)
  capture: sim_diffbot.default_2026-10-03_room_v1
  localization (mapping mode), 1 iteration(s):
    base:wheel_odom vs visual_odom  10.9%  pass  under 15%
    base:wheel_odom vs imu          2.5%   pass  under 15%
    base:wheel_odom vs scan         7.9%   pass  under 15%
    base:visual_odom vs imu         2.4%   pass  under 15%
    base:visual_odom vs scan        6.4%   pass  under 15%
    base:imu vs scan                4.0%   pass  under 15%
    drift at end: 0.083 (pass; 0.08 is 17% of the 0.50 deploy abort limit (warn > 0.12, fail > 0.25))
    loop closures: 150, mean error 0.313
    performance (HOST): 452 Hz sustainable vs 19 Hz input, CPU 49%, sandbox tier none — keeps up
    (warning) loop_closure: Mean loop closure error is 0.31 across 150 closures
  plan: 36 waypoints over 2.57 in grid2d, 9.7 s, no violations
  verdict: READY for the deploy gate (the code executed in the sandbox against the recorded stream)
  stack: stk_sim_diffbot.default_20261003T075503896778 (pin it with `quatern pin stk_sim_diffbot.default_20261003T075503896778`)
```

## Reading the report

- **Cross-check.** `base:wheel_odom vs visual_odom  10.9%  pass  under 15%`
  reads as: on the `base` channel, these two sources disagreed by 10.9% of the
  distance travelled, over time-aligned windows, and the warning line is 15%.
  The critical line is 30% (`thresholds.cross_check_defaults` in
  `~/.quatern/config.json`). With four sources there are six pairs. When the
  pairs with one source disagree and the pairs without it agree, that source
  is named as the outlier.
  [02_cross_check_catches_drift](../02_cross_check_catches_drift/) shows it.
- **Drift at end.** The capture ends where it started, so any distance between
  the estimated start and end is error. The lines are set from the deploy abort
  limit (0.50 m on a planar base): warn above 0.12, fail above 0.25. A map that
  far off would start a deploy close to its abort. 0.083 passes.
- **Warnings don't block.** The loop-closure warning is recorded with the stack
  and shown again at the gate, but the verdict is still READY.
- **What READY means.** The code ran in the sandbox against this recording,
  every critical signal passed, and the plan reached the goal with no
  violations. It doesn't mean the robot has moved. That's the gate's job.
  See [04_safety](../../04_safety/).

## What to look for in the run record

There's no receipt yet, since nothing has been deployed. Verification writes a
**stack** instead: `~/.quatern/stacks/sim_diffbot/stk_*.json`, with the
verdict, the capture it was verified against, and the code and parameter
hashes. `quatern stacks --robot sim_diffbot` lists them, and `quatern pin
<stack id>` marks one as last-known-good for `quatern deploy`.

## Docs

[quatern.co/docs/verification](https://quatern.co/docs/verification/#reading-the-report): reading the report, [cross-checks](https://quatern.co/docs/verification/#cross-checks), [what READY means](https://quatern.co/docs/verification/#what-ready-means)
