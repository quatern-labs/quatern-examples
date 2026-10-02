"""Add a simulator target to an installed robot, copied from its `sim` target
with some options changed. This is how a fault is injected: the built-in
simulator (backend `sim2d`) reads `drift` and `failed_sensors` from a target's
options.

    python3 sim_target.py ROBOT NEW_TARGET '{"drift": {"wheel_odom": 0.45}}'

Pass `sim` as NEW_TARGET to change the robot's own sim target in place.
Only edits the robot's .quatern.json in the data directory (QUATERN_DATA_DIR,
default ~/.quatern); nothing else.
"""

import json
import os
import sys
from pathlib import Path

robot, target, patch = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
data_dir = Path(os.environ.get("QUATERN_DATA_DIR") or Path.home() / ".quatern").expanduser()
path = data_dir / "robots" / f"{robot}.quatern.json"
config = json.loads(path.read_text())
spec = json.loads(json.dumps(config["targets"]["sim"]))
spec["options"].update(patch)
config["targets"][target] = spec
path.write_text(json.dumps(config, indent=2) + "\n")
print(f"{path.name}: target {target!r} options {json.dumps(spec['options'], sort_keys=True)}")
