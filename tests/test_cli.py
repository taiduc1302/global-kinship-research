from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "synthetic-vietnam-korea-case.json"


class CLITests(unittest.TestCase):
    def invoke(self, *args):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run([sys.executable, "-m", "kinship", *map(str, args)], env=env, capture_output=True, text=True, check=False)

    def test_cli_profiles(self):
        p = self.invoke("profiles")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("vietnam", p.stdout)
        self.assertIn("korea", p.stdout)

    def test_cli_audit(self):
        p = self.invoke("audit", CASE)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(json.loads(p.stdout)["ok"])

    def test_cli_plan(self):
        p = self.invoke("plan", "vietnam", "--name", "Nguyễn")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["status"], "draft-not-searched")

    def test_cli_sources(self):
        p = self.invoke("sources", "--region", "china")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertFalse(json.loads(p.stdout)["archive_search_executed"])
        self.assertIn("Shanghai Library", p.stdout)

    def test_cli_local_search(self):
        p = self.invoke("search", CASE, "Nguyen Van An")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('"id": "P1"', p.stdout)

    def test_cli_agent_offline(self):
        p = self.invoke("agent", CASE, "--region", "vietnam", "--question", "What next?")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["mode"], "guided-offline")

    def test_cli_report(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "case-report.md"
            p = self.invoke("report", CASE, "--out", dest)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("### C1", dest.read_text(encoding="utf-8"))

    def test_cli_invalid_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            path.write_text("{", encoding="utf-8")
            p = self.invoke("audit", path)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("Error:", p.stderr)


if __name__ == "__main__":
    unittest.main()
