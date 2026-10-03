# A cross-check catches a drifting sensor

> **No key needed.**

The same capture-and-verify as [`01_capture_and_verify`](../01_capture_and_verify/),
except the simulator gives `sim_diffbot`'s wheel odometry a 45% distance and
heading error. The fault goes in through the simulator target's `drift`
option, which [`sim_target.py`](sim_target.py) sets in the robot's
`.quatern.json`. Every stream still looks healthy on its own (right rate, no
dropouts), so only comparing wheel odometry with the other sources reveals the
problem. Visual odometry, the IMU and the lidar all disagree with wheel
odometry and agree with each other, so verification names wheel odometry as
the faulty source and refuses to call the stack ready.

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
recorded sim_diffbot.default_2026-10-03_room_v1 (120.0 s)
  stream       verdict  health
  wheel_odom   ok       49.8 Hz, dropout 0%, noise 0.0040
  visual_odom  ok       29.4 Hz, dropout 2%, noise 0.0100
  imu          ok       99.8 Hz, dropout 0%, noise 0.0040
  scan         ok       10.0 Hz, dropout 0%, noise 0.0100
Verification of sim_diffbot.default — goal: Navigate around the island to reach (1.2, 2.0)
  capture: sim_diffbot.default_2026-10-03_room_v1
  localization (mapping mode), 3 iteration(s):
    base:wheel_odom vs visual_odom  90.9%  FAIL  over the 30% critical limit
    base:wheel_odom vs imu          31.2%  FAIL  over the 30% critical limit
    base:wheel_odom vs scan         90.6%  FAIL  over the 30% critical limit
    base:visual_odom vs imu         2.4%   pass  under 15%
    base:visual_odom vs scan        6.3%   pass  under 15%
    base:imu vs scan                4.5%   pass  under 15%
    drift at end: 2.001 (FAIL; 2.00 is 400% of the 0.50 deploy abort limit (warn > 0.12, fail > 0.25))
    loop closures: 150, mean error 0.992
    (critical) drift: Trajectory drifted 2.00 by the end of the run: 2.00 is 400% of the 0.50 deploy abort limit (warn > 0.12, fail > 0.25). A plan from this estimate would start that far from where the robot is
  plan: not attempted (localization did not pass)
  next: calibrate — wheel_odom is the outlier on base: it disagrees with visual_odom (91%), imu (31%), scan (91%), while visual_odom, imu and scan agree. wheel_odom reads distance 41% long against visual_odom; turns 41% too far against visual_odom; turns 43% too far against imu; reads distance 44% long against scan; turns 44% too far against scan: likely wheel or leg slip, or a wrong wheel radius (or stride calibration); or a wrong track width, or slip while turning.. Every other source agrees, so the actuator-derived estimate is at fault; recalibrate before re-running.
  verdict: NOT READY
    - localization health is 'fail': Localization failed verification: wheel_odom is the outlier on base: it disagrees with visual_odom (91%), imu (31%), scan (91%), while visual_odom, imu and scan agree. wheel_odom reads distance 41% long against visual_odom; turns 41% too far against visual_odom; turns 43% too far against imu; reads distance 44% long against scan; turns 44% too far against scan: likely wheel or leg slip, or a wrong wheel radius (or stride calibration); or a wrong track width, or slip while turning. (+2 more critical) (base: 3 of 6 cross-checks disagree across wheel_odom, visual_odom, imu and scan).
    - no motion plan on record
```

## Reading the report

- Every stream passes its health check (`ok`, right rate). Stream health can't
  see this fault, but the cross-checks can. Every pair with `wheel_odom` fails
  (91%, 31% and 91% against a 30% critical line), and every pair without it
  passes.
- *"wheel_odom is the outlier on base"*: visual odometry, the IMU and the
  lidar agree with each other, so Quatern can say which source is wrong, not
  just that two disagree. It also says how: distance read about 41–44% long
  and turns 41–44% too far, the 45% fault the simulator injected. That points
  at wheel slip, the wheel radius or the track width, so `next` is
  `calibrate`, not a recapture.
- `wheel_odom vs imu` is only 31% because the IMU checks heading alone. The
  distance error shows up against visual odometry and the lidar.
- `3 iteration(s)`: verification retried before giving up. It doesn't loop
  forever (`thresholds.max_offline_iterations`).
- No plan is attempted on a localization that failed, so a stack like this one
  can never reach the gate.

## Docs

[quatern.co/docs/verification](https://quatern.co/docs/verification/#cross-checks): cross-checks
