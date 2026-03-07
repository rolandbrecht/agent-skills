#!/usr/bin/env python3
"""
build-graph.py — Build a code graph from Python source files.

Usage:
    python3 build-graph.py <directory>                    # JSON graph to stdout
    python3 build-graph.py <directory> --callers <symbol> # Find all callers of a symbol
    python3 build-graph.py <directory> --unused           # Detect unused definitions
    python3 build-graph.py <directory> --depends-on <mod> # Show what depends on a module
    python3 build-graph.py <directory> --cycles           # Detect circular imports

Requires: Python 3.8+ (stdlib only, no external dependencies)
"""

import ast
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


def parse_file(filepath, base_dir):
    """Parse a single Python file and extract nodes and edges."""
    rel_path = os.path.relpath(filepath, base_dir)
    module_id = rel_path.replace(os.sep, "/").removesuffix(".py").replace("/", ".")

    nodes = []
    edges = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        print(f"  Warning: SyntaxError in {rel_path}: {e}", file=sys.stderr)
        return nodes, edges

    # Module node
    nodes.append({
        "id": module_id,
        "type": "Module",
        "file": rel_path,
        "language": "python",
    })

    # Track current class context for method resolution
    class GraphVisitor(ast.NodeVisitor):
        def __init__(self):
            self.class_stack = []
            self.function_stack = []

        def _qualified_name(self, name):
            parts = [module_id]
            parts.extend(self.class_stack)
            parts.append(name)
            return "::".join(parts)

        def _current_scope(self):
            if self.function_stack:
                return self.function_stack[-1]
            if self.class_stack:
                parts = [module_id] + self.class_stack
                return "::".join(parts)
            return module_id

        def visit_ClassDef(self, node):
            qname = self._qualified_name(node.name)
            nodes.append({
                "id": qname,
                "type": "Class",
                "file": rel_path,
                "line": node.lineno,
                "name": node.name,
            })

            # Inheritance edges
            for base in node.bases:
                if isinstance(base, ast.Name):
                    edges.append({
                        "from": qname,
                        "to": base.id,
                        "type": "extends",
                        "file": rel_path,
                        "line": node.lineno,
                    })
                elif isinstance(base, ast.Attribute):
                    edges.append({
                        "from": qname,
                        "to": ast.unparse(base),
                        "type": "extends",
                        "file": rel_path,
                        "line": node.lineno,
                    })

            self.class_stack.append(node.name)
            self.generic_visit(node)
            self.class_stack.pop()

        def visit_FunctionDef(self, node):
            qname = self._qualified_name(node.name)
            nodes.append({
                "id": qname,
                "type": "Function",
                "file": rel_path,
                "line": node.lineno,
                "name": node.name,
                "async": False,
                "params": [arg.arg for arg in node.args.args],
            })

            if self.class_stack:
                class_qname = module_id + "::" + "::".join(self.class_stack)
                edges.append({
                    "from": qname,
                    "to": class_qname,
                    "type": "member-of",
                })

            self.function_stack.append(qname)
            self.generic_visit(node)
            self.function_stack.pop()

        def visit_AsyncFunctionDef(self, node):
            qname = self._qualified_name(node.name)
            nodes.append({
                "id": qname,
                "type": "Function",
                "file": rel_path,
                "line": node.lineno,
                "name": node.name,
                "async": True,
                "params": [arg.arg for arg in node.args.args],
            })

            if self.class_stack:
                class_qname = module_id + "::" + "::".join(self.class_stack)
                edges.append({
                    "from": qname,
                    "to": class_qname,
                    "type": "member-of",
                })

            self.function_stack.append(qname)
            self.generic_visit(node)
            self.function_stack.pop()

        def visit_Import(self, node):
            for alias in node.names:
                edges.append({
                    "from": module_id,
                    "to": alias.name,
                    "type": "imports",
                    "file": rel_path,
                    "line": node.lineno,
                })

        def visit_ImportFrom(self, node):
            if node.module:
                edges.append({
                    "from": module_id,
                    "to": node.module,
                    "type": "imports",
                    "file": rel_path,
                    "line": node.lineno,
                })

        def visit_Call(self, node):
            caller = self._current_scope()
            callee = None

            if isinstance(node.func, ast.Name):
                callee = node.func.id
            elif isinstance(node.func, ast.Attribute):
                callee = node.func.attr

            if callee:
                edges.append({
                    "from": caller,
                    "to": callee,
                    "type": "calls",
                    "file": rel_path,
                    "line": node.lineno,
                })

            self.generic_visit(node)

    visitor = GraphVisitor()
    visitor.visit(tree)

    return nodes, edges


