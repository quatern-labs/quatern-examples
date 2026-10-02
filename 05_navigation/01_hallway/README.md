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
[2/7] Pick a world
    Hallway: A 13 m office hallway, 1.7 m wide, with door frames every 3 m and a radiator: long, narrow and repetitive.
    goal: Drive down the hallway to (8.0, 0.6)
[3/7] Record a 120-second drive in the simulator
    recorded jetson_rover.default_2026-10-02_quickstart_hallway_v1: wheel_odom 20 Hz, imu 100 Hz, scan 7 Hz, depth_cloud 6 Hz
[6/7] Verify offline against the capture
    localization: drift at end 0.21; one source per channel, so nothing to cross-check
    plan: 42 waypoints, 8.03 long, 16.3s
    verdict: READY after 1 iteration(s); stack stk_jetson_rover.default_20261002T063504663874
[7/7] Deploy in the simulator, behind the gate and the watchdog
    RECEIPT rcpt_jetson_rover.default_20261002T063504672781: COMPLETED (STOP_OBSERVED)
      stop: observed 0.03s after the stop request, travel after stop 0.000 (by watchdog)
      max deviation base: 0.199
      max deviation base/rad: 0.107
      live base:localizer vs wheel_odom: 9.2%
      live base:predicted vs measured: 12.3%

Quickstart complete in 14s wall-clock.
```

## Is the drift in bounds?

- **Offline**: `drift at end 0.21`. The capture drive ends where it started,
  so 0.21 m is pure error. It passes because it's under the warning line of
  0.25 (the critical line is 1.0, `thresholds.drift_warn` /
  `drift_critical`). It's close, which is typical of this corridor. `quatern
  verify` prints the thresholds next to the number.
- **Live**: `max deviation base: 0.199` against the watchdog's abort limit of
  0.5 m. `base/rad: 0.107` against 0.8 rad. Both stayed well inside, so the
  run completed.

## What to look for in the run record

In `~/.quatern/receipts/jetson_rover.default/<stack id>/rcpt_*.json`:

- `predicted.plan_length` (8.03 m) and `predicted.duration_sec` are what the
  gate promised. The `commanded` and `observed` samples are what happened.
- `deviation_max` against the abort limits. `residuals_live` holds the live
  cross-check of the localizer against wheel odometry (9.2%).
- `live_checks.warnings` is empty when nothing came close to a limit.

## Docs

[quatern.co/docs/quickstart](https://quatern.co/docs/quickstart/) · [quatern.co/docs/verification](https://quatern.co/docs/verification/#reading-the-report)
