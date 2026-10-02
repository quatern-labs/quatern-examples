# Record a capture and verify against it

> **No key needed.**

`quatern capture` records a sensor session. In the simulator, an operator
drives the world's loop and stops where it started, and Quatern only records:
it never commands motion during a capture. `quatern verify` then runs the
localizer and planner modules in the sandbox against that recording and writes
a report in plain English. This example uses `sim_diffbot` because it has
**two** sources that estimate its base, wheel odometry and visual odometry.
That makes the report include a cross-check, the signal that catches a sensor
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
recorded sim_diffbot.default_2026-10-02_room_v1 (120.0 s)
  stream       verdict  health
  wheel_odom   ok       49.8 Hz, dropout 0%, noise 0.0040
  visual_odom  ok       29.4 Hz, dropout 2%, noise 0.0100
  imu          ok       99.8 Hz, dropout 0%, noise 0.0040
  scan         ok       10.0 Hz, dropout 0%, noise 0.0100
  depth_cloud  ok       6.0 Hz, dropout 0%, noise 0.0045
Verification of sim_diffbot.default — goal: Navigate around the island to reach (1.2, 2.0)
  localizer: python module, build none, run `python3 node.py`, sandbox tier none
  calibration: fresh (0 min old, cal_sim_diffbot.default_20261002T062316829878)
  capture: sim_diffbot.default_2026-10-02_room_v1
  localization (mapping mode), 1 iteration(s):
    base:wheel_odom vs visual_odom  10.9%  pass  under 15%
    drift at end: 0.122 (pass; warn > 0.25, critical > 1.0)
    loop closures: 150, mean error 0.323
    performance (HOST): 195 Hz sustainable vs 19 Hz input, CPU 36%, sandbox tier none — keeps up
    (warning) loop_closure: Mean loop closure error is 0.32 across 150 closures
  plan: 36 waypoints over 2.59 in grid2d, 8.2 s, no violations
  verdict: READY for the deploy gate (the code executed in the sandbox against the recorded stream)
  stack: stk_sim_diffbot.default_20261002T062341549544 (pin it with `quatern pin stk_sim_diffbot.default_20261002T062341549544`)
```

## Reading the report

- **Cross-check.** `base:wheel_odom vs visual_odom  10.9%  pass  under 15%`
  reads as: on the `base` channel, these two sources disagreed by 10.9% of the
  distance travelled, over time-aligned windows, and the warning line is 15%.
  The critical line is 30% (`thresholds.cross_check_defaults` in
  `~/.quatern/config.json`). With three or more sources, the one every
  disagreeing pair involves is named as the outlier.
- **Drift at end.** The capture ends where it started, so any distance between
  the estimated start and end is error. 0.122 is under the 0.25 warning line.
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
