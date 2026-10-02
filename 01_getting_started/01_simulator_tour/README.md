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
    turtlebot3_burger.default: Robot turtlebot3_burger (instance default): 3 DOF — base/x (unbounded) m, base/y (unbounded) m, base/yaw (unbounded) rad. Sensors: wheel_odom (odometry, estimates base), imu (imu), scan (laserscan). Plans in grid2d over group 'base'.
[2/7] Pick a world
    Room: A 5.8 x 4.4 m living room: a kitchen island in the middle, a sofa, a cabinet, a chair and a bin along the walls.
    goal: Navigate around the island to reach (1.2, 2.0)
[3/7] Record a 120-second drive in the simulator
    recorded turtlebot3_burger.default_2026-10-02_quickstart_room_v1: wheel_odom 30 Hz, imu 100 Hz, scan 5 Hz
    note: only wheel_odom estimates base on this capture; single source, no cross-check is possible for it
[4/7] Calibrate the simulated actuators
    cal_turtlebot3_burger.default_20261002T062159509760: all joints nominal
[5/7] Generate localization and planning
    No API key is set, so Quatern uses its reference localizer and planner, with parameters chosen from
    this capture's stream health.
[6/7] Verify offline against the capture
    localization: drift at end 0.19; one source per channel, so nothing to cross-check
    plan: 52 waypoints, 2.61 long, 15.5s
    verdict: READY after 1 iteration(s); stack stk_turtlebot3_burger.default_20261002T062209273703
[7/7] Deploy in the simulator, behind the gate and the watchdog
    RECEIPT rcpt_turtlebot3_burger.default_20261002T062209284827: COMPLETED (STOP_OBSERVED)
      e-stop: not declared (software stop layers only)
      stop: observed 0.03s after the stop request, travel after stop 0.000 (by watchdog)
      max deviation base: 0.117
      max deviation base/rad: 0.242
      live base:localizer vs wheel_odom: 4.6%
      performance (TARGET): 1464 Hz sustainable vs 16 Hz input, CPU 10%, sandbox tier none, command-to-actuation 0.056s

Quickstart complete in 18s wall-clock.
  robot 0.0s, world 0.0s, capture 2.7s, calibrate 0.0s, generate 0.0s, verify 9.8s, deploy 5.5s
```

## What to look for in the run record

The receipt is plain JSON at
`~/.quatern/receipts/turtlebot3_burger.default/<stack id>/rcpt_*.json`.

- `final_state` is `COMPLETED` and `acknowledgement` is `STOP_OBSERVED`. A run
  only counts as complete when the goal was reached **and** the stop was seen.
- `evidence_domain` is `SIMULATION` and `hardware` is `false`. A sim result
  never passes for a hardware result.
- `code_hashes` and `modules` record exactly which localizer and planner ran.
- `deviation_max` shows how far the run strayed from the plan, in metres
  (`base`) and radians (`base/rad`). Compare it with the abort limits the gate
  printed (0.5 and 0.8).

`quatern stats` prints the time from install to the first verified stack and
to the first sim deploy. Those timings stay on your machine.

## Docs

[quatern.co/docs/quickstart](https://quatern.co/docs/quickstart/)