def build_graph(directory):
    """Build the complete code graph for a directory of Python files."""
    all_nodes = []
    all_edges = []

    base_dir = os.path.abspath(directory)

    py_files = sorted(Path(base_dir).rglob("*.py"))

    if not py_files:
        print(f"No .py files found in {directory}", file=sys.stderr)
        return {"nodes": [], "edges": []}

    print(f"Parsing {len(py_files)} Python files...", file=sys.stderr)

    for filepath in py_files:
        # Skip common non-source directories
        parts = filepath.parts
        if any(p in parts for p in ("__pycache__", ".venv", "venv", "node_modules", ".git")):
            continue

        nodes, edges = parse_file(str(filepath), base_dir)
        all_nodes.extend(nodes)
        all_edges.extend(edges)

    print(f"Graph: {len(all_nodes)} nodes, {len(all_edges)} edges", file=sys.stderr)

    return {"nodes": all_nodes, "edges": all_edges}


def find_callers(graph, symbol):
    """Find all edges that call a given symbol."""
    results = []
    for edge in graph["edges"]:
        if edge["type"] == "calls" and edge["to"] == symbol:
            results.append(edge)
    return results


def find_unused(graph):
    """Find defined symbols that are never referenced."""
    # Collect all defined function/class names
    defined = {}
    for node in graph["nodes"]:
        if node["type"] in ("Function", "Class"):
            defined[node["name"]] = node

    # Collect all referenced symbols
    referenced = set()
    for edge in graph["edges"]:
        if edge["type"] in ("calls", "references", "extends"):
            referenced.add(edge["to"])

    # Find unreferenced
    unused = []
    for name, node in defined.items():
        # Skip private/dunder methods and __init__
        if name.startswith("_"):
            continue
        if name not in referenced:
            unused.append(node)

    return unused


def find_dependents(graph, module):
    """Find all modules that import a given module."""
    results = []
    for edge in graph["edges"]:
        if edge["type"] == "imports" and (edge["to"] == module or edge["to"].endswith("." + module)):
            results.append(edge)
    return results


def find_cycles(graph):
    """Detect circular import dependencies."""
    # Build adjacency list of module-level imports
    adj = defaultdict(set)
    for edge in graph["edges"]:
        if edge["type"] == "imports":
            adj[edge["from"]].add(edge["to"])

    visited = set()
    in_stack = set()
    cycles = []

    def dfs(node, path):
        visited.add(node)
        in_stack.add(node)
        path.append(node)

        for neighbor in adj.get(node, []):
            if neighbor in in_stack:
                cycle_start = path.index(neighbor) if neighbor in path else -1
                if cycle_start >= 0:
                    cycles.append(path[cycle_start:] + [neighbor])
            elif neighbor not in visited:
                dfs(neighbor, path)

        path.pop()
        in_stack.discard(node)

    for node in list(adj.keys()):
        if node not in visited:
            dfs(node, [])

    return cycles


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    directory = sys.argv[1]

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    graph = build_graph(directory)

    # Handle query flags
    if "--callers" in sys.argv:
        idx = sys.argv.index("--callers")
        if idx + 1 >= len(sys.argv):
            print("Error: --callers requires a symbol name", file=sys.stderr)
            sys.exit(1)
        symbol = sys.argv[idx + 1]
        results = find_callers(graph, symbol)
        if results:
            print(f"\nCallers of '{symbol}':")
            for r in results:
                loc = f" ({r.get('file', '?')}:{r.get('line', '?')})" if 'file' in r else ""
                print(f"  ← {r['from']}{loc}")
        else:
            print(f"\nNo callers found for '{symbol}'")

    elif "--unused" in sys.argv:
        unused = find_unused(graph)
        if unused:
            print(f"\nPotentially unused symbols ({len(unused)}):")
            for u in sorted(unused, key=lambda x: x["file"]):
                print(f"  {u['type']:10} {u['name']:30} {u['file']}:{u['line']}")
        else:
            print("\nNo unused symbols detected.")

    elif "--depends-on" in sys.argv:
        idx = sys.argv.index("--depends-on")
        if idx + 1 >= len(sys.argv):
            print("Error: --depends-on requires a module name", file=sys.stderr)
            sys.exit(1)
        module = sys.argv[idx + 1]
        results = find_dependents(graph, module)
        if results:
            print(f"\nModules that depend on '{module}':")
            for r in results:
                loc = f" ({r.get('file', '?')}:{r.get('line', '?')})" if 'file' in r else ""
                print(f"  ← {r['from']}{loc}")
        else:
            print(f"\nNo modules depend on '{module}'")

    elif "--cycles" in sys.argv:
        cycles = find_cycles(graph)
        if cycles:
            print(f"\nCircular dependencies detected ({len(cycles)}):")
            for i, cycle in enumerate(cycles, 1):
                print(f"  Cycle {i}: {' → '.join(cycle)}")
        else:
            print("\nNo circular dependencies detected.")

    else:
        # Default: output full graph as JSON
        print(json.dumps(graph, indent=2))


if __name__ == "__main__":
    main()
