#!/usr/bin/env bash
# requires: none
# The same capture-and-verify, but the simulator gives wheel odometry a 45%
# distance and heading error. The cross-check against visual odometry has to
# catch it, and verification must refuse to call the stack ready.
set -euo pipefail
cd "$(dirname "$0")"

quatern init --robot sim_diffbot --no-sample --yes
python3 sim_target.py sim_diffbot sim '{"drift": {"wheel_odom": 0.45}}'
quatern capture --robot sim_diffbot --seconds 120 --label room --yes

# verify exits non-zero when the stack is not ready; that is the point here.
if quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"; then
  echo "expected verification to fail with wheel odometry drifting" >&2
  exit 1
fi
