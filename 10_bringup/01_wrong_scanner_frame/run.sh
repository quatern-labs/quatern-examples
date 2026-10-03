#!/usr/bin/env bash
# requires: none
# A TurtleBot 3 whose config says the lidar is on 'laser', a frame its URDF
# doesn't have (the scanner is on base_scan). Bringup catches it before the
# robot drives, writes the checked fix, and passes on the second run.
set -euo pipefail
cd "$(dirname "$0")"

quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes

# The mistake: the scanner's frame set to the driver's default name.
python3 set_sensor_frame.py turtlebot3_burger scan laser

# bringup exits 1 while anything fails, --write included: it applies the fix
# after reporting what it found.
if quatern bringup --robot turtlebot3_burger; then exit 1; fi
if quatern bringup --robot turtlebot3_burger --write; then exit 1; fi

quatern bringup --robot turtlebot3_burger
