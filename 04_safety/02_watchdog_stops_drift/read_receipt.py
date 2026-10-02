"""Print the fields of a robot's newest run record (receipt) that explain how
the run ended. Receipts are plain JSON, write-once, under
<data dir>/receipts/<robot>.<instance>/<stack id>/.

    python3 read_receipt.py ROBOT [INSTANCE]
"""

import json
import os
import sys
from pathlib import Path

robot = sys.argv[1]
instance = sys.argv[2] if len(sys.argv) > 2 else "default"
data_dir = Path(os.environ.get("QUATERN_DATA_DIR") or Path.home() / ".quatern").expanduser()
receipts = sorted(
    (data_dir / "receipts" / f"{robot}.{instance}").glob("*/rcpt_*.json"), key=lambda p: p.stat().st_mtime
)
if not receipts:
    sys.exit(f"no receipts for {robot}.{instance} under {data_dir}")
r = json.loads(receipts[-1].read_text())

print(f"receipt:        {r['receipt_id']}")
print(f"target:         {r['target']} (hardware: {r['hardware']}, evidence: {r['evidence_domain']})")
print(f"final_state:    {r['final_state']}")
print(f"acknowledgement: {r['acknowledgement']}")
print("transitions:")
for t in r["transitions"]:
    print(f"  {t['state']:<20} {t.get('reason', '')}")
if r.get("abort"):
    a = r["abort"]
    print("abort:")
    print(f"  check:      {a['check']}")
    print(f"  reason:     {a['reason']}")
    print(f"  detail:     {a['detail']}")
    print(f"  stopped_by: {a['stopped_by']}")
s = r["stop"]
print("stop:")
print(f"  observed: {s['observed']} after {s['observed_after_sec']}s, travel after stop {s['travel_after_stop']} m")
print(f"  bounded travel promised at the gate: {r['bounded_travel']['stopping_distance']} m worst case")
print(f"deviation_max:  {json.dumps(r['deviation_max'])}")
fired = r["live_checks"].get("fired")
if fired:
    print(f"live_checks.fired: {fired['check']} at t={fired['t']}s")
