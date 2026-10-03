#!/usr/bin/env bash
# requires: agent
# Reproduction: a TurtleBot 3 whose RPLIDAR driver stamps scans 'laser' while
# the URDF's lidar link is 'base_scan'. Diagnose it, have the agent write the
# fix, apply the checked fix, and diagnose again with a simulator recording.
# Then the same with no sensor_frame in the costmap (no_sensor_frame/).
set -euo pipefail

# Work on a copy, so --write never changes the files in this repository.
work=$(mktemp -d)
cp -R launch.log nav2_params.yaml rplidar.yaml no_sensor_frame "$work"
cd "$work"

quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes

# A copy of the robot's URDF, so a fix to it lands here, not on the installed robot.
urdf="${QUATERN_DATA_DIR:-$HOME/.quatern}/robots/turtlebot3_burger.urdf"
cp "$urdf" .
cp "$urdf" no_sensor_frame/

# diagnose exits 1 when it finds a cause.
if quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger; then exit 1; fi

quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger --agent | tee agent.out
# The agent exits 0 even when usage runs out mid-task; treat that as a failure.
if grep -q "usage for this month is used up" agent.out; then
  echo "the agent ran out of usage before finishing" >&2
  exit 1
fi

if quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger --write; then exit 1; fi
quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger

# The variant: no sensor_frame, so the costmap uses the scan's own 'laser'.
cd no_sensor_frame
if quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger; then exit 1; fi

quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger --agent | tee agent.out
# The agent exits 0 even when usage runs out mid-task; treat that as a failure.
if grep -q "usage for this month is used up" agent.out; then
  echo "the agent ran out of usage before finishing" >&2
  exit 1
fi

if quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger --write; then exit 1; fi
quatern diagnose launch.log nav2_params.yaml rplidar.yaml turtlebot3_burger.urdf --robot turtlebot3_burger
