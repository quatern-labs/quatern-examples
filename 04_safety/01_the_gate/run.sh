#!/usr/bin/env bash
# requires: none
# Every deploy goes through the gate: it shows what will run and what will
# stop it, then asks. Without a terminal to ask on, and without --yes, it
# refuses: nothing moves until a person says yes.
set -euo pipefail

# A verified stack to deploy: record in the simulator, verify offline.
quatern init --robot sim_diffbot --no-sample --yes
quatern capture --robot sim_diffbot --seconds 120 --label room --yes
quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"
stack=$(quatern stacks --robot sim_diffbot --json | python3 -c 'import json, sys; print(json.load(sys.stdin)["stacks"][0]["stack_id"])')
quatern pin "$stack"

if quatern deploy --robot sim_diffbot < /dev/null; then
  echo "expected the gate to refuse without a person to answer it" >&2
  exit 1
fi
