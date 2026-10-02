# Set up a robot from a URDF

> **No key needed.**

Point `/init` (or `quatern init`) at your robot's URDF and Quatern writes the
`.quatern.json` next to a copy of it. Sensors come from the URDF's own
`<sensor>` elements, and the Gazebo extension most real URDFs already carry is
read too. A few questions cover what the URDF can't say: is this a mobile
robot, and which link is the base? Does it publish odometry? Which backend
should it run on? Each question has a flag, so the whole thing can run
unattended. `doctor` then checks the description, the config and the backend
before anything moves, and exits non-zero with a plain-English list of fixes
if something's wrong.

The sample, [`my_rover.urdf`](my_rover.urdf), is a small diff-drive base with
fixed wheels (driven by base velocity, like most ROS 2 bases) and a 2D lidar
declared as a Gazebo `ray` sensor. Swap in your own URDF.

## Run it

In the REPL (`quatern`, from this folder):

```text
quatern (no robot / -) > /init --urdf my_rover.urdf --mobile-base base_link --odometry yes --backend sim2d --yes
quatern (my_rover / sim2d:sim) > /doctor
```

Or as two commands, which is what `./run.sh` and CI do:

```sh
quatern init --urdf my_rover.urdf --mobile-base base_link --odometry yes --backend sim2d --yes
quatern doctor --robot my_rover
```

Leave the flags off and `/init --urdf my_rover.urdf` asks each question
instead. `--backend sim2d` gives the robot a target in the built-in simulator,
so you can try it straight away. Use `ros2` for a real robot.

## Expected output

Real REPL session, trimmed. Paths and the toolchain lines depend on your machine.

```text
quatern (no robot / -) > /init --urdf my_rover.urdf --mobile-base base_link --odometry yes --backend sim2d --yes
wrote ~/.quatern/robots/my_rover.urdf
wrote ~/.quatern/robots/my_rover.quatern.json
  Robot my_rover (instance default): 3 DOF — base/x (unbounded) m, base/y (unbounded) m, base/yaw (unbounded) rad. Sensors: base_odom (odometry, estimates base), scan (laserscan). Plans in grid2d over group 'base'.
robot my_rover selected; target sim2d:sim
quatern (my_rover / sim2d:sim) > /doctor
quatern doctor — my_rover (instance default, target sim)
  ok    config      my_rover.default: 3 DOF, 2 sensor(s), plans in grid2d
  ok    urdf        no TODO placeholders
  ok    backend     target 'sim' uses the sim2d backend
  ok    backend     built-in simulator: world 'room' (Room), 5x real time when live
  ok    streams     base_odom (odometry) at 50.0 Hz, last sample 0.02s ago
  ok    streams     scan (laserscan) at 5.0 Hz, last sample 0.20s ago
  WARN  calibration no fresh valid calibration
        -> run `quatern calibrate --robot my_rover`
  WARN  sandbox     isolation tier none: resource limits only, no filesystem or network namespace
        -> install bubblewrap on Linux for a hard tier
  WARN  silence     stop-on-silence not verified on target 'sim'
  WARN  agent       agent off: not signed in and no API key
ready: no blocking problems
```

## What to look for

There is no run record yet, because nothing has moved. Read what `init` wrote
instead:

- `~/.quatern/robots/my_rover.quatern.json` has a `sim` target
  (`"backend": "sim2d"`) and a `mock` target. A `mobile_base` section with
  conservative default limits (0.5 m/s, 1.0 rad/s). Replace them with your
  robot's real numbers.
- `sensors` lists `scan` as a `laserscan` on `laser_link`, which the URDF told
  it, plus `base_odom`, which your answer added.
- `planning.space` is `grid2d` with `mapping.source` `scan`. That works because
  there's a mobile base and a range sensor. Without a range sensor (and with
  no bounded joints to plan in instead), `init` refuses and says why.

In doctor's output, `WARN` lines don't block and `FAIL` lines do (and make
the exit code non-zero). A URDF comment containing `TODO` marks an unmeasured
value. It's a `WARN` on a simulated target and a `FAIL` on a hardware one.

## Docs

[quatern.co/docs/setup](https://quatern.co/docs/setup/#your-own-urdf): your own URDF, and [checking it with doctor](https://quatern.co/docs/setup/#check-it-with-doctor)
