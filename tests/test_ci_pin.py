"""The examples CI must fail, not skip green, when the pinned quatern isn't on PyPI."""

import re
import sys
import unittest
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "internal"))

import check_pin  # noqa: E402

WORKFLOW = (ROOT / ".github/workflows/examples.yml").read_text()
README = (ROOT / "README.md").read_text()
ISSUE_FORM = (ROOT / ".github/ISSUE_TEMPLATE/example-is-broken.yml").read_text()


class PinCheck(unittest.TestCase):
    def test_missing_pin_is_an_error(self):
        self.assertIn("0.3.0", check_pin.check("0.3.0", {"0.2.0"}))

    def test_released_pin_passes(self):
        self.assertIsNone(check_pin.check("0.3.0", {"0.2.0", "0.3.0"}))

    def test_reads_the_real_pin(self):
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
        self.assertRegex(check_pin.pinned_version(pyproject), r"^\d+\.\d+")


class Workflow(unittest.TestCase):
    def test_no_skip_green(self):
        self.assertNotIn("available == 'true'", WORKFLOW)
        self.assertNotIn("Skipping the examples", WORKFLOW)

    def test_installs_the_pin_not_latest(self):
        self.assertNotIn("pip install --upgrade quatern", WORKFLOW)
        self.assertIn('pip install "quatern==', WORKFLOW)

    def test_runs_the_pin_check(self):
        self.assertIn("python internal/check_pin.py", WORKFLOW)


class Docs(unittest.TestCase):
    def test_readme_does_not_claim_latest_or_continuous(self):
        self.assertNotRegex(README, r"continuously tested")
        self.assertNotRegex(README, r"against the latest Quatern Code release")

    def test_readme_states_what_is_tested(self):
        self.assertRegex(README, r"pinned in `pyproject.toml`")
        self.assertRegex(README, r"QUATERN_API_KEY")

    def test_issue_form_label_is_documented(self):
        label = re.search(r'labels: \["([^"]+)"\]', ISSUE_FORM).group(1)
        self.assertIn(f"`{label}`", (ROOT / ".github/labels.md").read_text())


if __name__ == "__main__":
    unittest.main()
