# 08 · Tuning

Say what you want in your own words, and `quatern tune` turns it into
parameter changes. Each change is replayed on the robot's recordings and kept
only if it helps, and you get before/after numbers per recording and the
change as a diff. Tuning moves nothing and deploys nothing: the result goes
through `quatern verify` and the gate like any other code.

| Example | What it shows | Needs |
| --- | --- | --- |
| [`01_less_drift_in_the_hallway`](01_less_drift_in_the_hallway/) | "Less drift in the hallway" on a Jetson rover: which localizer knobs were tried, the one kept, and drift before and after on each recording. | Nothing |

Two goals are understood today: **drift** (words like drift, localization,
lost, pose, map) tunes the localizer, and **goal oscillation** (oscillating,
jitter, overshoot, settle) tunes how the planner arrives. Anything else is
refused with that list. `--agent` lets the agent propose changes of its own.
