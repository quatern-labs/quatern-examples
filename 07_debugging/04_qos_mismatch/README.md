# QoS mismatch: a subscriber that never gets a scan

> **Needs sign-in (free) or an Anthropic key.** Run `quatern login` (GitHub,
> free monthly usage) or set `ANTHROPIC_API_KEY`.

> **This is a reproduction.** `launch.log` and `scan_guard.yaml` were written
> from scratch for this example, in the shape ROS 2 Humble prints and reads.
> They aren't copied from anyone's robot. `scan_guard` stands in for the small
> node everyone writes. Its source isn't part of the example.

## What it shows

`scan_guard` is a small node that holds the robot still when the lidar sees
something closer than `stop_distance`. It subscribes to `/scan` with the
default QoS, which is reliable. The lidar driver publishes best effort, as
sensor drivers usually do. DDS matches the two, then delivers nothing:

```text
[scan_guard]: New publisher discovered on topic '/scan', offering incompatible QoS. No messages will be sent to it. Last incompatible policy: RELIABILITY_QOS_POLICY
[scan_guard]: no scan for 5.0 s on /scan; holding zero velocity
```

`ros2 topic echo /scan` works, because the CLI adapts its QoS, which makes this
one confusing the first time. `quatern diagnose` names the cause, the agent
writes the fix, and the checked fix is applied and re-diagnosed with a
simulator recording.

## Run it

```sh
quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes
quatern diagnose launch.log scan_guard.yaml --robot turtlebot3_burger
quatern diagnose launch.log scan_guard.yaml --robot turtlebot3_burger --agent
quatern diagnose launch.log scan_guard.yaml --robot turtlebot3_burger --write
quatern diagnose launch.log scan_guard.yaml --robot turtlebot3_burger
```

`run.sh` runs these on a copy of the files, so `--write` never changes the
repository.

## Expected output

Trimmed.

`quatern diagnose`:

```text
1. scan_guard and the publisher of /scan have incompatible QoS (reliability)  [qos_incompatible]
   On /scan the publisher offers less than scan_guard asks for (reliability): DDS connects them, then sends nothing. A sensor driver usually publishes best-effort; a subscriber that insists on reliable never receives a message.
   evidence:
     launch.log:7: [scan_guard-2] [WARN] [1759399530.410881920] [scan_guard]: New publisher discovered on topic '/scan', offering incompatible QoS. No messages will be sent to it. Last incompatible policy: RELIABILITY_QOS_POLICY
     launch.log:6: [scan_guard-2] [INFO] [1759399530.402316657] [scan_guard]: stop_distance 0.25 m, subscribing to /scan with the default QoS (reliable, keep last 10)
   fix (scan_guard.yaml):
     --- a/scan_guard.yaml
     +++ b/scan_guard.yaml
     @@ -6,3 +6,7 @@
          scan_topic: /scan
          stop_distance: 0.25
          cmd_vel_out: /cmd_vel
     +    qos_overrides:
     +      /scan:
     +        subscription:
     +          reliability: best_effort
   - checked against the configuration: qos_incompatible is gone and nothing new appears
   - not replayable on turtlebot3_burger.default_2026-10-03_room_v1: only the ROS 2 stack itself can run this change
   also: This asks scan_guard to accept best_effort on /scan through ROS 2 QoS overrides; a node that does not declare overrides ignores it, and then the publisher must offer reliability instead.

note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`:

```text
[tool] diagnose_stack {"files": ["launch.log", "scan_guard.yaml"], "robot": "turtlebot3_burger"}
[tool] propose_fix {"files": ["launch.log", "scan_guard.yaml"], "cause": "qos_incompatible", "subject": "scan_guard:/scan", "file": "scan_guard.yaml", "robot": "turtlebot3_burg...
[result] propose_fix {"accepted":true,"cause":"qos_incompatible","subject":"scan_guard:/scan","file":"scan_guard.yaml","diff":"--- a/scan_...
`diagnose_stack` returned one finding, a QoS mismatch on `/scan`. The fix has only been checked against the configuration. It has not been run on a live ROS 2 graph.
[...]
**Fix**

Quatern's reference fix and my own fix, checked with `propose_fix`, are the same diff. I set the key path `scan_guard.ros__parameters.qos_overrides./scan.subscription.reliability` to `best_effort`.
[...]
**Caveat**
- `qos_overrides` only works if `scan_guard` declares QoS overrides when it creates its subscription. Otherwise the node ignores the parameter and the warning stays in the log.
- In that case, make the `/scan` publisher offer reliable QoS instead, or change the subscription QoS in `scan_guard`'s code to sensor-data (best-effort).
- To confirm, relaunch and check that the line 7 warning is gone and `scan_guard` is receiving `/scan` messages.
```

After `--write`, diagnose again:

```text
wrote: scan_guard.yaml
no root cause found in launch.log, scan_guard.yaml, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
```

## What diagnose got right, and what it didn't

**The cause: right.** The fix is a parameter, and **whether it works depends on
code that isn't here.** A ROS 2 node reads `qos_overrides.<topic>.subscription.*`
only if it creates the subscription with QoS overriding options (in rclpy,
`qos_overriding_options=QoSOverridingOptions.with_default_policies()`). Most
hand-written nodes don't, and then the parameter does nothing. Both diagnose's
`also:` line and the agent's caveat say this. If you own the node, the
simplest fix is in the code: subscribe with `qos_profile_sensor_data`.
Diagnose reads parameters, logs, URDFs and TF trees, not source code, so it
can't write that change. That wasn't run here.

**The recording proves nothing about QoS.** The `note:` line is the lidar
mount check, and it passes. The QoS change is labelled *not replayable*. To
confirm on a robot, the incompatible-QoS warning is gone after relaunch, and
`ros2 topic info /scan --verbose` shows both endpoints as `BEST_EFFORT`.

## What to look for in the run record

Diagnose writes no receipt or stack. For a record, run it with `--json`.
`findings[0].cause` is `qos_incompatible`, `findings[0].subject` is
`scan_guard:/scan`, `findings[0].advice` holds the QoS-overrides caveat, and
`findings[0].fix.verified` is `false`. `written` lists `scan_guard.yaml` after
`--write`.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-you-get): what you get
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
