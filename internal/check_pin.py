"""Check that the quatern version pinned in pyproject.toml is on PyPI.

    python internal/check_pin.py     # prints the pinned version; exit 1 if it is not released

CI runs this before installing, so an unpublished pin fails the job instead of
skipping it green.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parent.parent
PYPI_URL = "https://pypi.org/pypi/quatern/json"


def pinned_version(pyproject: dict) -> str:
    for dep in pyproject["project"]["dependencies"]:
        if dep.startswith("quatern"):
            match = re.search(r"==\s*([\w.]+)", dep)
            if match:
                return match.group(1)
    raise SystemExit("pyproject.toml does not pin quatern with ==")


def check(wanted: str, released: set[str]) -> str | None:
    """Return an error message if `wanted` is not among `released`, else None."""
    if wanted in released:
        return None
    return f"quatern=={wanted} is not on PyPI (released: {', '.join(sorted(released)) or 'none'})."


def main() -> int:
    wanted = pinned_version(tomllib.loads((ROOT / "pyproject.toml").read_text()))
    with urllib.request.urlopen(PYPI_URL, timeout=30) as r:  # noqa: S310
        released = set(json.load(r)["releases"])
    error = check(wanted, released)
    if error:
        print(f"::error title=Pinned quatern not installable::{error}")
        return 1
    print(wanted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
