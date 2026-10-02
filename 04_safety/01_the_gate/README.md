# The deploy gate

> **No key needed.**

`quatern deploy` never starts with motion. It starts with the **gate**: the
robot, the target and whether it's hardware, the stack and where it was
verified, the plan's length, peak speed and duration, every condition that
will abort the run, the worst-case distance the robot can travel after an
abort, and the path drawn over the map. Then it asks `y/N`. Only a yes mints
the one-time token a deploy needs, and the agent's tools can never mint one.
This example verifies a stack, pins it, and runs `deploy` with no terminal and
no `--yes`. The gate is printed, and the deploy refuses.

## Run it

```sh
quatern init --robot sim_diffbot --no-sample --yes
quatern capture --robot sim_diffbot --seconds 120 --label room --yes
quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"
quatern pin <stack id from verify>
quatern deploy --robot sim_diffbot < /dev/null
```

Run the last line in your own terminal without `< /dev/null` and you'll be
asked `Proceed past the gate? THE ROBOT WILL MOVE. [y/N]`. Answer `y` to watch
the simulated run.

## Expected output

Trimmed (the map is cut).

```text
pinned stk_sim_diffbot.default_20261002T063419506850 as last-known-good for sim_diffbot (verified on instance default)
DEPLOY GATE
  robot:      sim_diffbot (instance default)
  target:     sim (sim2d, not hardware)
  stack:      stk_sim_diffbot.default_20261002T063419506850 [ready] from capture sim_diffbot.default_2026-10-02_room_v1
  plan:       36 waypoints over 2.59 in grid2d
  max speed:  1.764 rad/s on base/yaw (limit 2.000)
  duration:   8.2 s predicted
  will abort on:
    - the localizer's estimate, or the robot's own state, off the plan by more than: base 0.5, base/rad 0.8
    - the localizer disagreeing with a source or with the plan past critical (planar 30%) for 5 ticks in a row, once moving 0.5 s
    - no estimate from the localizer for 0.50 s
    - a stream stale (0.50 s, or two periods of a slower source) or under 30% of its rate
    - any DOF outside its URDF bounds or over its velocity limit: base/x 0.5, base/y 0.5, base/yaw 2
    - the scan disagreeing with the map (under 35% on mapped structure for 5 scans in a row)
    - an obstacle in the planned path that the map did not have, or a drop-off ahead
  bounded travel after an abort (m, worst case on base/x):
    watchdog path 0.175   silence path 0.400   (v_max 0.5, brake 1, detect 0.100s)
  PLACEHOLDERS in the travel inputs (a hardware target refuses):
    - brake_decel not measured: defaulted to max_linear_acceleration
  map:        sim_diffbot.default_2026-10-02_room_v1, 0.0 h old
  sandbox:    tier none (resource limits always enforced)

.......#......**G.........##......
.......#......*###........##......
.......#.....**####.......##......
......##.....*##.##.......#.......
......##....S.............#.......
(0.30 m per character; origin (-3.8, -3.6); # occupied, * path, S start, G goal)
error: Proceed past the gate? THE ROBOT WILL MOVE. — no terminal to ask on; pass --yes to confirm
```

## What to look for

- **`will abort on`** is the watchdog's contract for this run, with the actual
  numbers loaded from your config and the robot's URDF.
- **Bounded travel**: how far the robot can still go after an abort. The
  watchdog path is when the watchdog stops it. The silence path is when
  everything on the host dies and the robot's own command-silence cut has to
  stop it.
- **`PLACEHOLDERS`**: an input to that bound that was never measured. The
  simulator proceeds anyway. A hardware target refuses until it's measured.
- No receipt is written, because nothing was dispatched. Answer `y` and the
  receipt's `gate` section records who confirmed it and whether a physical
  e-stop was declared (`--estop`).

## Docs

[quatern.co/docs/safety](https://quatern.co/docs/safety/#the-deploy-gate): the deploy gate
