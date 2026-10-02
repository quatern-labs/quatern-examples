#!/usr/bin/env bash
# requires: none
# Verify a stack on a healthy simulated robot, then deploy that same stack on
# a target whose wheel odometry drifts 45%. The gate passes (the stack is
# ready); the watchdog has to stop the run, and the receipt says ABORTED.
set -euo pipefail
cd "$(dirname "$0")"

# A verified stack to deploy: record in the simulator, verify offline.
quatern init --robot sim_diffbot --no-sample --yes
quatern capture --robot sim_diffbot --seconds 120 --label room --yes
quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"
stack=$(quatern stacks --robot sim_diffbot --json | python3 -c 'import json, sys; print(json.load(sys.stdin)["stacks"][0]["stack_id"])')
python3 sim_target.py sim_diffbot sim_drift '{"drift": {"wheel_odom": 0.45}}'

# deploy exits non-zero when the run does not complete.
if quatern deploy --robot sim_diffbot --stack "$stack" --target sim_drift --yes; then
  echo "expected the watchdog to abort the drifting run" >&2
  exit 1
fi
python3 read_receipt.py sim_diffbot
