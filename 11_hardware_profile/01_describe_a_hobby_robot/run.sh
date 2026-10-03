#!/usr/bin/env bash
# requires: none
# A two-wheel hobby robot described in plain English: Quatern reads the parts,
# derives the motor PWM cap, and generates the firmware and wiring. The gate
# refuses a hardware deploy until the safety fields are confirmed and the
# wheels-up self-test has passed. Nothing here needs the robot.
set -euo pipefail

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"

quatern init --wizard --name tt_rover --kind wheeled --wheels 2 \
  --wheel-diameter 0.065 --track-width 0.14 --sensors odometry,laserscan,imu --lidar yes --camera no \
  --backend ros2 --lowlevel \
  --describe "Arduino Uno, an L298N driver, two TT motors rated 3-6V, LM393 slot sensors with 20-slot discs, 65 mm wheels, 2S 18650 li-ion pack" \
  --yes

# Described values are proposals: the gate refuses until a person confirms them.
if quatern profile check --robot tt_rover; then exit 1; fi

quatern profile set --robot tt_rover motors.rated_v 6
quatern profile set --robot tt_rover power.chemistry li_ion
quatern profile set --robot tt_rover power.cells 2
quatern profile set --robot tt_rover motor_driver.type l298n
quatern profile set --robot tt_rover motor_driver.voltage_drop_v 2.0

quatern profile show --robot tt_rover
quatern firmware build --robot tt_rover --out firmware
cat firmware/tt_rover/WIRING.md
grep -E "QB_PWM_MAX|QB_CAP_CONSERVATIVE" firmware/tt_rover/quatern_config.h
grep "SILENCE_TIMEOUT_MS = " firmware/tt_rover/tt_rover.ino

# Still refused: the wheels-up self-test hasn't run on the real robot.
if quatern profile check --robot tt_rover; then exit 1; fi
