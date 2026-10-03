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
   - verified on recording turtlebot3_burger.default_2026-10-03_room_v1: qos pass (frames of 2 recorded topic(s) against the TF tree; 1 subscribed topic(s) against the recording's topics; subscribers' reliability against the QoS each publisher offered)
   also: This asks scan_guard to accept best_effort on /scan through ROS 2 QoS overrides; a node that does not declare overrides ignores it, and then the publisher must offer reliability instead.

note: replayed turtlebot3_burger.default_2026-10-03_room_v1 through the configuration: scan_guard asks for reliable delivery on /scan, which is published best effort
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`:

```text
[tool] diagnose_stack {"files": ["launch.log", "scan_guard.yaml"], "robot": "turtlebot3_burger"}
[result] diagnose_stack {"findings":[{"cause":"qos_incompatible","subject":"scan_guard:/scan","severity":"error","summary":"scan_guard and th...
`diagnose_stack` returned one finding. Its fix was verified, with one caveat about whether scan_guard honors it.
[...]
- The replay of recording `turtlebot3_burger.default_2026-10-03_room_v1` agrees. The `/scan` publisher offers best-effort, as sensor drivers usually do.
[...]
**Checks it passed**
- Checked against the configuration: `qos_incompatible` is gone and nothing new appears.
- Replayed on the recording: the QoS check passes. It compared the subscriber's reliability against what each publisher offered, and checked the subscribed topics against the recording.

## Caveat

The fix relies on ROS 2 QoS parameter overrides, and only nodes that declare them honor them. The `launch.log` line says scan_guard uses "the default QoS". That suggests custom code, and I can't tell from the log whether it declares overrides. If it doesn't, the YAML edit is silently ignored and the warning persists.
[...]
```

After `--write`, diagnose again:

```text
wrote: scan_guard.yaml
no root cause found in launch.log, scan_guard.yaml, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
note: replayed turtlebot3_burger.default_2026-10-03_room_v1 through the configuration: frames, topics and QoS agree
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
```

The agent's wording changes from run to run. The diff doesn't. This run the
agent used Quatern's verified fix and didn't call `propose_fix`.

The fix is checked against the configuration and verified on the recording.
Every capture records its ROS context, including the QoS each publisher offers.
Replaying the simulator recording shows `/scan` is published best effort, so the
reliable subscription is the cause, and with the fix scan_guard's subscription
matches it. The recording's lidar mount check passed. The replay can't tell
whether scan_guard honours QoS overrides, so the caveat above still applies.

## What to look for in the run record

Diagnose writes no receipt or stack. For a record, run it with `--json`.
`findings[0].cause` is `qos_incompatible`, `findings[0].subject` is
`scan_guard:/scan`, `findings[0].advice` holds the QoS-overrides caveat, and
`findings[0].fix.verified` is `true`, with `fix.checks` listing *checked
against the configuration* and *verified on recording*. `notes` holds the
recording replay and the mount check, and `written` lists `scan_guard.yaml`
after `--write`.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-you-get): what you get
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
