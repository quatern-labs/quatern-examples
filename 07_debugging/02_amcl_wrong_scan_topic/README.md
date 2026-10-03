# AMCL never localizes: wrong scan topic

> **Needs sign-in (free) or an Anthropic key.** Run `quatern login` (GitHub,
> free monthly usage) or set `ANTHROPIC_API_KEY`.

> **This is a reproduction.** `launch.log`, `nav2_params.yaml` and
> `topics.txt` were written from scratch for this example, in the shape ROS 2
> Humble and Nav2's AMCL print and read. They aren't copied from anyone's
> robot.

## What it shows

A TurtleBot 3 Burger brought up under the namespace `tb3_1`. Its lidar
publishes `/tb3_1/scan` (`topics.txt`, from `ros2 topic list -t`). AMCL's
`scan_topic` is the absolute `/scan`, which the namespace doesn't change. The
particle cloud never converges, no `map -> odom` is published, and AMCL logs:

```text
[amcl]: No laser scan received (and thus no pose updates have been published) for 15.000000 seconds.  Verify that data is being published on the /scan topic.
```

`quatern diagnose` reads the log, the params file and the topic list and names
the cause. Then the agent explains it and writes its own fix, which
`propose_fix` checks. The checked fix is applied with `--write`, and diagnose
runs again, with the robot's URDF and a simulator recording, to show the cause
is gone.

## Run it

```sh
quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger --agent
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger --write
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger
```

`run.sh` runs these on a copy of the files, so `--write` never changes the
repository. `diagnose` exits 1 when it finds a cause and 0 when it doesn't.
Without `topics.txt`, diagnose still finds the cause but gives advice
(`to fix: Point scan_topic at the topic the lidar publishes`) instead of a
diff, because it doesn't know which topic the lidar uses.

## Expected output

Trimmed.

`quatern diagnose`:

```text
1. amcl listens for scans on /scan, which nothing publishes  [amcl_no_scans]
   amcl has had no laser scan since it started: it subscribes to /scan, but the lidar publishes on /tb3_1/scan. With no scans it never updates its pose, never publishes map -> odom, and everything downstream waits for a localization that never comes.
   evidence:
     launch.log:17: [amcl-2] [WARN] [1759401235.302440901] [amcl]: No laser scan received (and thus no pose updates have been published) for 15.000000 seconds.  Verify that data is being published on the /scan topic.
     topics: published LaserScan topics: /tb3_1/scan
     nav2_params.yaml:22: amcl: scan_topic: /scan
   fix (nav2_params.yaml):
     --- a/nav2_params.yaml
     +++ b/nav2_params.yaml
     @@ -19,4 +19,4 @@
            x: 0.0
            y: 0.0
            yaw: 0.0
     -    scan_topic: /scan
     +    scan_topic: /tb3_1/scan
   - checked against the configuration: amcl_no_scans is gone and nothing new appears
   - unverified: recording turtlebot3_burger.default_2026-10-03_room_v1 was made in the simulator and carries no message frames, topic names or QoS to check this against; a rosbag2 of the robot can (--bag)

note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`:

```text
[tool] diagnose_stack {"files": ["launch.log", "nav2_params.yaml", "topics.txt"], "robot": "turtlebot3_burger"}
[tool] propose_fix {"files": ["launch.log", "nav2_params.yaml", "topics.txt"], "cause": "amcl_no_scans", "subject": "amcl:/scan", "file": "nav2_params.yaml", "set": {"key": ["a...
[result] propose_fix {"accepted":true,"cause":"amcl_no_scans","subject":"amcl:/scan","file":"nav2_params.yaml","diff":"--- a/nav2_params.y...
`diagnose_stack` returned one finding for turtlebot3_burger, and the fix for it is not yet tested against a real recording.

## Root cause: AMCL listens on a topic nobody publishes (`amcl_no_scans`, error)
[...]
Quatern's fix is correct, and my own check with `propose_fix` produced the identical diff:
[...]
## How far the fix is checked

- **Checked against the configuration:** the `amcl_no_scans` cause is gone and nothing new appears.
- **Not replayed on a recording:** the only recording, `turtlebot3_burger.default_2026-10-03_room_v1`, comes from the simulator. It has no topic names, frames or QoS to replay against, so the fix is **unverified**. A rosbag2 from the real robot, passed as `--bag`, would let me replay it.
```

After `--write`, diagnose again:

```text
wrote: nav2_params.yaml
no root cause found in launch.log, nav2_params.yaml, topics.txt, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
```

The agent's wording changes from run to run. Its tool calls and the diff
don't.

The fix is checked against the configuration. On the recording it is
`unverified`: a simulator recording carries no message frames, topic names or
QoS to check it against, and a rosbag2 of the robot (`--bag`) can. The
recording's lidar mount check passed.

## What to look for in the run record

Diagnose writes no receipt or stack. For a record, run it with `--json`.
`findings[0].cause` is `amcl_no_scans`, `findings[0].evidence` includes the
`topics` entry, and `findings[0].fix.verified` is `false`, with `fix.checks`
listing *checked against the configuration* and *unverified*. `notes`
holds the mount check and `written` lists the files `--write` changed.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-it-reads): what it reads, including `ros2 topic list -t`
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
