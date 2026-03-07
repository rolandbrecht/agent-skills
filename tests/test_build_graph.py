"""
Tests for ast-code-graph/scripts/build-graph.py

Run: python3 -m pytest tests/test_build_graph.py -v
  or: python3 -m unittest tests/test_build_graph.py -v
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "ast-code-graph" / "scripts" / "build-graph.py"
FIXTURES = ROOT / "tests" / "fixtures"


def run_graph(args):
    """Run build-graph.py and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class TestBuildGraph(unittest.TestCase):
    """Test the graph builder on Python fixture files."""

    def test_produces_valid_json(self):
        stdout, stderr, rc = run_graph([str(FIXTURES)])
        self.assertEqual(rc, 0, f"Script failed: {stderr}")
        graph = json.loads(stdout)
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)

    def test_finds_modules(self):
        stdout, _, _ = run_graph([str(FIXTURES)])
        graph = json.loads(stdout)
        module_nodes = [n for n in graph["nodes"] if n["type"] == "Module"]
        module_files = {n["file"] for n in module_nodes}
        self.assertIn("sample_module.py", module_files)
        self.assertIn("sample_helper.py", module_files)

    def test_finds_classes(self):
        stdout, _, _ = run_graph([str(FIXTURES)])
        graph = json.loads(stdout)
        class_nodes = [n for n in graph["nodes"] if n["type"] == "Class"]
        class_names = {n["name"] for n in class_nodes}
        self.assertIn("DataProcessor", class_names)
        self.assertIn("DataExporter", class_names)
        self.assertIn("CsvExporter", class_names)

    def test_finds_functions(self):
        stdout, _, _ = run_graph([str(FIXTURES)])
        graph = json.loads(stdout)
        func_nodes = [n for n in graph["nodes"] if n["type"] == "Function"]
        func_names = {n["name"] for n in func_nodes}
        self.assertIn("find_files", func_names)
        self.assertIn("main", func_names)
        self.assertIn("load", func_names)
        self.assertIn("process", func_names)

    def test_finds_inheritance(self):
        stdout, _, _ = run_graph([str(FIXTURES)])
        graph = json.loads(stdout)
        extends_edges = [e for e in graph["edges"] if e["type"] == "extends"]
        extends_pairs = {(e["from"], e["to"]) for e in extends_edges}
        # DataExporter extends DataProcessor
        self.assertTrue(
            any("DataExporter" in f and "DataProcessor" == t for f, t in extends_pairs),
            f"Should find DataExporter extends DataProcessor, got: {extends_pairs}",
        )

    def test_finds_imports(self):
        stdout, _, _ = run_graph([str(FIXTURES)])
        graph = json.loads(stdout)
        import_edges = [e for e in graph["edges"] if e["type"] == "imports"]
        imported_modules = {e["to"] for e in import_edges}
        self.assertIn("os", imported_modules)
        self.assertIn("json", imported_modules)
        self.assertIn("sample_module", imported_modules)

    def test_finds_calls(self):
        stdout, _, _ = run_graph([str(FIXTURES)])
        graph = json.loads(stdout)
        call_edges = [e for e in graph["edges"] if e["type"] == "calls"]
        callees = {e["to"] for e in call_edges}
        self.assertIn("find_files", callees)
        self.assertIn("process", callees)
        self.assertIn("load", callees)

    def test_has_line_numbers(self):
        stdout, _, _ = run_graph([str(FIXTURES)])
        graph = json.loads(stdout)
        for node in graph["nodes"]:
            if node["type"] in ("Function", "Class"):
                self.assertIn("line", node, f"Node {node['id']} missing line number")
                self.assertGreater(node["line"], 0)


class TestBuildGraphCallers(unittest.TestCase):
    """Test the --callers flag."""

    def test_callers_finds_results(self):
        stdout, stderr, rc = run_graph([str(FIXTURES), "--callers", "process"])
        self.assertEqual(rc, 0)
        self.assertIn("process", stdout.lower())

    def test_callers_no_results(self):
        stdout, stderr, rc = run_graph([str(FIXTURES), "--callers", "nonexistent_func_xyz"])
        self.assertEqual(rc, 0)
        self.assertIn("no callers found", stdout.lower())


class TestBuildGraphUnused(unittest.TestCase):
    """Test the --unused flag."""

    def test_unused_runs(self):
        stdout, stderr, rc = run_graph([str(FIXTURES), "--unused"])
        self.assertEqual(rc, 0)


class TestBuildGraphCycles(unittest.TestCase):
    """Test the --cycles flag."""

    def test_cycles_runs(self):
        stdout, stderr, rc = run_graph([str(FIXTURES), "--cycles"])
        self.assertEqual(rc, 0)


class TestBuildGraphErrors(unittest.TestCase):
    """Test error handling."""

    def test_nonexistent_directory(self):
        _, stderr, rc = run_graph(["/nonexistent/path/xyz"])
        self.assertNotEqual(rc, 0)

    def test_no_arguments(self):
        _, stderr, rc = run_graph([])
        self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
