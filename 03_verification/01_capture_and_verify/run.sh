#!/usr/bin/env bash
# requires: none
# Record a capture in the simulator, then verify the reference localizer and
# planner against it offline. sim_diffbot has two sources that estimate its
# base (wheel and visual odometry), so the verdict includes a cross-check.
set -euo pipefail

quatern init --robot sim_diffbot --no-sample --yes
quatern capture --robot sim_diffbot --seconds 120 --label room --yes
quatern verify --robot sim_diffbot --label room --goal "Navigate around the island to reach (1.2, 2.0)"
