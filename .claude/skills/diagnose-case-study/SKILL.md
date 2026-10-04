---
name: diagnose-case-study
description: Add or update a 07_debugging case - hand-written ROS 2 logs and params run through quatern diagnose, with the agent's fix and the label for how it was verified.
---

# Diagnose case study (07_debugging)

Builds on `add-example` (header, `expected.txt`, index rows) and
`refresh-example-output` (Quatern build and pin policy). README rules:
`.claude/skills/readme-conventions.md`. Model new cases on
`07_debugging/02_amcl_wrong_scan_topic/`.

## Steps

1. **Write the inputs from scratch**: `launch.log`, `nav2_params.yaml`, and
   whatever else diagnose reads (`topics.txt` from `ros2 topic list -t`, a
   driver yaml, a URDF copy). Shape them like ROS 2 Humble / Nav2 prints and
   reads them. Never copy from anyone's robot, forum post or bug report.

2. **`run.sh`**, `# requires: agent`, in this order:
   ```bash
   work=$(mktemp -d)
   cp launch.log nav2_params.yaml topics.txt "$work"
   cd "$work"

   quatern init --robot turtlebot3_burger --no-sample --yes
   quatern capture --robot turtlebot3_burger --seconds 60 --label room --yes

   # diagnose exits 1 when it finds a cause.
   if quatern diagnose <files> --robot turtlebot3_burger; then exit 1; fi

   quatern diagnose <files> --robot turtlebot3_burger --agent | tee agent.out
   # The agent exits 0 even when usage runs out mid-task; treat that as a failure.
   if grep -q "usage for this month is used up" agent.out; then
     echo "the agent ran out of usage before finishing" >&2
     exit 1
   fi

   if quatern diagnose <files> --robot turtlebot3_burger --write; then exit 1; fi
   quatern diagnose <files> --robot turtlebot3_burger
   ```
   - `--write` also exits 1: it reports, then writes.
   - If the fix may land in the URDF, copy it in first so the installed robot
     isn't changed: `cp "${QUATERN_DATA_DIR:-$HOME/.quatern}/robots/<robot>.urdf" .`
     (see `04_lidar_frame_not_in_urdf`).
   - A variant goes in a subfolder (`no_sensor_frame/`), copied with `cp -R`,
     and runs the same four steps after `cd` into it.

3. **Run it** with a key: `python internal/run_examples.py 07_debugging/<case> --agent --logs logs`.

4. **README** (per conventions), plus:
   - A second callout at the top:
     `> **This is a reproduction.** <files> were written from scratch for this example, in the shape ROS 2 Humble and Nav2 ... print and read. They aren't copied from anyone's robot.`
   - Output blocks for: diagnose, `--agent` (trimmed with `[...]`), and
     "After `--write`, diagnose again". Say the agent's wording and whether
     it calls `propose_fix` change between runs; the diff doesn't.
   - A paragraph stating how the fix was checked, using diagnose's label
     **word for word**: `verified on recording`, or `unverified` followed by
     diagnose's reason exactly as printed (for example
     `unverified: a recording cannot load a pluginlib plugin`). Don't
     paraphrase, soften or add commentary.
   - Run record: diagnose writes no receipt; describe `--json` fields
     (`findings[0].cause`, `findings[0].fix.verified`, `fix.checks`, `notes`,
     `written`).
   - Docs: https://quatern.co/docs/diagnose/ with a real anchor
     (`#what-it-reads`, `#how-the-fix-is-checked`).

5. **`expected.txt`**: the cause label (`[amcl_no_scans]`), the diff `+` line,
   `checked against the configuration: ... is gone and nothing new appears`,
   the verification label, the namespace/replay/mount-check note fragments,
   `[tool] diagnose_stack`, `wrote: <file>`, and
   `no root cause found in <files>`. No recording names (dated).

6. **Concept README** (`07_debugging/README.md`): table row, and keep the
   closing paragraph in sync. It says which cases are
   `verified on recording` and which stay `unverified` and why, and which
   cases use the namespaced robot. Update the top-level README row 7 if it
   lists the cases.

## Files touched

- `07_debugging/NN_case/{run.sh,README.md,expected.txt,launch.log,nav2_params.yaml,...}`
- `07_debugging/README.md` (table and verified/unverified paragraph)
- `README.md` (row 7 lists the cases)

## Done when

- `python internal/run_examples.py 07_debugging/<case> --agent` passes with a
  key. No hook runs these (`requires: agent`); without a key, report it as
  not run instead of claiming it passes.
- The label in README prose, README output, `expected.txt` and the concept
  README paragraph are identical strings, and match the log
  (`grep -n "verified" logs/07_debugging__<case>.log`).
- `git status` shows the case's input files unchanged after the run.
- Each case's README says its inputs were written from scratch.
- `pre-commit run --all-files` passes.

## Gotchas from history

- **Namespaces** (`ddcd0dd` → `c640b75`): the simulator capture is made under
  `/`; diagnose reads it in the robot's namespace (`/tb3_1`) taken from
  `topics.txt`. Before quatern had that, 02's fix was rejected on
  replay and 05 flagged a topic mismatch. Put the namespaced topics in
  `topics.txt`, and expect the note
  `was made under namespace /, but the robot runs under /tb3_1 (its declared topics)`.
- Without `topics.txt` diagnose may only give advice (`to fix: ...`) instead
  of a diff; say so in the README if it's the case.
- Labels change with Quatern (`615c495`: "checked against the configuration,
  unverified on the recording"; `ddcd0dd`: three became
  `verified on recording`, 01 got a new reason). On a refresh, re-copy the
  label from the log; never carry the old wording forward.
- Cases Quatern now handles internally as regression tests get removed
  (`d354898`); renumber and fix cross-references per `add-example`.
- The mount check (`the URDF's base_scan mount gives the sharpest map`) runs
  in every case; its scores are measured values: README only.
