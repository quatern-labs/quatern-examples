"""Set one sensor's frame in an installed robot's Quatern config.

python3 set_sensor_frame.py <robot> <sensor> <frame>
"""

import json
import os
import sys
from pathlib import Path

robot, sensor, frame = sys.argv[1:4]
data_dir = Path(os.environ.get("QUATERN_DATA_DIR") or Path.home() / ".quatern")
path = data_dir / "robots" / f"{robot}.quatern.json"
config = json.loads(path.read_text())
(entry,) = [s for s in config["sensors"] if s["name"] == sensor]
entry["frame"] = frame
path.write_text(json.dumps(config, indent=2) + "\n")
print(f"{path.name}: {sensor}.frame = {frame}")
