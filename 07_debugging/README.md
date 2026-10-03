# 07 · Debugging

Case studies of ROS 2 failures that come up again and again on robot forums,
each reproduced and run through `quatern diagnose`. Each one shows the broken
setup, what diagnose found (real output, trimmed), the fix the agent wrote,
and what checking it on a simulator recording does and doesn't prove. Where
diagnose can't solve a case, the README says so and shows that output too.

Every log and params file here was written from scratch for these examples.
None is copied from anyone's robot. Each case says so at the top.

| Example | What it shows | Needs |
| --- | --- | --- |
| [`01_nav2_planner_fails_to_initialize`](01_nav2_planner_fails_to_initialize/) | A Nav2 config from a newer release on Humble: the planner plugin's name doesn't exist, and the whole bringup aborts. Solved. | Sign-in (free) or an Anthropic key |
| [`02_lidar_frame_not_in_urdf`](02_lidar_frame_not_in_urdf/) | The lidar driver stamps `laser`, the URDF has `base_scan`, and the costmap drops every scan. Found, but the checked fix alone isn't enough. The common variant isn't caught. | Sign-in (free) or an Anthropic key |
| [`03_amcl_not_converging`](03_amcl_not_converging/) | AMCL on a namespaced robot listening on the wrong scan topic (solved), and AMCL with no initial pose (not caught). | Sign-in (free) or an Anthropic key |
| [`04_qos_mismatch`](04_qos_mismatch/) | A reliable subscriber and a best-effort lidar: connected, and silent. Solved, if the node accepts QoS overrides. | Sign-in (free) or an Anthropic key |

**What "verified on a recording" means here.** Diagnose replays a fix on a
recording only when a recording can show the cause, which today means a lidar
mounted other than the URDF says. None of these four is that kind, so every
fix here is *checked against the configuration* and labelled *not
replayable*. The recording still runs the mount check, and it passes, which
rules out a rotated lidar. Confirming the fix itself takes a relaunch of the
real stack.
