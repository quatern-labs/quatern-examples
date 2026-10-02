#!/usr/bin/env bash
# requires: agent
# One request to the agent, no REPL. Needs `quatern login` (free) or your own
# ANTHROPIC_API_KEY. The catalog robot ships a sample capture, so the agent
# has something to verify straight away.
set -euo pipefail

quatern init --robot turtlebot3_burger --yes
out=$(mktemp)
quatern agent "For the robot turtlebot3_burger: list its captures, run the localizer over the newest one, and tell me in two sentences whether that capture is good enough to verify a stack against." | tee "$out"

# `quatern agent` exits 0 even when usage runs out mid-task; treat that as a failure.
if grep -q "usage for this month is used up" "$out"; then
  echo "the agent ran out of usage before finishing" >&2
  exit 1
fi
