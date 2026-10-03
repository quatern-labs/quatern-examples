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
the cause. Then the agent explains it, and can write its own fix for
`propose_fix` to check. The checked fix is applied with `--write`, and diagnose
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
   - verified on recording turtlebot3_burger.default_2026-10-03_room_v1: topics pass (frames of 2 recorded topic(s) against the TF tree; 1 subscribed topic(s) against the recording's topics; subscribers' reliability against the QoS each publisher offered; the recording was made under namespace /, but the robot runs under /tb3_1 (its declared topics): its topics are read in /tb3_1 (/imu as /tb3_1/imu, /odom as /tb3_1/odom, /robot_description as /tb3_1/robot_description, /scan as /tb3_1/scan))

note: recording turtlebot3_burger.default_2026-10-03_room_v1 was made under namespace /, but the robot runs under /tb3_1 (its declared topics): its topics are read in /tb3_1 (/imu as /tb3_1/imu, /odom as /tb3_1/odom, /robot_description as /tb3_1/robot_description, /scan as /tb3_1/scan)
note: replayed turtlebot3_burger.default_2026-10-03_room_v1 through the configuration: amcl subscribes to /scan (scan_topic), which the recording does not have (it has /tb3_1/scan)
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`:

```text
[tool] diagnose_stack {"files": ["launch.log", "nav2_params.yaml", "topics.txt"], "robot": "turtlebot3_burger"}
[result] diagnose_stack {"findings":[{"cause":"amcl_no_scans","subject":"amcl:/scan","severity":"error","summary":"amcl listens for scans on ...
`diagnose_stack` returned one root cause. I found nothing it missed, and Quatern's fix was correct, so I didn't write my own or call `propose_fix`.

## Root cause: AMCL listens on `/scan`, but the lidar publishes on `/tb3_1/scan`
[...]
**How it was checked**
- Checked against the configuration: the `amcl_no_scans` finding is gone and no new finding appears.
- Replayed on the recording `turtlebot3_burger.default_2026-10-03_room_v1`: the topics, frames and QoS checks pass.
- The recording was made under namespace `/`, but the robot declares `/tb3_1` topics. The tool read the recording's topics in `/tb3_1` (`/scan` as `/tb3_1/scan`, `/odom` as `/tb3_1/odom`, and so on).
- The mount check passed. The URDF's `base_scan` orientation gives the sharpest map at +0° (score 36.1, against 4.0 at the other three angles), so the lidar mount matches the URDF.

I pointed the parameter at `/tb3_1/scan` because that is the topic the robot declares. I did not pick it only because the recording had it.
[...]
```

After `--write`, diagnose again:

```text
wrote: nav2_params.yaml
no root cause found in launch.log, nav2_params.yaml, topics.txt, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
note: recording turtlebot3_burger.default_2026-10-03_room_v1 was made under namespace /, but the robot runs under /tb3_1 (its declared topics): its topics are read in /tb3_1 (/imu as /tb3_1/imu, /odom as /tb3_1/odom, /robot_description as /tb3_1/robot_description, /scan as /tb3_1/scan)
note: replayed turtlebot3_burger.default_2026-10-03_room_v1 through the configuration: frames, topics and QoS agree
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
```

The agent's wording changes from run to run, and so does whether it calls
`propose_fix` to check a fix of its own. The diff doesn't change.

The fix is checked against the configuration and verified on the recording.
The simulator recording was made without a namespace, and the robot declares
its topics under `/tb3_1` (`topics.txt`). Diagnose reads the recording's
topics in the robot's namespace, so the recorded `/scan` is `/tb3_1/scan`.
The declared topics win: the recording doesn't pull the fix back to `/scan`.
Before the fix, the replay shows AMCL subscribed to a topic the recording
doesn't have. After it, frames, topics and QoS agree. The recording's lidar
mount check passed.

## What to look for in the run record

Diagnose writes no receipt or stack. For a record, run it with `--json`.
`findings[0].cause` is `amcl_no_scans`, `findings[0].evidence` includes the
`topics` entry, and `findings[0].fix.verified` is `true`, with `fix.checks`
listing *checked against the configuration* and *verified on recording*.
`notes` holds the namespace mapping, the recording replay and the mount check,
and `written` lists the files `--write` changed.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-it-reads): what it reads, including `ros2 topic list -t`
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
