#!/usr/bin/env bash
# requires: agent
# Reproduction: AMCL on a namespaced TurtleBot 3 that never localizes because
# it listens on /scan while the lidar publishes /tb3_1/scan. Diagnose it, have
# the agent write the fix, apply the checked fix, and diagnose again with a
# simulator recording. Then AMCL with no initial pose, which diagnose does not
# find.
set -euo pipefail

# Work on a copy, so --write never changes the files in this repository.
work=$(mktemp -d)
cp -R . "$work"
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

# The variant: scans arrive, but nobody gave AMCL an initial pose.
cd no_initial_pose
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger
quatern diagnose launch.log nav2_params.yaml topics.txt --robot turtlebot3_burger --agent | tee agent.out
# The agent exits 0 even when usage runs out mid-task; treat that as a failure.
if grep -q "usage for this month is used up" agent.out; then
  echo "the agent ran out of usage before finishing" >&2
  exit 1
fi
