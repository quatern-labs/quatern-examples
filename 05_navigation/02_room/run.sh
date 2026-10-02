#!/usr/bin/env bash
# requires: none
# The room world: a living room with a kitchen island in the middle. The plan
# has to go around the island.
set -euo pipefail

quatern quickstart --robot turtlebot3_waffle --world room --yes
