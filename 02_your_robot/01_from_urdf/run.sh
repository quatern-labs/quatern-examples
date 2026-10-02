#!/usr/bin/env bash
# requires: none
# Set up your own robot from a URDF, then check it. In the REPL this is
# `/init --urdf my_rover.urdf` and then `/doctor`; the same flags work there.
set -euo pipefail
cd "$(dirname "$0")"

quatern init --urdf my_rover.urdf --mobile-base base_link --odometry yes --backend sim2d --yes
quatern doctor --robot my_rover
