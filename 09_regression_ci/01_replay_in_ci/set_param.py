"""Set one parameter in a module's params.json (a number, or any JSON).

python3 set_param.py <params.json> <name> <value>
"""

import json
import sys
from pathlib import Path

path, name, value = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
params = json.loads(path.read_text())
params[name] = json.loads(value)
path.write_text(json.dumps(params, indent=2) + "\n")
print(f"{path}: {name} = {params[name]}")
