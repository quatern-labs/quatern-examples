#!/usr/bin/env bash
# requires: none
# The hallway world: a long corridor with doorways. Plan down it, deploy in
# the simulator, and check the localizer's drift stayed in bounds.
set -euo pipefail

quatern quickstart --robot jetson_rover --world hallway --yes
