# 09 · Regression tests in CI

Save a set of your robot's recordings once, then replay it against every
change to your localizer or planner. `quatern regress run` exits 1 when a
metric gets worse, so it can fail a pull request. The set is a directory you
commit next to your modules, and it replays with nothing but
`pip install quatern`: no robot and no ROS.

| Example | What it shows | Needs |
| --- | --- | --- |
| [`01_replay_in_ci`](01_replay_in_ci/) | `regress init`, `run` and `baseline` on a TurtleBot 3's recording. A one-line change to the localizer fails the run, and the GitHub Actions workflow that runs it on every pull request. | Nothing |
