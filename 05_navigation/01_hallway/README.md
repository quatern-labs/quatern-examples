# Hallway: plan, deploy, drift in bounds

> **No key needed.**

The hallway is long, narrow and repetitive: 13 m long, 1.7 m wide, with a
door frame every 3 m. That's exactly where a localizer's drift adds up and a
loop closure can match the wrong door. This example takes the `jetson_rover`
catalog robot (skid-steer base, 2D lidar, depth camera, IMU) through a capture
in the hallway, verifies its reference localizer and planner, and deploys an
8 m run down the corridor in the simulator. Three questions matter: did the
drift stay inside its bounds, did the plan reach the goal, and did the live
run stay on the plan?

## Run it

```sh
quatern quickstart --robot jetson_rover --world hallway --yes
```

## Expected output

Trimmed.

```text
[1/7] Pick a robot
    jetson_rover.default: Robot jetson_rover (instance default): 3 DOF — base/x (unbounded) m, base/y (unbounded) m, base/yaw (unbounded) rad. Sensors: wheel_odom (odometry, estimates base), imu (imu, cross-checks base), scan (laserscan, cross-checks base), depth_cloud (pointcloud). Plans in grid2d over group 'base'.
[2/7] Pick a world
    Hallway: A 13 m office hallway, 1.7 m wide, with door frames every 3 m and a radiator: long, narrow and repetitive.
    goal: Drive down the hallway to (8.0, 0.6)
[3/7] Record a 120-second drive in the simulator
    recorded jetson_rover.default_2026-10-03_quickstart_hallway_v1: wheel_odom 20 Hz, imu 100 Hz, scan 7 Hz, depth_cloud 6 Hz
[6/7] Verify offline against the capture
    localization: drift at end 0.03; cross-checks wheel_odom vs imu 4%, wheel_odom vs scan 12%, imu vs scan 6%
    plan: 42 waypoints, 8.01 long, 17.3s
    verdict: READY after 1 iteration(s); stack stk_jetson_rover.default_20261003T075112117819
[7/7] Deploy in the simulator, behind the gate and the watchdog
    RECEIPT rcpt_jetson_rover.default_20261003T075112882041: COMPLETED (STOP_OBSERVED)
      stop: observed 0.03s after the stop request, travel after stop 0.001, turn after stop 0.000 rad (by watchdog)
      max deviation base: 0.181
      max deviation base/rad: 0.033
      live base:localizer vs wheel_odom: 7.1%
      live base:predicted vs measured: 8.9%

Quickstart complete in 21s wall-clock.
```

## Is the drift in bounds?

- **Offline**: `drift at end 0.03`. The capture drive ends where it started,
  so 0.03 m is pure error. The lines come from the deploy abort limit (0.5 m):
  warn above 0.12, fail above 0.25. `quatern verify` prints them next to the
  number.
- **Cross-checks**: the jetson rover's odometry comes from its wheels alone, so
  all three pairs count: wheel odometry vs IMU 4%, wheel odometry vs lidar
  12%, and IMU vs lidar 6%. All are under the 15% warning line. Where the
  corridor's walls don't pin the pose along it, the lidar's scan matcher gives
  that scan no estimate, so it doesn't count as agreement.
- **Live**: `max deviation base: 0.181` against the watchdog's abort limit of
  0.5 m. `base/rad: 0.033` against 0.8 rad. Both stayed well inside, so the
  run completed.

## What to look for in the run record

In `~/.quatern/receipts/jetson_rover.default/<stack id>/rcpt_*.json`:

- `predicted.plan_length` (8.01 m) and `predicted.duration_sec` are what the
  gate promised. The `commanded` and `observed` samples are what happened.
- `deviation_max` against the abort limits. `residuals_live` holds the live
  cross-check of the localizer against wheel odometry (7.1%) and of the plan
  against what was measured (8.9%).
- `live_checks.warnings` is empty when nothing came close to a limit.

## Docs

[quatern.co/docs/quickstart](https://quatern.co/docs/quickstart/) · [quatern.co/docs/verification](https://quatern.co/docs/verification/#reading-the-report)
