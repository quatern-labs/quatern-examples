# 04 · Safety

Nothing moves until a person says yes at the **gate**. Once something is
moving, a **watchdog** in its own process can stop it at any moment, and every
run ends in a write-once **receipt** that says how it ended and why. These
examples make each layer act, in the simulator.

| Example | What it shows | Needs |
| --- | --- | --- |
| [`01_the_gate`](01_the_gate/) | What the gate shows before a deploy, and that it refuses when nobody is there to answer. | Nothing |
| [`02_watchdog_stops_drift`](02_watchdog_stops_drift/) | Inject odometry drift into the simulator. The watchdog aborts the run mid-motion. Then read the ABORTED receipt. | Nothing |
| [`03_switched_off_sensor`](03_switched_off_sensor/) | Switch a sensor off in the simulator. The deploy refuses before anything moves. | Nothing |

**Which faults can you inject?** The built-in simulator (backend `sim2d`)
reads two fault options from a target's `options`:

- `drift`: `{"<source>": fraction}` adds that much distance and heading error
  to an odometry or visual-odometry source (examples 02 and
  [03_verification/02](../03_verification/02_cross_check_catches_drift/)).
- `failed_sensors`: `["<source>", ...]` switches those sources off for the
  whole session (example 03).

A sensor that freezes partway *through* a run (a stale stream mid-motion) is
not injectable in the built-in simulator today. The watchdog's stale-stream
check exists, and Quatern's Gazebo setup has scripts for that kind of fault
(dropping a topic, an obstacle appearing, stopping the command stream). Those
need ROS 2 and Gazebo, and they're not part of these examples.
