#!/usr/bin/env bash
# requires: none
# Deploy a verified stack on a target where one of the robot's sensors is
# switched off. The deploy refuses before anything moves.
set -euo pipefail
cd "$(dirname "$0")"

# A verified stack to deploy: record in the simulator, verify offline.
quatern init --robot sim_diffbot --no-sample --yes
quatern capture --robot sim_diffbot --seconds 120 --label room --yes
quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"
stack=$(quatern stacks --robot sim_diffbot --json | python3 -c 'import json, sys; print(json.load(sys.stdin)["stacks"][0]["stack_id"])')
python3 sim_target.py sim_diffbot sim_no_camera '{"failed_sensors": ["visual_odom"]}'

if quatern deploy --robot sim_diffbot --stack "$stack" --target sim_no_camera --yes; then
  echo "expected the deploy to refuse with a sensor switched off" >&2
  exit 1
fi
