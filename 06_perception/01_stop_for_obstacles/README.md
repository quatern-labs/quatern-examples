# Stop for obstacles using the lidar

> **Needs sign-in (free) or an Anthropic key.** Run `quatern login` (GitHub,
> free monthly usage) or set `ANTHROPIC_API_KEY`.

A TurtleBot 3 Burger with a 360° lidar gets a verified stack and a map from
the simulator tour (run with `--no-agent`, so that part uses no tokens). Then
the request goes to the agent: *stop for obstacles using the lidar*. The agent
works through Quatern's tools. It checks calibration and captures, asks
`deploy_to_robot` what stands between the stack and a run, re-runs the
localizer over the capture, and analyses the result. Quatern's agent can
prepare a deploy but never confirm one: `deploy_to_robot` always stops at the
human gate.

What actually stops the robot for an obstacle is the watchdog. During every
deploy it compares live lidar scans with the verified map, and it aborts on
*"an obstacle in the planned path that the map did not have"* and on *"the
scan disagreeing with the map"*. Both are listed on the gate in
[04_safety/01_the_gate](../../04_safety/01_the_gate/). The agent's job here is
to find that, check the stack and map it relies on, and explain it.

## Run it

```sh
quatern quickstart --robot turtlebot3_burger --world room --no-agent --yes
quatern agent "For the robot turtlebot3_burger in the simulator: stop for obstacles using the lidar. Check what in the verified stack and the deploy actually uses the scan to stop the robot, deploy the newest ready stack on the sim target, and tell me what would stop it if a box appeared in its path."
```

**Usage.** This is a long agent task, and tool results carry whole
trajectories, so it can use a large share of a month's free usage. Check
`quatern whoami` first.

## Expected output

> **Partial.** The only recorded run so far stopped when the account's free
> monthly usage ran out, before the agent's final answer. Below is that real
> transcript, trimmed. It'll be replaced with a complete run once one is
> recorded. The tool sequence is what to check.

```text
I'll start with the preconditions: calibration state and existing captures.
[tool] get_current_calibration {"robot": "turtlebot3_burger"}
[tool] list_captures {"robot": "turtlebot3_burger", "max_age_hours": 168}
Calibration is valid, at 19 seconds old. Next I'll check whether a verified stack is pinned. The deploy tool lists any unmet preconditions and always stops at the human gate.
[tool] deploy_to_robot {"robot": "turtlebot3_burger"}
[tool] run_slam_standalone {"capture_id": "turtlebot3_burger.default_2026-10-02_quickstart_room_v1", "module": {"files": {}, "reference": "python", ...
[tool] analyze_verification_signals {"slam_output": {"drift_at_end": 0.193, "residuals": {}, "sources": {"base": ["wheel_odom"]}, ...
[tool] decide_next_verification_step {"current_state": {"robot": "turtlebot3_burger", ...
[agent] Free usage for this month is used up. Resets November 1. You can also set ANTHROPIC_API_KEY to use your own key.
```

When usage runs out, `quatern agent` prints that line and still exits 0. So
check its output, not just its exit code.

## What to look for

- The agent calls `deploy_to_robot`, and it can't get past the gate. Any run
  that happens needs a person to run `quatern deploy` and answer `y`.
- If you do deploy (`quatern pin <stack id>`, then `quatern deploy --robot
  turtlebot3_burger`), the receipt's `live_checks.series.scan_match` holds the
  scan-against-map evidence the watchdog judged the run by, as
  `[sim time, match fraction, points]` samples. An obstacle abort shows up in
  `abort` and `live_checks.fired`.

## Docs

- [quatern.co/docs/safety](https://quatern.co/docs/safety/#the-watchdog): the watchdog
- [quatern.co/docs/accounts](https://quatern.co/docs/accounts/#free-monthly-usage): free monthly usage
