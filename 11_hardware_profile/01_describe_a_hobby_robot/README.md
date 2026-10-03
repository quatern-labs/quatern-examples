# Describe a hobby robot, get its firmware

> **No key needed.**

## What it shows

A two-wheel robot built from hobby parts: an Arduino Uno, an L298N motor
driver, two TT gear motors, LM393 slot sensors and a 2S Li-ion pack. The
parts are described in one sentence, and `quatern init --lowlevel` reads it
into a hardware profile. The values it reads are proposals, so the deploy
gate refuses real hardware until a person confirms the safety fields: motor
rating, battery and driver. After `quatern profile set` confirms them,
`quatern firmware build` derives the motor PWM cap from the motors' rating,
the full battery and the driver's voltage drop, assigns the pins, and
generates the sketch, `WIRING.md`, `PROTOCOL.md` and the host-side bridge.
The gate still refuses until the wheels-up self-test passes on the real
robot, which this example doesn't have.

## Run it

```sh
quatern init --wizard --name tt_rover --kind wheeled --wheels 2 \
  --wheel-diameter 0.065 --track-width 0.14 --sensors odometry,laserscan,imu --lidar yes --camera no \
  --backend ros2 --lowlevel \
  --describe "Arduino Uno, an L298N driver, two TT motors rated 3-6V, LM393 slot sensors with 20-slot discs, 65 mm wheels, 2S 18650 li-ion pack" \
  --yes
quatern profile check --robot tt_rover                       # refused: exits 1

quatern profile set --robot tt_rover motors.rated_v 6
quatern profile set --robot tt_rover power.chemistry li_ion
quatern profile set --robot tt_rover power.cells 2
quatern profile set --robot tt_rover motor_driver.type l298n
quatern profile set --robot tt_rover motor_driver.voltage_drop_v 2.0

quatern profile show --robot tt_rover
quatern firmware build --robot tt_rover --out firmware
cat firmware/tt_rover/WIRING.md
quatern profile check --robot tt_rover                       # still refused: no self-test
```

