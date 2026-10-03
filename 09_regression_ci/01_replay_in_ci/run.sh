#!/usr/bin/env bash
# requires: none
# Save a robot's recordings as a regression set, replay it against a
# localizer module, and fail when a change makes a metric worse. The same
# `regress run` is what quatern-regress.yml runs in GitHub Actions.
set -euo pipefail

# Work in a scratch directory, as if it were your robot's repository.
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp "$(dirname "$0")/set_param.py" "$work"
cd "$work"

quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes

# Your localizer, as a module directory you commit. Here it's the one
# `quatern tune` writes out.
quatern tune --robot turtlebot3_burger "less drift" --out modules/localizer

# Once, on the machine with the recordings: the set, with its baseline.
quatern regress init regress/room --robot turtlebot3_burger --world "reach (1.2, 2.0)" --localizer modules/localizer

# On every change (this is the CI step).
quatern regress run regress/room --localizer modules/localizer --junit regress.xml

# A change that stops the scan matcher pulling the pose toward the map.
python3 set_param.py modules/localizer/params.json live_map_weight 0
if quatern regress run regress/room --localizer modules/localizer --junit regress.xml; then exit 1; fi
cat regress.xml

# A change that is meant to move the numbers: accept them as the new baseline.
quatern regress baseline regress/room --localizer modules/localizer
quatern regress run regress/room --localizer modules/localizer
