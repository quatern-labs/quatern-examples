# 02 · Your robot

A robot is two files: a **URDF** (links, joints, limits, geometry) and a small
`<name>.quatern.json` with what a URDF can't say (targets, sensors, planning).
You never write the JSON by hand. `quatern init` writes it.

| Example | What it shows | Needs |
| --- | --- | --- |
| [`01_from_urdf`](01_from_urdf/) | Set up your own robot from a URDF with `/init` (sample URDF included), then `doctor`. | Nothing |
| [`02_catalog_robot`](02_catalog_robot/) | Pick a robot from the catalog, install it and check it. | Nothing |
