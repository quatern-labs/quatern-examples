# Lidar frame doesn't match the URDF

> **Needs sign-in (free) or an Anthropic key.** Run `quatern login` (GitHub,
> free monthly usage) or set `ANTHROPIC_API_KEY`.

> **This is a reproduction.** `launch.log`, `rplidar.yaml` and both
> `nav2_params.yaml` files were written from scratch for this example, in the
> shape ROS 2 Humble, Nav2 and `rplidar_ros` print and read. They aren't copied
> from anyone's robot. The URDF is the catalog TurtleBot 3 Burger's.

## What it shows

A TurtleBot 3 Burger whose LDS was swapped for an RPLIDAR. The URDF puts the
lidar on the link `base_scan`, as upstream TurtleBot 3 does. The RPLIDAR driver
stamps its scans `laser` (`frame_id: laser` in `rplidar.yaml`), and the costmap
was told the same:

```yaml
obstacle_layer:
  observation_sources: scan
  scan:
    topic: /scan
    sensor_frame: laser
    data_type: "LaserScan"
```

Nothing crashes. The local costmap drops every scan, so the robot never sees
an obstacle:

```text
[local_costmap.local_costmap]: Message Filter dropping message: frame 'laser' at time 1759398108.112 for reason 'discarding message because the queue is full'
[local_costmap.local_costmap]: The scan observation buffer has not been updated for 10.00 seconds, and it should be updated every 0.20 seconds.
```

`no_sensor_frame/` is the same failure with no `sensor_frame` in the costmap,
which is the more common config: the costmap then takes the frame from each
scan's header.

For each, `quatern diagnose` names the cause, the agent explains it and writes
its own fix, which `propose_fix` checks, and the checked fix is applied with
`--write` and diagnosed again with a simulator recording.

## Run it

```sh
quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes
cp ~/.quatern/robots/turtlebot3_burger.urdf .
cp ~/.quatern/robots/turtlebot3_burger.urdf no_sensor_frame/

quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger
quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger --agent
quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger --write
quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger

cd no_sensor_frame
quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger
quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger --agent
quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger --write
quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger
```

