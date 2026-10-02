#!/usr/bin/env bash
# requires: agent
# Ask the agent, in plain English, to make the robot stop for obstacles using
# its lidar. The tour first gives it a verified stack and a map to work from
# (--no-agent keeps that part on the reference modules, so it costs nothing).
set -euo pipefail

quatern quickstart --robot turtlebot3_burger --world room --no-agent --yes
out=$(mktemp)
quatern agent "For the robot turtlebot3_burger in the simulator: stop for obstacles using the lidar. Check what in the verified stack and the deploy actually uses the scan to stop the robot, deploy the newest ready stack on the sim target, and tell me what would stop it if a box appeared in its path." | tee "$out"

# `quatern agent` exits 0 even when usage runs out mid-task; treat that as a failure.
if grep -q "usage for this month is used up" "$out"; then
  echo "the agent ran out of usage before finishing" >&2
  exit 1
fi
