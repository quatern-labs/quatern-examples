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
[result] list_captures [

[tool] get_current_calibration {"robot": "turtlebot3_burger"}
[result] get_current_calibration null

[tool] run_slam_standalone {"capture_id": "turtlebot3_burger.default_2026-10-02_sample_v1", "module": {"files": {}, "reference": "python", ...
[result] run_slam_standalone {

[tool] analyze_verification_signals {"slam_output": {"drift_at_end": 0.2058, "residuals": {}, "sources": {"base": ["wheel_odom"]}, ...
[error] analyze_verification_signals Invalid arguments for analyze_verification_signals: slam_output is missing instance; pass the complete dict run_slam_...

[tool] analyze_verification_signals {"slam_output": {"trajectory": [], "drift_at_end": 0.2058, ...
[result] analyze_verification_signals {
**Verdict:** The capture is clean but only weakly suitable. The streams are healthy (0% dropout on
wheel_odom and scan, 0.17% on imu, low noise), and the localizer reported health "pass" with 0.206
drift at the end, just under the 0.25 limit. However, only wheel_odom ended up estimating the base.
That means no residuals were computed, nothing corroborated the trajectory, and the 30 s run had no
loop closures. [...]
```

The `[error]` line is normal. The tools validate their input, and the agent
fixes the call and retries.

## What to look for

There is no run record here, because nothing was deployed. Check the tool calls
instead:

- `run_slam_standalone` executed the localizer in the sandbox over the
  recorded stream. The agent didn't estimate anything itself.
- The verdict cites numbers the harness computed (`drift_at_end`, dropout),
  and the agent notes that a single source means nothing was cross-checked.
  [03_verification](../../03_verification/) shows what a cross-check adds.

## Docs

- [quatern.co/docs/accounts](https://quatern.co/docs/accounts/#sign-in-with-github): signing in, free usage, your own key
- [quatern.co/docs/commands](https://quatern.co/docs/commands/#quatern-agent): `quatern agent`
