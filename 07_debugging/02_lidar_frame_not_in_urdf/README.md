# Lidar frame doesn't match the URDF

> **Needs sign-in (free) or an Anthropic key.** Run `quatern login` (GitHub,
> free monthly usage) or set `ANTHROPIC_API_KEY`.

> **This is a reproduction.** `launch.log` and both `nav2_params.yaml` files
> were written from scratch for this example, in the shape ROS 2 Humble, Nav2
> and `rplidar_ros` print and read. They aren't copied from anyone's robot. The
> URDF is the catalog TurtleBot 3 Burger's.

## What it shows

A TurtleBot 3 Burger whose LDS was swapped for an RPLIDAR. The URDF still puts
the lidar on the link `base_scan`, as upstream TurtleBot 3 does. The RPLIDAR
driver stamps its scans `laser`, its default, and the costmap was told the
same:

```yaml
obstacle_layer:
  observation_sources: scan
  scan:
    topic: /scan
    sensor_frame: laser
    data_type: "LaserScan"
```

Nothing crashes. The driver reports `frame_id: laser`, `robot_state_publisher`
loads `base_scan`, and the local costmap quietly drops every scan, so the robot
drives into things:

```text
[local_costmap.local_costmap]: Message Filter dropping message: frame 'laser' at time 1759398108.112 for reason 'discarding message because the queue is full'
[local_costmap.local_costmap]: The scan observation buffer has not been updated for 10.00 seconds, and it should be updated every 0.20 seconds.
```

`quatern diagnose` finds the mismatch, the agent writes a fix, and the checked
fix is applied and re-diagnosed with a simulator recording. Then comes the more
common form of the same bug, with no `sensor_frame` in the costmap. **Diagnose
doesn't catch that one, and the agent doesn't either.** Both results are below.

## Run it

```sh
quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes
quatern diagnose launch.log nav2_params.yaml --robot turtlebot3_burger
quatern diagnose launch.log nav2_params.yaml --robot turtlebot3_burger --agent
quatern diagnose launch.log nav2_params.yaml --robot turtlebot3_burger --write
quatern diagnose launch.log nav2_params.yaml --robot turtlebot3_burger

# the variant: no sensor_frame
quatern diagnose launch.log no_sensor_frame/nav2_params.yaml --robot turtlebot3_burger
quatern diagnose launch.log no_sensor_frame/nav2_params.yaml --robot turtlebot3_burger --agent
```

`run.sh` runs these on a copy of the files, so `--write` never changes the
repository. With `--robot` and no URDF on the command line, diagnose reads the
robot's own URDF.

## Expected output

Trimmed.

`quatern diagnose`:

```text
1. local_costmap expects its sensor in frame 'laser', which the URDF does not have  [sensor_frame_not_in_urdf]
   obstacle_layer.scan.sensor_frame is 'laser', but the robot's URDF has no link of that name; the sensor is mounted on 'base_scan'. Every message is dropped as being in an unknown frame, so the costmap never sees an obstacle.
   evidence:
     nav2_params.yaml:22: local_costmap: obstacle_layer.scan.sensor_frame: laser
     launch.log:15: [controller_server-3] [INFO] [1759398108.240513087] [local_costmap.local_costmap]: Message Filter dropping message: frame 'laser' at time 1759398108.112 for reason 'discarding message because the queue is full'
   fix (nav2_params.yaml):
     --- a/nav2_params.yaml
     +++ b/nav2_params.yaml
     @@ -19,7 +19,7 @@
              observation_sources: scan
              scan:
                topic: /scan
     -          sensor_frame: laser
     +          sensor_frame: base_scan
                data_type: "LaserScan"
                max_obstacle_height: 2.0
                clearing: true
   - checked against the configuration: sensor_frame_not_in_urdf is gone and nothing new appears
   - not replayable on turtlebot3_burger.default_2026-10-03_room_v1: only the ROS 2 stack itself can run this change
   also: If the sensor's driver stamps its messages 'laser', change the driver's frame_id to 'base_scan' too (or instead): the URDF and the messages must agree.

note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`:

