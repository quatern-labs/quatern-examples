# Your first agent task

> **Needs sign-in (free) or an Anthropic key.** Run `quatern login` (GitHub,
> free monthly usage) or set `ANTHROPIC_API_KEY`. Everything else in this repo
> runs without one.

`quatern agent "..."` sends one plain-English request to Quatern's agent
without opening the REPL. The agent answers by calling the same tools the
commands use, and each call streams to your terminal as `[tool] name {args}`
followed by `[result]`, so you can see what it actually did. In this example
the agent reads the sample capture that ships with every catalog robot, runs
the localizer over it in the sandbox, and says whether the capture is good
enough to verify against. The agent can prepare a deploy but can never confirm
one: only a person at the gate can.

## Run it

```sh
quatern init --robot turtlebot3_burger --yes
quatern agent "For the robot turtlebot3_burger: list its captures, run the localizer over the newest one, and tell me in two sentences whether that capture is good enough to verify a stack against."
```

Name the robot in the request. `quatern agent --robot` only applies to the
REPL (`--interactive`). In the REPL you can type the same sentence at the
prompt.

**Usage.** Tool results include whole trajectories, so agent requests use a lot
of tokens. Check `quatern whoami` for what you have left this month.

## Expected output

Real output, trimmed. The agent's wording differs from run to run, and this
time it ignored "two sentences". The tool calls are what to check.

```text
[tool] list_captures {"robot": "turtlebot3_burger"}
[result] list_captures [{"capture_id":"turtlebot3_burger.default_2026-10-03_sample_v1","robot":"turtlebot3_burger","instance":"default","tim...

[tool] get_robot_config {"robot": "turtlebot3_burger"}
[result] get_robot_config {"robot":"turtlebot3_burger.default", ...

[tool] get_module_protocol {}
[result] get_module_protocol {"protocol_version":1, ...

[tool] run_slam_standalone {"capture_id": "turtlebot3_burger.default_2026-10-03_sample_v1", "module": {"files": {}, "reference": "python", "params": {"source_weights": {"wheel_odom": 1...
[result] run_slam_standalone {"result_id":"res_run_slam_standalone_eaab6665", ...

[tool] analyze_verification_signals {"slam_output": "res_run_slam_standalone_eaab6665"}
[result] analyze_verification_signals {"slam_health":"pass","issues":[],"summary":"Localization converged cleanly: base: wheel_odom corroborated by scan; n...

[tool] decide_next_verification_step {"current_state": {"robot": "turtlebot3_burger", "last_slam_result": "res_run_slam_standalone_eaab6665", "last_analysis": {"slam_health": "pass"}, "calibrati...
[result] decide_next_verification_step {"recommended_action":"calibrate","reason":"No valid calibration on record. Actuator response must be measured before...
The newest capture is good enough to verify a localizer against, but it's a short one. It's the only capture, a bundled 30 s sample (`turtlebot3_burger.default_2026-10-03_sample_v1`). Localization health is `pass`, with drift at the end of 0.049, every scan matched, and no constraint violations. Wheel odometry agrees with the scan-to-map pose (residual 0.048) and the IMU yaw agrees with it too (0.023). Both are well under the 0.15 warning limit. The wheel-odom/IMU pair doesn't count as a check, because the odometry already fuses the IMU.

- **Loop closure:** There were 0 loop closures, so this capture can't test loop-closure tuning.
[...]
```

## What to look for

There is no run record here, because nothing was deployed. Check the tool calls
instead:

- `run_slam_standalone` executed the localizer in the sandbox over the
  recorded stream. The agent didn't estimate anything itself.
- `analyze_verification_signals` computed the signals, and the verdict cites
  its numbers (`drift_at_end`, the residuals). The agent didn't judge the
  capture by eye.
- The base was cross-checked from two directions. Wheel odometry estimates
  the base. The lidar's scan-to-map pose checks it (wheel odometry vs lidar,
  residual 0.048), and so does the IMU heading (IMU vs lidar, 0.023). Both
  are under the 0.15 warning limit.
- Wheel odometry vs IMU is not counted. The odometry already fuses the IMU, so
  the two aren't independent. `quatern init` shows these roles: `wheel_odom
  (odometry, estimates base, fuses imu)`, `imu (imu, cross-checks base)`,
  `scan (laserscan, cross-checks base)`.
  [03_verification](../../03_verification/) shows a cross-check catching a
  drifting sensor.

## Docs

- [quatern.co/docs/accounts](https://quatern.co/docs/accounts/#sign-in-with-github): signing in, free usage, your own key
- [quatern.co/docs/commands](https://quatern.co/docs/commands/#quatern-agent): `quatern agent`
- [quatern.co/docs/verification](https://quatern.co/docs/verification/#cross-checks): cross-checks
