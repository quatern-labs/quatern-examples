# 10 · Bringup

The checklist before a robot drives: are its sensors delivering, at their
rates, on one clock, in the frames the URDF says, mounted where the URDF says?
`quatern bringup` runs it on a recording (or a short live probe, where nothing
moves), and every failure comes with a fix that's been checked by running the
check again on the patched files.

| Example | What it shows | Needs |
| --- | --- | --- |
| [`01_wrong_scanner_frame`](01_wrong_scanner_frame/) | A TurtleBot 3 whose config puts the lidar on `laser`, a frame its URDF doesn't have. Bringup fails, `--write` applies the checked fix, and the second run passes. | Nothing |