```text
[tool] diagnose_stack {"files": ["launch.log", "nav2_params.yaml"], "robot": "turtlebot3_burger"}
[tool] propose_fix {"files": ["launch.log", "nav2_params.yaml"], "cause": "sensor_frame_not_in_urdf", "subject": "local_costmap.obstacle_layer.scan.sensor_frame", "file": "nav2...
[result] propose_fix {"accepted":true,"cause":"sensor_frame_not_in_urdf","subject":"local_costmap.obstacle_layer.scan.sensor_frame","file"...
`diagnose_stack` found one root cause. I checked its fix with `propose_fix`, and the check passed. The fix has not been run on the real ROS 2 stack.
[...]
## Fix

Quatern's reference fix and my own fix, built from a single-parameter `propose_fix` call, produced the same diff:

-          sensor_frame: laser
+          sensor_frame: base_scan
[...]
## Check the driver's frame as well

The URDF and the message headers have to agree. If the LiDAR driver stamps its messages `laser`, the costmap change only moves the mismatch. In that case, set the driver's `frame_id` to `base_scan` as well, or instead. Check the stamped frame with `ros2 topic echo /scan --field header.frame_id`.
```

After `--write`, diagnose again:

```text
wrote: nav2_params.yaml
no root cause found in launch.log, nav2_params.yaml, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
```

The variant, with no `sensor_frame`:

```text
no root cause found in launch.log, no_sensor_frame/nav2_params.yaml, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)

[tool] diagnose_stack {"files": ["launch.log", "no_sensor_frame/nav2_params.yaml"], "robot": "turtlebot3_burger"}
[result] diagnose_stack {"findings":[],"read":["launch.log","no_sensor_frame/nav2_params.yaml", ...
[tool] diagnose_stack {"files": ["no_sensor_frame/launch.log", "no_sensor_frame/nav2_params.yaml"], "robot": "turtlebot3_burger"}
[error] diagnose_stack Invalid arguments for diagnose_stack: no such file: no_sensor_frame/launch.log
`diagnose_stack` returned no findings, so I have no root cause to explain and no diff to give.
[...]
The directory name `no_sensor_frame` suggests the failure is a sensor frame that the URDF lacks, but that is only a guess from the name. Nothing in the tool output supports it. I can't open the log or the YAML myself, and I haven't quoted any log lines, because I haven't seen any. `propose_fix` also needs a specific cause and subject, and I don't have one. I won't write a fix for a problem I haven't identified.
```

## What diagnose got right, and what it didn't

**The finding is right, but the checked fix alone wouldn't fix this robot.** In
Nav2's obstacle layer, `sensor_frame` only sets the frame used for the sensor
origin. The message filter still transforms each scan by the `frame_id` in its
header, which is `laser`, and the TF tree has no `laser`. Diagnose's "checked
against the configuration" means its detectors stop firing. It doesn't mean
the scans stop being dropped. The `also:` line and the agent both point at the
real fix: make the scans and the URDF agree. Either set the driver's
`frame_id` to `base_scan` (and drop `sensor_frame`, or leave it equal), or name
the URDF link after what the driver publishes. Neither of those was run here.

**The recording proves the mount, not the frame name.** The `note:` line
replays the capture's scans with the URDF's `base_scan` mount and three
rotations of it. The URDF's mount is the sharpest by far (36.1 against 4.0),
so the lidar is where the URDF says. A frame-name fix isn't replayable, and
diagnose says so.

**The common variant isn't caught.** Most configs leave `sensor_frame` unset,
so the costmap takes the frame from the message. The detector works from the
`sensor_frame` parameter and doesn't yet read the frame out of a "Message
Filter dropping message" line, so with the same log it finds nothing. The
agent only sees what `diagnose_stack` returns, so it has nothing to check a fix
against. It says so, asks for `ros2 topic list -t` and `view_frames` output,
and doesn't guess. Its one hint, from the folder's name, it flags as a guess.

## What to look for in the run record

Diagnose writes no receipt or stack. For a record, run it with `--json`.
`findings[0].cause` is `sensor_frame_not_in_urdf`, `findings[0].advice` holds
the driver `frame_id` advice, and `findings[0].fix.verified` is `false`, with
`fix.checks` listing *checked against the configuration* and *not replayable*.
The mount check is in `notes`. For the variant, `findings` is empty.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-you-get): what you get
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
