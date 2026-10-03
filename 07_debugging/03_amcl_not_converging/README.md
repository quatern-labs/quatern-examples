# AMCL never converges

> **Needs sign-in (free) or an Anthropic key.** Run `quatern login` (GitHub,
> free monthly usage) or set `ANTHROPIC_API_KEY`.

> **This is a reproduction.** Every `launch.log`, `nav2_params.yaml` and
> `topics.txt` here was written from scratch for this example, in the shape
> ROS 2 Humble and Nav2's AMCL print and read. None is copied from anyone's
> robot.

## What it shows

"AMCL isn't converging" covers several different failures. In RViz the
particle cloud never collapses and the robot never shows up on the map. In TF
there's no `map -> odom`. This example takes two of the most common causes and
runs both through `quatern diagnose`. **Diagnose solves the first and not the
second.**

**1. AMCL never gets a scan.** The TurtleBot 3 is brought up under the
namespace `tb3_1`, so its lidar publishes `/tb3_1/scan` (`topics.txt`, from
`ros2 topic list -t`). AMCL's `scan_topic` is the absolute `/scan`, which no
namespace changes. AMCL waits forever:

```text
[amcl]: No laser scan received (and thus no pose updates have been published) for 15.000000 seconds.  Verify that data is being published on the /scan topic.
```

**2. AMCL gets scans but has no initial pose** (`no_initial_pose/`). The topic
is right, but `set_initial_pose` is `false` and nobody clicked *2D Pose
Estimate*. AMCL logs the warning below (the typo is AMCL's) every two seconds
and never publishes a pose:

```text
[amcl]: ACML cannot publish a pose or update the transform. Please set the initial pose...
```

For the first, the agent writes the fix and diagnose re-checks it with a
simulator recording. For the second, both diagnose and the agent come back
empty-handed.

## Run it

```sh
quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger --agent
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger --write
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger

# the second cause: no initial pose
cd no_initial_pose
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger --agent
```

`run.sh` runs these on a copy of the files, so `--write` never changes the
repository.

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
   - not replayable on turtlebot3_burger.default_2026-10-03_room_v1: only the ROS 2 stack itself can run this change

note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`:

```text
[tool] diagnose_stack {"files": ["launch.log", "nav2_params.yaml", "topics.txt"], "robot": "turtlebot3_burger"}
[tool] propose_fix {"files": ["launch.log", "nav2_params.yaml", "topics.txt"], "cause": "amcl_no_scans", "subject": "amcl:/scan", "file": "nav2_params.yaml", "set": {"key": ["a...
[result] propose_fix {"accepted":true,"cause":"amcl_no_scans","subject":"amcl:/scan","file":"nav2_params.yaml","diff":"--- a/nav2_params.y...
`diagnose_stack` returned one root cause for this stack, and the fix for it checks out against the configuration. It has not been run on a live ROS 2 graph.

## Root cause: AMCL listens on `/scan`, but the lidar publishes on `/tb3_1/scan`
[...]
The robot is namespaced as `tb3_1`, but the AMCL parameter still holds the default un-namespaced topic.

## Fix

Quatern's reference fix and my own via `propose_fix` give the same diff. `propose_fix` accepted it with `amcl_no_scans` gone and nothing new appearing:

-    scan_topic: /scan
+    scan_topic: /tb3_1/scan
[...]
## Other issues
`diagnose_stack` found nothing else in these files, such as plugin, TF, QoS or clock problems. If other nodes also still use `/scan`, for example the costmap obstacle layers, they would hit the same problem. The tool didn't flag any, so I can't confirm one way or the other.
```

After `--write`, diagnose again:

```text
wrote: nav2_params.yaml
no root cause found in launch.log, nav2_params.yaml, topics.txt, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
```

The second cause, no initial pose:

```text
no root cause found in launch.log, nav2_params.yaml, topics.txt, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)

[tool] diagnose_stack {"files": ["launch.log", "nav2_params.yaml", "topics.txt"], "robot": "turtlebot3_burger"}
[result] diagnose_stack {"findings":[],"read":["launch.log","nav2_params.yaml","topics.txt", ...
`diagnose_stack` returned no findings, so I can't give you a root cause or a fix diff for this stack.
[...]
I haven't written a fix, because `propose_fix` needs a specific cause and subject to check, and I would only be guessing at one. I also can't open the files myself, so I can't quote log lines that `diagnose_stack` didn't surface.
```

## What diagnose got right, and what it didn't

**No scans: solved, checked against the configuration.** The topic list is
what makes this one work. Without `topics.txt`, diagnose still finds the cause
from AMCL's warning, but it doesn't know which topic the lidar publishes on,
so it advises instead of writing a fix. The agent's caution is worth taking:
in a namespaced bringup, any other node with an absolute `/scan` has the same
problem. Here only AMCL's parameters were given, so nothing else could be
checked.

**The recording proves the mount, not the topic.** The `note:` line is the
lidar mount check on the simulator capture. It passes. The topic fix is
labelled *not replayable*, because only a running ROS 2 graph can show AMCL
receiving scans. To confirm on a robot: the warning stops and
`ros2 run tf2_ros tf2_echo map odom` prints a transform.

**No initial pose: not solved.** Diagnose has no detector for "AMCL has scans
but no pose". The "Please set the initial pose" line isn't one it reads, and
`set_initial_pose: false` is valid on its own. The agent can't read files
beyond what `diagnose_stack` returns, so it says it has no finding to check a
fix against and asks for more. On a real robot, the fix is to set
`set_initial_pose: true` with an `initial_pose`, or publish one on
`/initialpose` (RViz's *2D Pose Estimate* does). That wasn't checked here.
Other "not converging" causes, like a wrong `laser_model_type`, odometry noise
(`alpha1`..`alpha5`) or a map that doesn't match the room, aren't detected
either.

## What to look for in the run record

Diagnose writes no receipt or stack. For a record, run it with `--json`.
`findings[0].cause` is `amcl_no_scans`, `findings[0].evidence` includes the
`topics` entry, and `findings[0].fix.verified` is `false`, with `fix.checks`
listing *checked against the configuration* and *not replayable*. For the
no-initial-pose case, `findings` is empty and `read` lists what was read.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-it-reads): what it reads, including `ros2 topic list -t`
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
