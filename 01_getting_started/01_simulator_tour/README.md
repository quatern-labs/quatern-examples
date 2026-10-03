# The 2-minute simulator tour

> **No key needed.** Runs entirely on your machine in Quatern's built-in simulator.

`quatern quickstart` takes a catalog robot (here a TurtleBot 3 Burger) through
the whole loop in seven steps. It installs the robot, picks a world, records a
scripted 120-second drive in sim time, calibrates, generates a localizer and a
planner, verifies them offline against the capture, and deploys the result in
the simulator behind the gate and the watchdog. No ROS, no Gazebo, no URDF to
write. Without a sign-in it uses Quatern's reference localizer and planner. The
first time you run a bare `quatern`, it offers this same tour.

## Run it

```sh
quatern quickstart --robot turtlebot3_burger --world room --yes
```

`--yes` answers every question with its default, which includes passing the
gate for the **simulated** deploy. Leave it off to be asked. `./run.sh` runs
the same command.

## Expected output

Trimmed. IDs carry timestamps, and timings depend on your machine.

```text
[1/7] Pick a robot
    turtlebot3_burger.default: Robot turtlebot3_burger (instance default): 3 DOF — base/x (unbounded) m, base/y (unbounded) m, base/yaw (unbounded) rad. Sensors: wheel_odom (odometry, estimates base, fuses imu), imu (imu, cross-checks base), scan (laserscan, cross-checks base). Plans in grid2d over group 'base'.
[2/7] Pick a world
    Room: A 5.8 x 4.4 m living room: a kitchen island in the middle, a sofa, a cabinet, a chair and a bin along the walls.
    goal: Navigate around the island to reach (1.2, 2.0)
[3/7] Record a 120-second drive in the simulator
    recorded turtlebot3_burger.default_2026-10-03_quickstart_room_v1: wheel_odom 30 Hz, imu 100 Hz, scan 5 Hz
[4/7] Calibrate the simulated actuators
    cal_turtlebot3_burger.default_20261003T075043352665: no actuated joints to sweep (driven by base velocity)
[5/7] Generate localization and planning
    No API key is set, so Quatern uses its reference localizer and planner, with parameters chosen from
    this capture's stream health.
[6/7] Verify offline against the capture
    localization: drift at end 0.05; cross-checks wheel_odom vs scan 11%, imu vs scan 9%
    plan: 35 waypoints, 2.46 long, 14.9s
    verdict: READY after 1 iteration(s); stack stk_turtlebot3_burger.default_20261003T075050072216
[7/7] Deploy in the simulator, behind the gate and the watchdog
    RECEIPT rcpt_turtlebot3_burger.default_20261003T075050614297: COMPLETED (STOP_OBSERVED)
      stop: observed 0.00s after the stop request, travel after stop 0.000, turn after stop 0.000 rad (by watchdog)
      max deviation base: 0.117
      max deviation base/rad: 0.261
      live base:localizer vs wheel_odom: 7.7%
      live base:predicted vs measured: 17.4%
      performance (TARGET): 7876 Hz sustainable vs 17 Hz input, CPU 10%, sandbox tier none, command-to-actuation 0.061s

Quickstart complete in 15s wall-clock.
  robot 0.0s, world 0.0s, capture 2.1s, calibrate 0.0s, generate 0.0s, verify 6.7s, deploy 5.8s
deploy watchdog: base:predicted_vs_measured: the localizer and the plan disagree by 18% of the distance travelled over the last 3.8s (warn 15%, critical 30%)
```

The verify step cross-checks the localizer's sources against each other.
Wheel odometry estimates the base. The lidar (through a scan-to-map matcher)
and the IMU (heading only) check it: `wheel_odom vs scan 11%` and `imu vs
scan 9%`, both under the 15% warning line. Wheel odometry vs IMU isn't
compared, because the TurtleBot 3's odometry already takes its heading from
the IMU (`fuses imu`). The `deploy watchdog` line is a live warning, not an
abort: the run only aborts past 30% for 5 ticks in a row.

## What to look for in the run record

The receipt is plain JSON at
`~/.quatern/receipts/turtlebot3_burger.default/<stack id>/rcpt_*.json`.

- `final_state` is `COMPLETED` and `acknowledgement` is `STOP_OBSERVED`. A run
  only counts as complete when the goal was reached **and** the stop was seen.
- `evidence_domain` is `SIMULATION` and `hardware` is `false`. A sim result
  never passes for a hardware result.
- `code_hashes` and `modules` record exactly which localizer and planner ran.
- `deviation_max` shows how far the run strayed from the plan, in metres
  (`base`) and radians (`base/rad`). Compare it with the watchdog's abort
  limits for a planar base, 0.5 m and 0.8 rad.
- `residuals_live` holds the live cross-checks (`base:localizer_vs_wheel_odom`,
  `base:predicted_vs_measured`), and `live_checks.warnings` holds any warning
  the watchdog printed.

`quatern stats` prints the time from install to the first verified stack and
to the first sim deploy. Those timings stay on your machine.

## Docs

[quatern.co/docs/quickstart](https://quatern.co/docs/quickstart/)
