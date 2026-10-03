# Less drift in the hallway

> **No key needed.**

## What it shows

The hallway is where a localizer drifts: long, narrow, and with a door frame
every 3 m that all look alike. This example runs the `jetson_rover` through
the hallway quickstart (capture, verify, simulated deploy), then asks
`quatern tune` for "less drift in the hallway". The words pick the objective
(drift, so the localizer, and its `drift_at_end`). Quatern starts from the
stack the quickstart verified, tries one localizer parameter at a time
(`smoothing_window`, `loop_closure_threshold`, `keyframe_stride`,
`live_map_weight`) and replays each candidate on the robot's recordings
exactly as `quatern verify` does. It keeps a change only if it cuts mean
drift by 2% or more. You get drift before and after on every recording, and
the change as a diff of `params.json`. Nothing is applied.

## Run it

```sh
quatern quickstart --robot jetson_rover --world hallway --yes
quatern tune --robot jetson_rover "less drift in the hallway"
```

Then, to use the result:

```sh
quatern tune --robot jetson_rover "less drift in the hallway" --out tuned_localizer/   # write the tuned module
quatern tune --robot jetson_rover "less drift in the hallway" --save                   # verify it as a new stack
```

`--save` doesn't pin or deploy the new stack. `quatern pin` and the gate in
`quatern deploy` are still the only way it runs.

## Expected output

Trimmed (the quickstart's progress lines are cut).

```text
[6/7] Verify offline against the capture
    localization: drift at end 0.06; cross-checks wheel_odom vs imu 4%, wheel_odom vs scan 12%, imu vs scan 6%
    plan: 41 waypoints, 7.97 long, 17.2s
    verdict: READY after 1 iteration(s); stack stk_jetson_rover.default_20261003T200517355353
[7/7] Deploy in the simulator, behind the gate and the watchdog
    RECEIPT rcpt_jetson_rover.default_20261003T200518419864: COMPLETED (STOP_OBSERVED)
Quickstart complete in 23s wall-clock.
quatern tune — jetson_rover.default: less localization drift ('less drift in the hallway')
  starting from stack stk_jetson_rover.default_20261003T200517355353; replayed on 2 recording(s), 11 trial(s)
  metric: drift_at_end, how far the localizer's pose ends from where the recording says the robot was

  recording                                              metric              before  after   change
  jetson_rover.default_2026-10-03_quickstart_hallway_v1  drift_at_end        0.0574  0.0513  -11%
                                                         loop_closures       0       0       same
                                                         loop_closure_error  0       0       same
  jetson_rover.default_2026-10-03_sample_v1              drift_at_end        0.0416  0.0398  -4%
                                                         loop_closures       0       0       same
                                                         loop_closure_error  0       0       same

  changes: live_map_weight = 0.4
  params.json:
    --- a/params.json
    +++ b/params.json
    @@ -1,6 +1,7 @@
     {
       "actuator_response": {},
       "keyframe_stride": 12,
    +  "live_map_weight": 0.4,
       "loop_closure_threshold": 0.75,
       "smoothing_window": 4,
       "source_weights": {
  nothing was applied: --out writes the tuned module, --save verifies it as a stack; only `quatern deploy` runs one
```

## What to look for

- **The recordings**: tune replays the robot's newest three recordings, here
  the hallway capture and the sample capture that came with the robot. Name
  others with `--recording`. Drift went down on both: 0.0574 to 0.0513 m in
  the hallway (-11%) and 0.0416 to 0.0398 m on the sample (-4%).
- **The change**: `live_map_weight` from its default 0.25 to 0.4. While
  mapping, the localizer pulls its pose toward the map it has built so far by
  this much. Pulling harder helps in a corridor that looks the same every few
  metres, and pulling too hard makes a fast robot oscillate, which is why it
  is a parameter.
- **Loop closures**: `loop_closures` and `loop_closure_error` are checked so
  a change can't buy less drift with unreliable closures. A candidate that
  pushes the closure error over its warn limit is ruled out.
- **Every trial**: the 11 trials, and why any was ruled out, are listed by
  `quatern tune ... --json`.
- **The stack it started from**: `starting from stack stk_...` is the
  quickstart's verified stack. The diff is against that stack's
  `localizer_params`, in `~/.quatern/stacks/jetson_rover/<stack id>.json`.

## Docs

[quatern.co/docs/tune](https://quatern.co/docs/tune/#what-it-tunes) · [How a candidate is judged](https://quatern.co/docs/tune/#how-a-candidate-is-judged)
