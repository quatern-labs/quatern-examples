# 11 · Hardware profile

For a robot you built from parts: a microcontroller, an H-bridge, gear motors
and wheel sensors. Describe the parts, and Quatern derives the motor PWM cap
from the motors' rating and the battery, assigns the pins, and generates the
base firmware, its wiring sheet and the host-side bridge. Nobody edits the
firmware by hand. The deploy gate refuses real hardware until the safety
fields are confirmed and a wheels-up self-test has passed.

| Example | What it shows | Needs |
| --- | --- | --- |
| [`01_describe_a_hobby_robot`](01_describe_a_hobby_robot/) | A two-wheel Uno + L298N robot described in one sentence: the profile, the gate's refusals, the PWM cap, `WIRING.md` and the firmware build. | Nothing |

Robots that already close their own motor loop (every commercial base in the
catalog) use **interface mode** instead: nothing is generated or flashed, and
the self-test checks `/cmd_vel` against `/odom`.
