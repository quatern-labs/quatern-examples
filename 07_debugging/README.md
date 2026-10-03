# 07 · Debugging

Case studies of ROS 2 failures that come up again and again on robot forums,
each reproduced and run through `quatern diagnose`. Each one shows the broken
setup, what diagnose found (real output, trimmed), the fix the agent wrote,
and the result of diagnosing again with a simulator recording.

Every log and params file here was written from scratch for these examples.
None is copied from anyone's robot. Each case says so at the top.

| Example | What it shows | Needs |
| --- | --- | --- |
| [`01_nav2_planner_fails_to_initialize`](01_nav2_planner_fails_to_initialize/) | A Nav2 config from a newer release on Humble: the planner plugin's name doesn't exist, and the whole bringup aborts. | Sign-in (free) or an Anthropic key |
| [`02_amcl_wrong_scan_topic`](02_amcl_wrong_scan_topic/) | AMCL on a namespaced robot listens on `/scan` while the lidar publishes `/tb3_1/scan`, so it never localizes. | Sign-in (free) or an Anthropic key |
| [`03_qos_mismatch`](03_qos_mismatch/) | A reliable subscriber and a best-effort lidar: connected, and silent. The fix applies when the node accepts QoS overrides. | Sign-in (free) or an Anthropic key |

Each fix is checked against the configuration. None of them is replayed on the
recording; diagnose replays a fix only when the cause is a sensor mount. The
recording's lidar mount check runs in every case and passes.
