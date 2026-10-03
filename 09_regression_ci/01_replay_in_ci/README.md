# Replay recordings in CI, fail on a regression

> **No key needed.**

## What it shows

A regression set is a directory holding a robot's recordings, its config and
URDF, and a baseline of every metric. You commit it next to your localizer
and planner. This example records a TurtleBot 3 in the simulator, writes its
localizer out as a module directory (here, with `quatern tune --out`), makes
a set with `regress init`, and replays it with `regress run`: no regressions.
Then it changes one parameter, `live_map_weight` to 0, so the localizer stops
pulling its pose toward the scan map. The next run fails: drift at the end
grows from 0.037 m to 0.169 m, the JUnit report has the failure, and the exit
code is 1. `regress baseline` accepts the new numbers when a change is meant
to move them. [`quatern-regress.yml`](quatern-regress.yml) is the GitHub
Actions workflow that runs the same `regress run` on every pull request.

## Run it

```sh
quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes
quatern tune --robot turtlebot3_burger "less drift" --out modules/localizer

quatern regress init regress/room --robot turtlebot3_burger --world "reach (1.2, 2.0)" --localizer modules/localizer
quatern regress run regress/room --localizer modules/localizer --junit regress.xml

# set "live_map_weight": 0 in modules/localizer/params.json, then
quatern regress run regress/room --localizer modules/localizer --junit regress.xml    # exits 1
quatern regress baseline regress/room --localizer modules/localizer
```

`run.sh` does this in a scratch directory and makes the edit with
`set_param.py`.

To run it in CI, copy [`quatern-regress.yml`](quatern-regress.yml) to
`.github/workflows/` in the repository that holds `modules/` and `regress/`.
It installs Quatern from PyPI and needs no robot and no ROS.

## Expected output

Trimmed.

```text
quatern tune — turtlebot3_burger.default: less localization drift ('less drift')
  starting from generated defaults (no verified stack yet); replayed on 1 recording(s), 11 trial(s)
  ...
  changes: smoothing_window = 9
  wrote the tuned module to modules/localizer (verify it: quatern verify --robot turtlebot3_burger.default --goal ... --module modules/localizer)
made regress/room: 1 recording(s) of turtlebot3_burger.default, baseline recorded
run it: quatern regress run regress/room --localizer ...
quatern regress — regress/room
  recording                                     metric       baseline  now
  turtlebot3_burger.default_2026-10-03_room_v1  all metrics                 ok  within tolerance

no regressions
modules/localizer/params.json: live_map_weight = 0
quatern regress — regress/room
  recording                                     metric        baseline  now
  turtlebot3_burger.default_2026-10-03_room_v1  drift_at_end  0.0373    0.1693  FAIL  0.1693 is over 0.0373 + 0.01 allowed
                                                drift_band    0.0373    0.1693  FAIL  drift crosses into warning: 0.17 is 34% of the 0.50 deploy abort limit (warn > 0.12, fail > 0.25)

2 regression(s)
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="quatern regress" tests="1" failures="1">
  <testcase classname="quatern.regress" name="turtlebot3_burger.default_2026-10-03_room_v1"><failure message="drift_at_end: 0.1693 is over 0.0373 + 0.01 allowed">drift_at_end: 0.0373 -&gt; 0.1693: 0.1693 is over 0.0373 + 0.01 allowed</failure><failure message="drift_band: drift crosses into warning: 0.17 is 34% of the 0.50 deploy abort limit (warn &gt; 0.12, fail &gt; 0.25)">drift_band: 0.0373 -&gt; 0.1693: drift crosses into warning: 0.17 is 34% of the 0.50 deploy abort limit (warn &gt; 0.12, fail &gt; 0.25)</failure></testcase>
</testsuite>
baseline recorded for 1 recording(s) in regress/room
quatern regress — regress/room
  recording                                     metric       baseline  now
  turtlebot3_burger.default_2026-10-03_room_v1  all metrics                 ok  within tolerance

no regressions
```

## What to look for in the set

`regress/room/` is what you commit:

```text
regress/room/
  regress.json                       robot, goal, recordings, baseline, tolerances
  robot/turtlebot3_burger.quatern.json
  robot/turtlebot3_burger.urdf
  recordings/turtlebot3_burger.default_2026-10-03_room_v1/
    capture.json
    frames.jsonl.gz                  every frame, in Quatern's portable form (about 690 KB for 60 s)
```

- `regress.json` → `baseline.<recording>` holds the numbers each run is
  compared with: `drift_at_end` (0.0373), `residual_max`, `loop_closures`,
  `plan_ok`, `plan_length`, `plan_duration` and `violations` (the planner
  metrics are there because the set has a `world`).
- `regress.json` → `tolerances`: `{"relative": 0.1, "absolute": 0.01}`. A
  metric regresses when it grows by more than 10% or 0.01, whichever is more,
  or (`drift_band`) when drift crosses into the warning or critical band.
- `baseline_quatern` is the Quatern version that recorded the baseline.
- Without `--localizer`, the code under test is what Quatern generates for
  the robot. That makes the set a check on a Quatern upgrade, too.

## Docs

[quatern.co/docs/regress](https://quatern.co/docs/regress/#what-is-compared) · [In CI](https://quatern.co/docs/regress/#in-ci)
