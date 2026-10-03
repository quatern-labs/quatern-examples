# Pick a catalog robot

> **No key needed.**

Quatern ships descriptions of common robots: TurtleBot 3 (Burger and Waffle),
TurtleBot 4, AgileX LIMO and Scout, Clearpath Husky and Jackal, a Unitree Go2,
a Jetson rover kit, UR5e and Franka FR3 arms, Quatern's own C101 test rover,
and two sim-only test robots.
`quatern init --robot <name>` installs one: a primitive-geometry URDF, a
config with simulator, mock, Gazebo and hardware targets using the robot's
standard ROS 2 topics, and a short sample capture. So `quatern verify` works
offline before you've recorded anything. `doctor` then checks it. Planar bases
run in the built-in 2D simulator, and arms run in the mock simulator.

## Run it

```sh
quatern init --list
quatern init --robot turtlebot3_waffle --yes
quatern doctor --robot turtlebot3_waffle
```

In the REPL, `/robots` lists the catalog and `/init --robot turtlebot3_waffle`
installs one.

## Expected output

Trimmed.

```text
Robots in the catalog (quatern init --robot <name>):
    agilex_limo        AgileX's 4 kg multimodal education robot in four-wheel differential mode: lidar, depth camera, IMU.  [built-in sim]
    clearpath_jackal   Clearpath's 17 kg, 2 m/s research UGV with a SICK LMS1xx and IMU (ROS 2, clearpath_common).          [built-in sim]
    franka_fr3         Franka's 7-DOF torque-controlled research arm, 3 kg payload, 855 mm reach; joint encoders.           [mock sim]
    jetson_rover       A typical Jetson Nano/Orin rover kit: skid-steer base, 2D lidar, depth camera, IMU.                  [built-in sim]
    sim_diffbot        A round 32 cm diff-drive robot with lidar, depth camera, visual odometry and IMU; sim only.          [built-in sim]
    turtlebot3_burger  ROBOTIS's small diff-drive classroom robot: LDS 360° lidar, IMU, wheel odometry.                     [built-in sim]
    turtlebot3_waffle  The larger TurtleBot 3: wider diff-drive base, LDS 360° lidar, IMU, wheel odometry.                  [built-in sim]
    turtlebot4         Clearpath/iRobot TurtleBot 4 on a Create 3 base: RPLIDAR A1, IMU, wheel odometry.                    [built-in sim]
    unitree_go2        Unitree's 15 kg quadruped driven as a planar base (walk, sidestep, turn); 4D lidar, IMU.             [built-in sim]
    ur5e               6-DOF collaborative arm, 5 kg payload, 850 mm reach; joint encoders.                                 [mock sim]

  Robot turtlebot3_waffle (instance default): 3 DOF — base/x (unbounded) m, base/y (unbounded) m, base/yaw (unbounded) rad. Sensors: wheel_odom (odometry, estimates base, fuses imu), imu (imu, cross-checks base), scan (laserscan, cross-checks base). Plans in grid2d over group 'base'.
  what you need: For the sim: nothing. For the robot: a TurtleBot 3 Waffle or Waffle Pi running turtlebot3_bringup (robot.launch.py) on ROS 2, publishing /odom, /imu and /scan and accepting /cmd_vel. The camera is not used: the standard bringup does not start it.
  license: Apache-2.0 upstream; this simplified description is a derivative work
  imported the bundled sample capture turtlebot3_waffle.default_2026-10-03_sample_v1: `quatern verify` works offline right away
quatern doctor — turtlebot3_waffle (instance default, target sim)
  ok    config      turtlebot3_waffle.default: 3 DOF, 3 sensor(s), plans in grid2d
  ok    backend     target 'sim' uses the sim2d backend
  ok    streams     wheel_odom (odometry) at 30.0 Hz, last sample 0.03s ago
  ok    streams     imu (imu) at 100.0 Hz, last sample 0.01s ago
  ok    streams     scan (laserscan) at 5.0 Hz, last sample 0.20s ago
  WARN  calibration no fresh valid calibration
ready: no blocking problems
```

## What to look for

- The `what you need` line says what the real robot has to run. The `[built-in
  sim]` / `[mock sim]` tags say where you can try it without hardware.
- `~/.quatern/robots/turtlebot3_waffle.quatern.json` has the targets `sim`,
  `mock`, `gazebo` and `hardware`. `default_target` is `sim`, so nothing
  reaches hardware unless you pick that target by name.
- Choosing a robot? Look at its `Sensors:` line. It says what each sensor does
  for verification. `estimates base` is a source the localizer fuses.
  `cross-checks base` is a lidar or IMU that checks those estimates and is
  never fed to the localizer. `fuses imu` means the odometry already takes its
  heading from the IMU, so that pair isn't counted as a cross-check. On the
  Waffle, the lidar checks the wheel odometry and the IMU. See
  [03_verification](../../03_verification/).

## Docs

[quatern.co/docs/setup](https://quatern.co/docs/setup/#catalog-robots): catalog robots
