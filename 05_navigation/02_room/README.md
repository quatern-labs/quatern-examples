# Room: plan around an obstacle

> **No key needed.**

The room is 5.8 × 4.4 m with a kitchen island in the middle and furniture
along the walls. The goal on the far side of the island means the planner
can't go straight: it has to find a way around on the occupancy map Quatern
built from the capture's lidar, inflated by the robot's footprint. This
example runs a TurtleBot 3 Waffle through it: capture, verify, plan around
the island, and deploy in the simulator.

## Run it

```sh
quatern quickstart --robot turtlebot3_waffle --world room --yes
```

## Expected output

Trimmed.

```text
[1/7] Pick a robot
    turtlebot3_waffle.default: Robot turtlebot3_waffle (instance default): 3 DOF — base/x (unbounded) m, base/y (unbounded) m, base/yaw (unbounded) rad. Sensors: wheel_odom (odometry, estimates base, fuses imu), imu (imu, cross-checks base), scan (laserscan, cross-checks base). Plans in grid2d over group 'base'.
[2/7] Pick a world
    Room: A 5.8 x 4.4 m living room: a kitchen island in the middle, a sofa, a cabinet, a chair and a bin along the walls.
    goal: Navigate around the island to reach (1.2, 2.0)
[3/7] Record a 120-second drive in the simulator
    recorded turtlebot3_waffle.default_2026-10-03_quickstart_room_v1: wheel_odom 30 Hz, imu 100 Hz, scan 5 Hz
[6/7] Verify offline against the capture
    localization: drift at end 0.04; cross-checks wheel_odom vs scan 13%, imu vs scan 11%
    plan: 44 waypoints, 2.73 long, 15.7s
    verdict: READY after 1 iteration(s); stack stk_turtlebot3_waffle.default_20261003T075125962152
[7/7] Deploy in the simulator, behind the gate and the watchdog
    RECEIPT rcpt_turtlebot3_waffle.default_20261003T075126311898: COMPLETED (STOP_OBSERVED)
      stop: observed 0.03s after the stop request, travel after stop 0.000, turn after stop 0.000 rad (by watchdog)
      max deviation base: 0.042
      max deviation base/rad: 0.199
      live base:localizer vs wheel_odom: 4.5%
      live base:predicted vs measured: 13.0%

Quickstart complete in 13s wall-clock.
```

To see the path drawn over the map, verify, pin and run `quatern deploy` on
this robot yourself. The gate prints the map with the path, as in
[04_safety/01_the_gate](../../04_safety/01_the_gate/).

## Is the drift in bounds?

`drift at end 0.04`, under the 0.12 warning line (the fail line is 0.25).
The lidar checks the wheel odometry (13%) and the IMU (11%), both under the
15% warning line. Wheel odometry vs IMU isn't compared, because the
TurtleBot 3's odometry already fuses the IMU. Live, the run never got further
than 0.042 m from the plan (abort at 0.5 m).

## What to look for in the run record

In `~/.quatern/receipts/turtlebot3_waffle.default/<stack id>/rcpt_*.json`,
`map_id` names the occupancy map the plan was made on. The map itself is in
`~/.quatern/maps/` as a `.pgm` image you can open in any viewer.
`predicted.waypoints` (44) and `predicted.plan_length` (2.73 m) are the path
around the island.

## Docs

[quatern.co/docs/quickstart](https://quatern.co/docs/quickstart/)
