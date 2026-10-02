# A switched-off sensor stops the deploy before it starts

> **No key needed.**

The verified `sim_diffbot` stack depends on visual odometry. This example adds
a simulator target, `sim_no_camera`, with that sensor switched off
(`"failed_sensors": ["visual_odom"]`), and deploys there. Before any motion,
`deploy` probes every stream the robot is configured with. The camera produces
nothing, so the deploy is **refused** and the robot never moves. This is the
gate's preconditions at work, not the watchdog. The built-in simulator can
switch a sensor off for a whole session, but it can't freeze one partway
through a run (see the [section README](../README.md)).

## Run it

```sh
quatern init --robot sim_diffbot --no-sample --yes
quatern capture --robot sim_diffbot --seconds 120 --label room --yes
quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"
python3 sim_target.py sim_diffbot sim_no_camera '{"failed_sensors": ["visual_odom"]}'
quatern deploy --robot sim_diffbot --stack <stack id from verify> --target sim_no_camera --yes
```

`deploy` exits non-zero. `./run.sh` checks for it.

## Expected output

Trimmed. Note that `--yes` was given, and it still refuses.

```text
DEPLOY GATE
  robot:      sim_diffbot (instance default)
  target:     sim_no_camera (sim2d, not hardware)
  stack:      stk_sim_diffbot.default_20261002T063454453837 [ready] from capture sim_diffbot.default_2026-10-02_room_v1
  [...]

REFUSED:
  - stream problem: visual_odom (camera) produced no samples in 0s; it is switched off in this simulation
```

## What to look for

- `--yes` answers the gate's *question*. It can't override a failed
  precondition. Preconditions also cover a fresh calibration, a fresh map,
  and, on hardware, a passing stop-on-silence check and no placeholder
  values.
- There's no receipt, because nothing was requested of the robot. Compare that
  with [`02_watchdog_stops_drift`](../02_watchdog_stops_drift/), where the
  fault only shows up once the robot moves, so it's the watchdog that stops it
  and the receipt that records it.
- `quatern doctor --robot sim_diffbot --target sim_no_camera` reports the same
  stream problem ahead of time.

## Docs

[quatern.co/docs/safety](https://quatern.co/docs/safety/#the-layers): the safety layers
