#!/usr/bin/env bash
# requires: none
# Pick a robot from the catalog, install it, and check it.
set -euo pipefail

quatern init --list
quatern init --robot turtlebot3_waffle --yes
quatern doctor --robot turtlebot3_waffle
