# 03 · Verification

Quatern doesn't trust a localizer's opinion of itself. It replays a recorded
capture through the code in a sandbox, then computes the signals itself:
drift, loop closures, and **cross-checks** between every pair of independent
sources on the same motion: odometry, and the lidar and IMU that check it. A
stack is `READY` only when those pass and the
planner reaches the goal on the map they built.

| Example | What it shows | Needs |
| --- | --- | --- |
| [`01_capture_and_verify`](01_capture_and_verify/) | Record a simulated capture, verify against it, and read the report: what READY means and how to read a cross-check. | Nothing |
| [`02_cross_check_catches_drift`](02_cross_check_catches_drift/) | The same, with wheel odometry made 45% wrong in the simulator. The cross-check catches it and the verdict is NOT READY. | Nothing |