The URDF is copied next to the other files so that a fix to it lands there,
not on the installed robot. `run.sh` runs these on a copy of the folder (and
copies the URDF from `QUATERN_DATA_DIR` when that's set), so `--write` never
changes the repository. `diagnose` exits 1 when it finds a cause and 0 when it
doesn't.

## Expected output

Trimmed.

### With `sensor_frame: laser`

`quatern diagnose`:

```text
1. scans arrive stamped 'laser', a frame TF does not have: every one is dropped  [message_frame_not_in_tf]
   Each message's header says frame 'laser', and nothing publishes a transform for it: the TF tree has base_link, base_scan, caster_back, imu_link, wheel_left, wheel_right. The costmap transforms every observation by its header frame, so each scan is dropped and the robot never sees an obstacle. A costmap setting cannot fix this (sensor_frame only sets the sensor's origin): the messages and TF must agree.
   evidence:
     launch.log:15: [controller_server-3] [INFO] [1759398108.240513087] [local_costmap.local_costmap]: Message Filter dropping message: frame 'laser' at time 1759398108.112 for reason 'discarding message because the queue is full'
     launch.log:10: [rplidar_node-2] [INFO] [1759398102.612003816] [rplidar_node]: current scan mode: Sensitivity, sample rate: 8 Khz, max_distance: 12.0 m, scan frequency:10.0 Hz, frame_id: laser
     robot_state_publisher: links it publishes: base_link, base_scan, imu_link
     nav2_params.yaml:22: local_costmap: obstacle_layer.scan.sensor_frame: laser
   fix (turtlebot3_burger.urdf):
     --- a/turtlebot3_burger.urdf
     +++ b/turtlebot3_burger.urdf
     @@ -96,4 +96,12 @@
          <origin xyz="-0.032 0 0.078" rpy="0 0 0"/>
        </joint>

     +  <!-- Scans arrive stamped 'laser'; it is the same frame as base_scan. If the driver's frame
     +       is turned relative to base_scan (some lidars are mounted 180 deg around), set the rpy. -->
     +  <link name="laser"/>
     +  <joint name="laser_joint" type="fixed">
     +    <parent link="base_scan"/>
     +    <child link="laser"/>
     +    <origin xyz="0 0 0" rpy="0 0 0"/>
     +  </joint>
      </robot>
   - checked against the configuration: message_frame_not_in_tf is gone and nothing new appears
   - verified on recording turtlebot3_burger.default_2026-10-03_room_v1: frames pass (frames of 2 recorded topic(s) against the TF tree; 1 subscribed topic(s) against the recording's topics; subscribers' reliability against the QoS each publisher offered)
   also: Or set the driver's frame_id to 'base_scan' (rplidar_ros and most drivers take a frame_id parameter; pass its params file to diagnose and it writes that change instead), and remove sensor_frame from the costmap or set it to the same frame. Check what the driver stamps with: ros2 topic echo --once <topic> --field header.frame_id

note: replayed turtlebot3_burger.default_2026-10-03_room_v1 through the configuration: frames, topics and QoS agree
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`. The agent proposed changing the driver's
`frame_id` instead, and `propose_fix` accepted it and verified it on the
recording. It also tried the matching `sensor_frame` change on its own, and
`propose_fix` rejected that:

```text
[tool] diagnose_stack {"files": ["launch.log", "nav2_params.yaml", "rplidar.yaml", "turtlebot3_burger.urdf"], "robot": "turtlebot3_burger"}
[tool] propose_fix {"files": ["launch.log", "nav2_params.yaml", "rplidar.yaml", "turtlebot3_burger.urdf"], "cause": "message_frame_not_in_tf", "subject": "laser", "file": "rpli...
[result] propose_fix {"accepted":true,"cause":"message_frame_not_in_tf","subject":"laser","file":"rplidar.yaml","diff":"--- a/rplidar.yaml...
[tool] propose_fix {"files": ["launch.log", "nav2_params.yaml", "rplidar.yaml", "turtlebot3_burger.urdf"], "cause": "message_frame_not_in_tf", "subject": "laser", "file": "nav2...
[result] propose_fix {"accepted":false,"cause":"message_frame_not_in_tf","subject":"laser","reason":"the cause is still there after the fi...
## Fix options

**Option A: Quatern's fix, which adds a `laser` frame to the URDF.** It was verified against the configuration and replayed on the recording.
[...]
**Option B: my fix, which sets the driver's frame to `base_scan`.** I prefer this one. The URDF already has the right frame, so the driver should use it. `propose_fix` accepted it, and it was replayed on the recording. The recorded `laser` frame was read as `base_scan`, and the frame, topic and QoS checks passed.
-    frame_id: laser
+    frame_id: base_scan
[...]
**Change that does not work: setting only `sensor_frame` in `nav2_params.yaml` to `base_scan`.** `propose_fix` rejected it: "the cause is still there after the fix: scans arrive stamped 'laser'". The scan headers still say `laser`, so the scans are still dropped.
[...]
## Caveats
- Apply either A or B, not both. Both are verified on the recording, but this was not run on the live robot. Replaying the recording and checking the configuration are the only checks done.
```

After `--write` (Quatern's URDF fix), diagnose again:

```text
wrote: turtlebot3_burger.urdf
no root cause found in launch.log, nav2_params.yaml, rplidar.yaml, turtlebot3_burger.urdf, recording turtlebot3_burger.default_2026-10-03_room_v1
note: replayed turtlebot3_burger.default_2026-10-03_room_v1 through the configuration: frames, topics and QoS agree
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
```

### With no `sensor_frame` (`no_sensor_frame/`)

`quatern diagnose`. With no costmap setting naming `laser`, the fix is the
driver's `frame_id`:

```text
1. scans arrive stamped 'laser', a frame TF does not have: every one is dropped  [message_frame_not_in_tf]
   [...]
   evidence:
     launch.log:15: [controller_server-3] [INFO] [1759398108.240513087] [local_costmap.local_costmap]: Message Filter dropping message: frame 'laser' at time 1759398108.112 for reason 'discarding message because the queue is full'
     launch.log:10: [rplidar_node-2] [INFO] [1759398102.612003816] [rplidar_node]: current scan mode: Sensitivity, sample rate: 8 Khz, max_distance: 12.0 m, scan frequency:10.0 Hz, frame_id: laser
     robot_state_publisher: links it publishes: base_link, base_scan, imu_link
     rplidar.yaml:6: rplidar_node: frame_id: laser
   fix (rplidar.yaml):
     --- a/rplidar.yaml
     +++ b/rplidar.yaml
     @@ -3,7 +3,7 @@
        ros__parameters:
          serial_port: /dev/ttyUSB0
          serial_baudrate: 115200
     -    frame_id: laser
     +    frame_id: base_scan
          inverted: false
          angle_compensate: true
          scan_mode: Sensitivity
   - checked against the configuration: message_frame_not_in_tf is gone and nothing new appears
   - verified on recording turtlebot3_burger.default_2026-10-03_room_v1: frames pass (frames of 2 recorded topic(s) against the TF tree; 1 subscribed topic(s) against the recording's topics; subscribers' reliability against the QoS each publisher offered; recorded frames 'laser' read as 'base_scan' (the fix changes the driver's frame_id))
   also: The driver then stamps its scans 'base_scan', the URDF's link for the sensor.

note: replayed turtlebot3_burger.default_2026-10-03_room_v1 through the configuration: frames, topics and QoS agree
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`. The agent used Quatern's verified fix:

```text
[tool] diagnose_stack {"files": ["launch.log", "nav2_params.yaml", "rplidar.yaml", "turtlebot3_burger.urdf"], "robot": "turtlebot3_burger"}
[result] diagnose_stack {"findings":[{"cause":"message_frame_not_in_tf","subject":"laser","severity":"error","summary":"scans arrive stamped ...
`diagnose_stack` found one root cause in the four files. Its fix was already verified, so I didn't need to write my own or call `propose_fix`.
[...]
**How it was checked:**
- **Configuration:** `message_frame_not_in_tf` is gone and nothing new appears.
- **Recording replay:** I replayed it on `turtlebot3_burger.default_2026-10-03_room_v1`. Frames, topics and QoS all pass, with the recorded `laser` frame read as `base_scan`.
```

After `--write`, diagnose again:

```text
wrote: rplidar.yaml
no root cause found in launch.log, nav2_params.yaml, rplidar.yaml, turtlebot3_burger.urdf, recording turtlebot3_burger.default_2026-10-03_room_v1
note: replayed turtlebot3_burger.default_2026-10-03_room_v1 through the configuration: frames, topics and QoS agree
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
```

The agent's wording changes from run to run.

Each fix is checked against the configuration and verified on the recording.
Every capture records its ROS context: the frame each topic is stamped with,
the topics and the QoS. Replaying the simulator recording checks the recorded
frames against the fixed TF tree. With the driver fix, the recorded `laser`
frame is read as `base_scan`, the frame the fix makes the driver stamp. The
recording's lidar mount check passed.

## What to look for in the run record

Diagnose writes no receipt or stack. For a record, run it with `--json`.
`findings[0].cause` is `message_frame_not_in_tf` and `findings[0].subject` is
`laser`. `findings[0].fix.file` is the URDF with `sensor_frame` set, and
`rplidar.yaml` without it. `findings[0].fix.verified` is `true`, and
`fix.checks` lists *checked against the configuration* and *verified on
recording*.
`notes` holds the recording replay and the mount check, and `written` lists the
files `--write` changed.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-you-get): what you get
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