With [arduino-cli](https://arduino.github.io/arduino-cli/) installed,
`quatern firmware build --robot tt_rover --compile` also compiles the sketch
and ends with `compiled for arduino:avr:uno`. `quatern firmware flash` uploads
it and reads the firmware hash back from the board. Neither is in `run.sh`,
since they need arduino-cli, and flashing needs the board.

## Expected output

Trimmed (the robot summary, repeated cap lines and most of `WIRING.md` are
cut).

```text
  from your description: motor_driver.type = l298n, motor_driver.part = L298N, motor_driver.pin_model = en_in1_in2, motor_driver.channels = 2, motor_driver.voltage_drop_v = 2.0, controller.board = uno, encoders.type = single_channel, encoders.part = LM393 slot-type speed sensor, encoders.edges = both, motors.part = TT gear motor, power.chemistry = li_ion, motors.rated_v = 6.0, motors.count = 2, power.cells = 2, encoders.per_rev = 20, encoders.per_rev_unit = slots, drivetrain.wheel_diameter_m = 0.065
  hardware profile written; next: quatern firmware build --robot tt_rover
hardware profile of tt_rover.default: a hardware deploy is refused:
  - hardware: hardware profile: motors.rated_v = 6.0 was described, not confirmed: `quatern profile set motors.rated_v 6.0` to confirm it
  - hardware: hardware profile: power.chemistry = 'li_ion' was described, not confirmed: `quatern profile set power.chemistry li_ion` to confirm it
  - hardware: hardware profile: power.cells = 2 was described, not confirmed: `quatern profile set power.cells 2` to confirm it
  - hardware: hardware profile: motor_driver.type = 'l298n' was described, not confirmed: `quatern profile set motor_driver.type l298n` to confirm it
  - hardware: hardware profile: motor_driver.voltage_drop_v = 2.0 was described, not confirmed: `quatern profile set motor_driver.voltage_drop_v 2.0` to confirm it
  - hardware: the wheels-up self-test has not passed for this profile: run `quatern selftest --robot tt_rover.default --wheels-up`
  self-test:  not run for this profile
motors.rated_v = 6 (user)
  PWM cap: 6 V motors / (8.40 V full - 2 V driver drop) x 0.95 = 0.891
...
hardware profile of tt_rover.default (firmware mode), profile bdfa4693e9032bb6
  field                        value                                                                                                   source
  mode                         "firmware"                                                                                              user
  motors.rated_v               6                                                                                                       user
  motors.part                  "TT gear motor"                                                                                         described
  motors.count                 2                                                                                                       described
  power.chemistry              "li_ion"                                                                                                user
  power.cells                  2                                                                                                       user
  motor_driver.type            "l298n"                                                                                                 user
  motor_driver.part            "L298N"                                                                                                 described
  motor_driver.pin_model       "en_in1_in2"                                                                                            described
  motor_driver.channels        2                                                                                                       described
  motor_driver.voltage_drop_v  2.0                                                                                                     user
  controller.board             "uno"                                                                                                   described
  encoders.type                "single_channel"                                                                                        described
  encoders.part                "LM393 slot-type speed sensor"                                                                          described
  encoders.edges               "both"                                                                                                  described
  encoders.per_rev             20                                                                                                      described
  encoders.per_rev_unit        "slots"                                                                                                 described
  drivetrain.wheel_diameter_m  0.065                                                                                                   described
  channel_map                  [{"side": "left", "joints": ["wheel_left_joint"]}, {"side": "right", "joints": ["wheel_right_joint"]}]  default
  sensor_map                   ["wheel_left_joint", "wheel_right_joint"]                                                               default
  PWM cap:    0.891 (PWM 227): 6 V motors / (8.40 V full - 2 V driver drop) x 0.95 = 0.891
  firmware:   af813487e99d01d0
  ...
generated firmware/tt_rover (profile bdfa4693e9032bb6, firmware af813487e99d01d0)
  PWM cap: 0.891 = PWM 227/255; 6 V motors / (8.40 V full - 2 V driver drop) x 0.95 = 0.891
  pins:
  controller pin  goes to
  D5              driver ENA (left, PWM capped at 227)
  D4              driver IN1 (left direction)
  D7              driver IN2 (left direction)
  D6              driver ENB (right, PWM capped at 227)
  D8              driver IN3 (right direction)
  D12             driver IN4 (right direction)
  D2              wheel_left_joint sensor signal (INT0)
  D3              wheel_right_joint sensor signal (INT1)
  5V              driver logic 5V input and every sensor VCC
  GND             driver signal GND and every sensor GND (common ground)
  wiring: firmware/tt_rover/WIRING.md
<!-- GENERATED by `quatern firmware build` from the hardware profile of tt_rover (profile bdfa4693e9032bb6, firmware af813487e99d01d0). Do not edit: change the profile and rebuild. -->
# tt_rover wiring (uno + L298N)
...
### Uno → wheel sensors (one per wheel)

| Wheel | Signal (DO) | Interrupt | VCC | GND |
| --- | --- | --- | --- | --- |
| left | D2 | INT0 | Uno 5V | Uno GND |
| right | D3 | INT1 | Uno 5V | Uno GND |
...
* **Active brake:** both inputs HIGH with the enable on, for zero commands, e-stop and the 500 ms silence watchdog. The firmware never coasts to stop. TODO(measure): confirm on the bench that this driver brakes in that state.
* **PWM cap 0.891 (PWM 227):** 6 V motors / (8.40 V full - 2 V driver drop) x 0.95 = 0.891; about 5.70 V at the motors on a full pack. Derived from the profile: a different battery means a different profile and a rebuild.
...
#define QB_PWM_MAX 227
#define QB_CAP_CONSERVATIVE 0
static const uint32_t SILENCE_TIMEOUT_MS = 500;   // contract: robot stops itself
hardware profile of tt_rover.default: a hardware deploy is refused:
  - hardware: the wheels-up self-test has not passed for this profile: run `quatern selftest --robot tt_rover.default --wheels-up`
  self-test:  not run for this profile
```

## What to look for in the profile and the firmware

- **`source`** on every field in `quatern profile show`: `described` (read
  from your sentence), `user` (confirmed with `profile set`), `default`
  (from the URDF; the self-test measures it), and later `measured`. The
  profile is the `lowlevel` section of `~/.quatern/robots/tt_rover.quatern.json`.
- **The PWM cap**: `rated_v / (full_v - voltage_drop_v) x 0.95`, so
  6 / (8.4 - 2.0) x 0.95 = 0.891, or PWM 227 of 255. The motors see about
  5.7 V on a full pack. With an XY-160D (0.1 V drop) instead of an L298N, the
  same motors and pack get 0.687. With the rating or battery unknown, the
  firmware gets a conservative 0.25 and the gate refuses.
- **`quatern_config.h`**: `QB_PWM_MAX 227` and `QB_CAP_CONSERVATIVE 0` come
  from the profile. The 500 ms command-silence watchdog is fixed in the
  sketch, `SILENCE_TIMEOUT_MS = 500`, and a config header that tries to set it
  fails to compile.
- **`profile bdfa4693e9032bb6`** is the hash of the profile. It's in every
  generated file and in the firmware's INFO reply, and the gate refuses if
  the board reports firmware built from a different profile.
- **`WIRING.md`**: the pin table, the power side, common grounds and the free
  pins. The `TODO(measure)` line is a bench check the profile can't answer:
  whether this driver brakes with both inputs high.
- **The gate's refusals**: five unconfirmed safety fields at first, then only
  the wheels-up self-test (`quatern selftest --robot tt_rover --wheels-up`,
  wheels off the ground), which also measures which sensor is which wheel
  and whether a motor runs backwards.

## Docs

[quatern.co/docs/hardware-profiles](https://quatern.co/docs/hardware-profiles/#create-a-profile) · [The motor cap](https://quatern.co/docs/hardware-profiles/#the-motor-cap) · [Generate and flash the firmware](https://quatern.co/docs/hardware-profiles/#generate-and-flash-the-firmware)
