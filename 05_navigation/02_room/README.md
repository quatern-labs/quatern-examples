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
[2/7] Pick a world
    Room: A 5.8 x 4.4 m living room: a kitchen island in the middle, a sofa, a cabinet, a chair and a bin along the walls.
    goal: Navigate around the island to reach (1.2, 2.0)
[3/7] Record a 120-second drive in the simulator
    recorded turtlebot3_waffle.default_2026-10-02_quickstart_room_v1: wheel_odom 30 Hz, imu 100 Hz, scan 5 Hz
[6/7] Verify offline against the capture
    localization: drift at end 0.13; one source per channel, so nothing to cross-check
    plan: 44 waypoints, 2.63 long, 13.9s
    verdict: READY after 1 iteration(s); stack stk_turtlebot3_waffle.default_20261002T062729340397
[7/7] Deploy in the simulator, behind the gate and the watchdog
    RECEIPT rcpt_turtlebot3_waffle.default_20261002T062729366499: COMPLETED (STOP_OBSERVED)
      stop: observed 0.00s after the stop request, travel after stop 0.000 (by watchdog)
      max deviation base: 0.102
      max deviation base/rad: 0.253
      live base:localizer vs wheel_odom: 2.9%

Quickstart complete in 17s wall-clock.
```

To see the path drawn over the map, verify, pin and run `quatern deploy` on
this robot yourself. The gate prints the map with the path, as in
[04_safety/01_the_gate](../../04_safety/01_the_gate/).

## Is the drift in bounds?

`drift at end 0.13`, under the 0.25 warning line. Live, the run never got
further than 0.102 m from the plan (abort at 0.5 m).

## What to look for in the run record

In `~/.quatern/receipts/turtlebot3_waffle.default/<stack id>/rcpt_*.json`,
`map_id` names the occupancy map the plan was made on. The map itself is in
`~/.quatern/maps/` as a `.pgm` image you can open in any viewer.
`predicted.waypoints` (44) and `predicted.plan_length` (2.63 m) are the path
around the island.

## Docs

[quatern.co/docs/quickstart](https://quatern.co/docs/quickstart/)
