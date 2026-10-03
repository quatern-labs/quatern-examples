#!/usr/bin/env bash
# requires: agent
# Reproduction: AMCL gets scans but never localizes, because set_initial_pose
# is off and nothing publishes /initialpose. Diagnose it, have the agent write
# the fix, apply the checked fix, and diagnose again with a simulator recording.
set -euo pipefail

# Work on a copy, so --write never changes the files in this repository.
work=$(mktemp -d)
cp launch.log nav2_params.yaml topics.txt "$work"
cd "$work"

quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes

# diagnose exits 1 when it finds a cause.
if quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger; then exit 1; fi

quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger --agent | tee agent.out
# The agent exits 0 even when usage runs out mid-task; treat that as a failure.
if grep -q "usage for this month is used up" agent.out; then
  echo "the agent ran out of usage before finishing" >&2
  exit 1
fi

if quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger --write; then exit 1; fi
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger
