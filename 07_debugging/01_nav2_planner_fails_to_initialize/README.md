# Nav2 planner fails to initialize

> **Needs sign-in (free) or an Anthropic key.** Run `quatern login` (GitHub,
> free monthly usage) or set `ANTHROPIC_API_KEY`.

> **This is a reproduction.** `launch.log` and `nav2_params.yaml` were written
> from scratch for this example, in the shape ROS 2 Humble and Nav2 print and
> read. They aren't copied from anyone's robot.

## What it shows

A TurtleBot 3 Burger running Nav2 on ROS 2 Humble. The parameters were adapted
from a tutorial written for a newer Nav2, and `ros2 launch` gets as far as the
planner, then the whole bringup aborts:

```text
[planner_server-2] [FATAL] [...] [planner_server]: Failed to create global planner. Exception: According to the loaded plugin descriptions the class nav2_navfn_planner::NavfnPlanner with base class type nav2_core::GlobalPlanner does not exist. Declared types are  nav2_navfn_planner/NavfnPlanner ...
[lifecycle_manager-3] [ERROR] [...] [lifecycle_manager_navigation]: Failed to bring up all requested nodes. Aborting bringup.
```

The broken line is in `nav2_params.yaml`:

```yaml
planner_server:
  ros__parameters:
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner::NavfnPlanner"
```

Nav2 releases after Humble name plugins with `::`. Humble's pluginlib declares
them with a slash, `nav2_navfn_planner/NavfnPlanner`, as the declared-types
list in the error shows.

`quatern diagnose` reads the log and the params file and names the cause. Then
the agent explains it and writes its own fix, which `propose_fix` checks. The
checked fix is applied with `--write`, and diagnose runs again, with the
robot's URDF and a simulator recording, to show the cause is gone.

## Run it

```sh
quatern init --robot turtlebot3_burger --no-sample --yes
quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes
quatern diagnose launch.log nav2_params.yaml --robot turtlebot3_burger
quatern diagnose launch.log nav2_params.yaml --robot turtlebot3_burger --agent
quatern diagnose launch.log nav2_params.yaml --robot turtlebot3_burger --write
quatern diagnose launch.log nav2_params.yaml --robot turtlebot3_burger
```

`run.sh` runs these on a copy of the files, so `--write` never changes the
repository. `diagnose` exits 1 when it finds a cause and 0 when it doesn't.

## Expected output

Trimmed.

`quatern diagnose`:

```text
1. planner_server cannot load the plugin 'nav2_navfn_planner::NavfnPlanner': no installed plugin has that name  [planner_plugin_unknown]
   The global planner plugin is named 'nav2_navfn_planner::NavfnPlanner', and pluginlib only knows nav2_navfn_planner/NavfnPlanner, nav2_smac_planner/SmacPlanner2D, nav2_smac_planner/SmacPlannerHybrid, nav2_smac_planner/SmacPlannerLattice, nav2_theta_star_planner/ThetaStarPlanner. Names are case-sensitive; 'nav2_navfn_planner/NavfnPlanner' is almost certainly the one meant. planner_server fails to configure, and the lifecycle manager aborts the whole bringup.
   evidence:
     launch.log:16: [planner_server-2] [FATAL] [1759396448.052906114] [planner_server]: Failed to create global planner. Exception: According to the loaded plugin descriptions the class nav2_navfn_planner::NavfnPlanner with base class type nav2_core::GlobalPlanner does not exist. Declared types are  nav2_navfn_planner/NavfnPlanner nav2_smac_planner/SmacPlanner2D nav2_smac_planner/SmacPlannerHybrid nav2_smac_planner/SmacPlannerLattice nav2_theta_star_planner/ThetaStarPlanner
     nav2_params.yaml:9: planner_server.ros__parameters.GridBased.plugin: nav2_navfn_planner::NavfnPlanner
   fix (nav2_params.yaml):
     --- a/nav2_params.yaml
     +++ b/nav2_params.yaml
     @@ -6,7 +6,7 @@
          expected_planner_frequency: 20.0
          planner_plugins: ["GridBased"]
          GridBased:
     -      plugin: "nav2_navfn_planner::NavfnPlanner"
     +      plugin: "nav2_navfn_planner/NavfnPlanner"
            tolerance: 0.5
            use_astar: false
            allow_unknown: true
   - checked against the configuration: planner_plugin_unknown is gone and nothing new appears
   - not replayable on turtlebot3_burger.default_2026-10-03_room_v1: only the ROS 2 stack itself can run this change

note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
nothing written; --write applies the checked fixes
```

`quatern diagnose ... --agent`:

```text
[tool] diagnose_stack {"files": ["launch.log", "nav2_params.yaml"], "robot": "turtlebot3_burger"}
[tool] propose_fix {"files": ["launch.log", "nav2_params.yaml"], "cause": "planner_plugin_unknown", "subject": "nav2_navfn_planner::NavfnPlanner", "file": "nav2_params.yaml", "...
[result] propose_fix {"accepted":true,"cause":"planner_plugin_unknown","subject":"nav2_navfn_planner::NavfnPlanner","file":"nav2_params.ya...
`diagnose_stack` found one root cause. It is a bad plugin name in `nav2_params.yaml`. The fix is checked against the configuration only and has not been run on a real stack.

## Root cause: `planner_plugin_unknown`
The global planner plugin is written as `nav2_navfn_planner::NavfnPlanner`. pluginlib expects a slash between the package and the class, not C++-style `::`. Plugin names are case-sensitive and must match exactly.
[...]
## Fix
This is the diff `diagnose_stack` returned. My own `propose_fix` call, setting `planner_server.ros__parameters.GridBased.plugin`, produced the identical diff and was accepted.
[...]
## What was and wasn't checked
- **Checked against the configuration:** the `planner_plugin_unknown` finding is gone and no new finding appears.
- **Not replayed on a recording:** both tools report `verified: false`. They could not replay this change on `turtlebot3_burger.default_2026-10-03_room_v1`, because only the ROS 2 stack itself can run it.
- **Next step for you:** relaunch Nav2 with the edited file. If the planner configures, the log should no longer show the `[FATAL] Failed to create global planner` line. Other problems that the planner failure was hiding could show up once it starts.
```

After `--write`, diagnose again:

```text
wrote: nav2_params.yaml
no root cause found in launch.log, nav2_params.yaml, ~/.quatern/robots/turtlebot3_burger.urdf (turtlebot3_burger.default's URDF), recording turtlebot3_burger.default_2026-10-03_room_v1
note: mount check passed on turtlebot3_burger.default_2026-10-03_room_v1: the URDF's base_scan mount gives the sharpest map (+0 deg: 36.1, +90 deg: 4.0, +180 deg: 4.0, -90 deg: 4.0)
```

The agent's wording changes from run to run. Its tool calls and the diff
don't.

The fix is checked against the configuration. It was not replayed on the
recording. The recording's lidar mount check passed.

## What to look for in the run record

Diagnose writes no receipt or stack. For a record, run it with `--json`. Each
entry in `findings` has a `cause` (`planner_plugin_unknown`), `evidence` (with
`source` and `line`), and a `fix` with `author` (`reference` for Quatern's
own), `verified` (`false` here) and `checks` (the two lines above). `notes`
holds the mount check and `written` lists the files `--write` changed.

## Docs

- [quatern.co/docs/diagnose](https://quatern.co/docs/diagnose/#what-you-get): what you get
- [How the fix is checked](https://quatern.co/docs/diagnose/#how-the-fix-is-checked)
