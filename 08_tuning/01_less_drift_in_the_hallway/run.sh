#!/usr/bin/env bash
# requires: none
# Ask for less drift in the hallway, in your own words. Quatern tries one
# localizer parameter at a time on the robot's recordings and keeps what cuts
# drift, with before/after numbers per recording. Nothing is applied.
set -euo pipefail

# A capture in the hallway and a verified stack to start from.
quatern quickstart --robot jetson_rover --world hallway --yes

quatern tune --robot jetson_rover "less drift in the hallway"
