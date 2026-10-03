# Bringup catches a wrong scanner frame

> **No key needed.**

## What it shows

A lidar driver's default frame name is often `laser`, while the robot's URDF
mounts the scanner on another link. Here a TurtleBot 3's Quatern config says
its scan comes from `laser`, and its URDF has `base_scan`. Nothing on the
robot would tell you: the costmap would just drop every scan. This example
records the TurtleBot in the simulator, puts `laser` into its config, and runs
`quatern bringup`. The frames check fails and names the URDF's links, and the
fix is a diff to the config that's been checked by running the check again
on the patched file. `--write` applies it, and the second run checks
everything else too (mounts, rates, timestamps, and the ROS frames, QoS,
conventions and timing from the capture) and passes.

## Run it

```sh
quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes
python3 set_sensor_frame.py turtlebot3_burger scan laser     # the mistake
quatern bringup --robot turtlebot3_burger                    # exits 1
quatern bringup --robot turtlebot3_burger --write            # applies the checked fix
quatern bringup --robot turtlebot3_burger                    # passes
```

`set_sensor_frame.py` edits the robot's config in `~/.quatern/robots/` (or
`$QUATERN_DATA_DIR`). On a real robot, run `quatern bringup --robot <name>
--live` instead to probe the robot for a few seconds. Nothing moves.

## Expected output

Trimmed (init and capture are cut, and the `--write` run, which prints the
same report as the first, ends with the `wrote:` line).

```text
turtlebot3_burger.quatern.json: scan.frame = laser
quatern bringup — turtlebot3_burger (files only)
  frames
    ok    imu is mounted on imu_link, a link of the URDF
    FAIL  scan's frame 'laser' is not a link of the URDF
          config: sensors[2].frame = laser
          URDF links: base_link, base_scan, caster_back, imu_link, wheel_left, wheel_right
          fix (turtlebot3_burger.quatern.json):
            --- a/turtlebot3_burger.quatern.json
            +++ b/turtlebot3_burger.quatern.json
            @@ -113,7 +113,7 @@
                 {
                   "name": "scan",
                   "kind": "laserscan",
            -      "frame": "laser",
            +      "frame": "base_scan",
                   "rate_hz": 5,
                   "corroborates": "base"
                 }
          - checked: the frames check passes on the patched files
  note: the config does not load, so only the frames were checked: fix them, then run bringup again

1 failure(s) to fix before driving
nothing written; --write applies the checked fixes
...
wrote: ~/.quatern/robots/turtlebot3_burger.quatern.json (run bringup again to confirm)
quatern bringup — turtlebot3_burger.default (recording turtlebot3_burger.default_2026-10-03_room_v1)
  frames
    ok    imu is mounted on imu_link, a link of the URDF
    ok    scan is mounted on base_scan, a link of the URDF
  extrinsics
    ok    imu's mount is plausible
    ok    scan's mount is plausible
    ok    mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
  rates
    ok    wheel_odom at 29.9 Hz
    ok    imu at 99.7 Hz
    ok    scan at 5.0 Hz
  timestamps
    ok    wheel_odom's stamps are sane
    ok    imu's stamps are sane
    ok    scan's stamps are sane
  ros frames
    ok    message frames: every recorded frame (base_scan, imu_link, odom) is in the TF tree
    ok    sensor transforms: 5 static transform(s) match the URDF
    ok    REP 105: map -> odom -> base_link chain is consistent
  ros qos
    ok    subscribed topics: every subscribed topic has a publisher
    ok    QoS compatibility: every subscriber's QoS is compatible with its publishers'
  ros conventions
    ok    /imu: Imu follows REP 103 and REP 145
    ok    /odom: Odometry follows REP 103
    ok    /scan: LaserScan follows REP 103
    ok    transforms: every static rotation is a unit quaternion (a proper, right-handed rotation)
  ros timing
    ok    monotonic stamps: every stream's stamps only move forward
    ok    stamp vs receive: simulated time: stamps are compared with each other, not with the recorder's wall clock
    ok    clock skew: sensors agree within 11 ms
    ok    TF at message stamps: TF covers the stamps of 2 sensor stream(s)
  ros logs
    ok    /rosout and /diagnostics: no errors logged during the capture

ready to drive: nothing fails
```

## What to look for

- **`(files only)`** on the first run: a frame the URDF lacks stops the
  config from loading, so bringup checks the frames straight from the config
  and URDF files, and runs the rest once they're fixed.
- **The fix**: `sensors[2].frame` in `turtlebot3_burger.quatern.json`, from
  `laser` to `base_scan`, the link the URDF mounts a scanner on.
  `checked: the frames check passes on the patched files` means the patched
  config loads and no other check started failing. Nothing is written
  without `--write`.
- **The exit code**: 1 while anything fails, `--write` included (it reports
  what it found, then applies the fix), and 0 on the passing run, so bringup
  can gate a script.
- **The mount check**: the scans are replayed at the URDF's mount and turned
  90, 180 and 270 degrees. The URDF's yaw gives the sharpest map (36.1 against
  4.0), so the scanner is mounted where the URDF says.
- **The ROS checks** read the capture's ROS context: the frames, topics and
  QoS the simulated robot recorded alongside its sensors.

## Docs

[quatern.co/docs/bringup](https://quatern.co/docs/bringup/#the-checks) · [How a fix is checked](https://quatern.co/docs/bringup/#how-a-fix-is-checked)
