"""Tests for scripts/json-summary.py."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "json-summary.py"


def run(stdin, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin, capture_output=True, text=True,
    )


def match(file, line, text, rule=None):
    m = {"file": file, "range": {"start": {"line": line}}, "text": text}
    if rule:
        m["ruleId"] = rule
    return m


class TestJsonSummary(unittest.TestCase):
    def test_array_input(self):
        data = json.dumps([match("a.js", 0, "foo()"), match("a.js", 4, "foo(1)")])
        result = run(data)
        self.assertEqual(result.returncode, 0)
        self.assertIn("2 matches in 1 file", result.stdout)
        self.assertIn("a.js:1", result.stdout)
        self.assertIn("a.js:5", result.stdout)

    def test_stream_input(self):
        data = "\n".join(json.dumps(match("a.js", 0, "x")) for _ in range(3))
        result = run(data)
        self.assertEqual(result.returncode, 0)
        self.assertIn("3 matches in 1 file", result.stdout)

    def test_singular_plural(self):
        result = run(json.dumps([match("a.js", 0, "x")]))
        self.assertIn("1 match in 1 file", result.stdout)

    def test_empty_input(self):
        for stdin in ("[]", "", "   "):
            result = run(stdin)
            self.assertEqual(result.returncode, 0)
            self.assertIn("0 matches", result.stdout)

    def test_files_only(self):
        result = run(json.dumps([match("a.js", 0, "x")]), "--files-only")
        self.assertNotIn("Matches:", result.stdout)
        self.assertIn("Matches per file:", result.stdout)

    def test_rule_id_shown(self):
        result = run(json.dumps([match("a.js", 0, "x", rule="no-x")]))
        self.assertIn("[no-x]", result.stdout)

    def test_text_truncation(self):
        result = run(json.dumps([match("a.js", 0, "y" * 100)]), "--max-text", "10")
        self.assertIn("y" * 9 + "…", result.stdout)
        self.assertNotIn("y" * 10, result.stdout)

    def test_max_text_validation(self):
        result = run("[]", "--max-text", "0")
        self.assertEqual(result.returncode, 2)
        self.assertIn("10 or greater", result.stderr)

    def test_malformed_json(self):
        result = run("not json at all")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not valid ast-grep JSON", result.stderr)

    def test_scalar_json(self):
        result = run("42")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
