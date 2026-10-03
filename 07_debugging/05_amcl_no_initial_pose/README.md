# AMCL never localizes: no initial pose

> **Needs sign-in (free) or an Anthropic key.** Run `quatern login` (GitHub,
> free monthly usage) or set `ANTHROPIC_API_KEY`.

> **This is a reproduction.** `launch.log`, `nav2_params.yaml` and
> `topics.txt` were written from scratch for this example, in the shape ROS 2
> Humble and Nav2's AMCL print and read. They aren't copied from anyone's
> robot.

## What it shows

AMCL on a TurtleBot 3 Burger has its map and its scans (`scan_topic:
/tb3_1/scan`, which the lidar publishes). But `set_initial_pose` is `false`,
and nobody published a pose on `/initialpose` (RViz's *2D Pose Estimate*).
AMCL publishes no pose and no `map -> odom`, and logs this every two seconds
(the typo is AMCL's):

```text
[amcl]: ACML cannot publish a pose or update the transform. Please set the initial pose...
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

## Expected output

Trimmed.

`quatern diagnose`:

```text
1. amcl has no initial pose, so it never publishes a pose or map -> odom  [amcl_no_initial_pose]
   amcl is running with its map and (by this log) is not short of scans, but nobody told it where the robot starts: set_initial_pose is off and no pose arrived on /initialpose. It waits, publishes no pose and no map -> odom, and everything that needs the map frame waits with it.
   evidence:
     launch.log:12: [amcl-2] [WARN] [1759402013.120665418] [amcl]: ACML cannot publish a pose or update the transform. Please set the initial pose...
     launch.log: repeated 3 times
     nav2_params.yaml:17: amcl: set_initial_pose: false
   fix (nav2_params.yaml):
     --- a/nav2_params.yaml
     +++ b/nav2_params.yaml
     @@ -14,7 +14,7 @@
          max_particles: 2000
          update_min_d: 0.25
          update_min_a: 0.2
     -    set_initial_pose: false
     +    set_initial_pose: true
          initial_pose:
            x: 0.0
            y: 0.0
   - checked against the configuration: amcl_no_initial_pose is gone and nothing new appears
   - unverified: recording turtlebot3_burger.default_2026-10-03_room_v1 was made in the simulator and carries no message frames, topic names or QoS to check this against; a rosbag2 of the robot can (--bag)
   also: The fix starts AMCL at the initial_pose in the file (x 0.0, y 0.0, yaw 0.0): that must be where the robot really is on the map when it starts, or AMCL converges somewhere wrong. Without a fixed start, publish one on /initialpose instead (RViz's 2D Pose Estimate does).

note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`:

```text
[tool] diagnose_stack {"files": ["launch.log", "nav2_params.yaml", "topics.txt"], "robot": "turtlebot3_burger"}
[tool] propose_fix {"files": ["launch.log", "nav2_params.yaml", "topics.txt"], "cause": "amcl_no_initial_pose", "subject": "amcl", "file": "nav2_params.yaml", "set": {"key": ["...
[result] propose_fix {"accepted":true,"cause":"amcl_no_initial_pose","subject":"amcl","file":"nav2_params.yaml","diff":"--- a/nav2_params....
`diagnose_stack` found one root cause. Its fix passes the configuration check but is not replay-verified.
[...]
**Fix**
This is the diff from `diagnose_stack`. I submitted the same change to `propose_fix` as a single parameter set, and it was accepted with an identical diff.
[...]
**What was checked and what was not**
- **Checked:** against the configuration, the `amcl_no_initial_pose` finding is gone and nothing new appears.
- **Not verified:** the replay. The recording `turtlebot3_burger.default_2026-10-03_room_v1` came from the simulator and has no message frames, topic names or QoS to replay against. A rosbag2 of the real robot, passed with `--bag`, would verify it. Until then, don't treat this as a verified fix.

**The pose must match where the robot really starts**
- The fix starts AMCL at x 0.0, y 0.0, yaw 0.0 on the map.
- If the robot does not actually start there, AMCL will converge to the wrong place.
- If the start varies, leave `set_initial_pose: false` and publish the pose on `/initialpose` instead, for example with RViz's "2D Pose Estimate".
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
`findings[0].cause` is `amcl_no_initial_pose`, `findings[0].advice` holds the
note about where the robot starts, and `findings[0].fix.verified` is `false`,
with `fix.checks` listing *checked against the configuration* and
*unverified*. `notes` holds the mount check and `written` lists the files
`--write` changed.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-you-get): what you get
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
