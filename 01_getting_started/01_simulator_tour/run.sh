#!/usr/bin/env bash
# requires: none
# The 2-minute simulator tour: catalog robot -> simulated capture -> verified
# stack -> deploy in the simulator behind the gate and the watchdog.
set -euo pipefail

quatern quickstart --robot turtlebot3_burger --world room --yes
