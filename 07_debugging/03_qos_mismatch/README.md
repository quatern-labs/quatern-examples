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

`quatern diagnose` names the cause, the agent writes the fix, and the checked
fix is applied and re-diagnosed with a simulator recording.

**The fix applies when the node accepts QoS overrides.** It sets
`qos_overrides./scan.subscription.reliability` in `scan_guard`'s parameters.
A ROS 2 node reads that parameter only if it creates the subscription with QoS
overriding options (in rclpy,
`qos_overriding_options=QoSOverridingOptions.with_default_policies()`).

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
   - unverified: recording turtlebot3_burger.default_2026-10-03_room_v1 was made in the simulator and carries no message frames, topic names or QoS to check this against; a rosbag2 of the robot can (--bag)
   also: This asks scan_guard to accept best_effort on /scan through ROS 2 QoS overrides; a node that does not declare overrides ignores it, and then the publisher must offer reliability instead.

note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`:

```text
[tool] diagnose_stack {"files": ["launch.log", "scan_guard.yaml"], "robot": "turtlebot3_burger"}
[tool] propose_fix {"files": ["launch.log", "scan_guard.yaml"], "cause": "qos_incompatible", "subject": "scan_guard:/scan", "file": "scan_guard.yaml", "robot": "turtlebot3_burg...
[result] propose_fix {"accepted":true,"cause":"qos_incompatible","subject":"scan_guard:/scan","file":"scan_guard.yaml","diff":"--- a/scan_...
`diagnose_stack` found one root cause. The fix below is checked against the configuration only, not replayed on a recording.
[...]
**My own check with `propose_fix`**
- I set `scan_guard.ros__parameters.qos_overrides./scan.subscription.reliability = best_effort`. It was accepted and produces the identical diff.
- Checks that passed: `qos_incompatible` is gone and nothing new appears.
- It is still **unverified**. The recording `turtlebot3_burger.default_2026-10-03_room_v1` came from the simulator. It has no QoS, topic names or message frames to replay against.

**Caveat: this fix may have no effect**
- ROS 2 only honours `qos_overrides` if the node opted in when it created the subscription. The log says `scan_guard` subscribes "with the default QoS", which hints it may not.
- If `scan_guard` ignores the override, the mismatch will persist after the edit. The log line 7 warning will still appear on the next launch.
- The alternative is to change `scan_guard`'s subscription to a sensor-data QoS profile (best-effort) in its source. I can't check that here, because it is code rather than a config file.
```

After `--write`, diagnose again:

```text
wrote: scan_guard.yaml
no root cause found in launch.log, scan_guard.yaml, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
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
`findings[0].cause` is `qos_incompatible`, `findings[0].subject` is
`scan_guard:/scan`, `findings[0].advice` holds the QoS-overrides caveat, and
`findings[0].fix.verified` is `false`. `written` lists `scan_guard.yaml` after
`--write`.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-you-get): what you get
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
