---
name: ast-code-graph
description: Use this skill ANY time you need to search for code structure, refactor symbols, analyze impact, find dead code, or trace dependencies. Trigger this for queries like "find all calls to fetch", "rename oldApi to newApi safely", "find unused imports", or "what modules depend on X?". It uses AST parsing to understand code semantically, which is vastly superior to and safer than text-based grep for code modifications.
---

# AST & Code Graph Indexing

## Overview

Text-based search (`grep`, `ripgrep`) finds string matches. AST-based analysis understands **structure** — it knows the difference between a function definition, a function call, a comment, and a string literal.

**Primary tool:** [ast-grep](https://ast-grep.github.io/) (`sg` / `ast-grep`) — a fast, Rust-based CLI for structural code search, lint, and rewriting. It uses tree-sitter for parsing and supports 20+ languages out of the box.

**Core principle:** When the question is about *code structure*, use AST analysis. When the question is about *text content*, use grep.

## When to Use

Use this skill when the task involves:

| Task | Why AST beats grep |
|------|--------------------|
| **Refactoring / renaming** | Grep finds the string in comments and strings too; AST finds only the symbol |
| **Dead code detection** | Grep can't tell if an export is actually imported elsewhere |
| **Dependency tracing** | "What modules does X depend on?" requires understanding `import`/`require` |
| **Impact analysis** | "If I change function X, what breaks?" needs call-graph traversal |
| **Circular dependency detection** | Requires building and analyzing a full import graph |
| **Code migration** | Rewriting deprecated API patterns structurally across a codebase |
| **Custom linting** | Enforcing project-specific patterns that standard linters don't cover |

**Don't use this skill when:**

- Searching for a specific string, error message, or config value → use `grep`
- Finding files by name or extension → use `find`/`fd`
- The codebase is < 5 files and you can read them all → just read them

---

## Phase 1: Search — Find Code by Structure

### ast-grep (recommended — all languages)

`ast-grep` uses **pattern syntax** that looks exactly like the code you're searching for, using `$METAVAR` wildcards to match any AST node.

**Basic pattern search:**

```bash
# Find all calls to console.log
ast-grep -p 'console.log($MSG)' -l js src/

# Find all require() calls
ast-grep -p 'require($MOD)' -l js src/

# Find all async functions
ast-grep -p 'async function $NAME($$$PARAMS) { $$$BODY }' -l js src/

# Find if-else without braces
ast-grep -p 'if ($COND) $STMT' -l js src/
```

**Key metavariable syntax:**

- `$NAME` — matches a **single** AST node (like regex `.`). Example: `foo($ARG)` matches `foo(a)` but NOT `foo(a, b)`.
- `$$$ARGS` — matches **zero or more** nodes (like regex `.*`). Example: `foo($$$ARGS)` matches `foo()`, `foo(a)`, and `foo(a, b)`. **This is the most common pitfall! Default to `$$$` when matching arguments or block bodies unless you strictly want one node.**
- `$_` — anonymous match (when you don't need to reference it later).

**Search with rewrite preview:**

```bash
# Preview replacing var with const
ast-grep -p 'var $NAME = $VALUE' -r 'const $NAME = $VALUE' -l js src/

# Apply interactively (prompts y/n per match)
ast-grep -p 'var $NAME = $VALUE' -r 'const $NAME = $VALUE' -l js --interactive src/
```

See [ast-grep-cheatsheet.md](ast-grep-cheatsheet.md) for the full pattern reference.

---

## Phase 2: Pipeline JSON Output to Scripts

Often, simply printing matches to the terminal isn't enough. For complex analysis, you should export the matches as JSON and process them with a script. This is highly recommended for building graphs, finding dead code, or generating reports.

**Generate and save JSON:**

```bash
# Export all function definitions to a file for secondary analysis
ast-grep -p 'function $NAME($$$PARAMS) { $$$BODY }' -l typescript --json src/ > functions.json
```

Then, write a quick Python or Node.js script to read `functions.json` and extract the specific node text, line numbers, or relationships you need!
*(e.g., parsing the JSON to find functions that have a specific naming convention or parsing out all `import` sources to build a dependency graph).*

---

## Phase 3: Complex Workflows (Step-by-Step)

Here are detailed methodologies for solving complex structural problems:

### Workflow A: Impact Analysis (What breaks if I change X?)

1. **Search**: Find the definition of the target symbol `X` using `ast-grep` and ensure you have its exact name and module path.
2. **Find Direct Callers**: Use `ast-grep` to find all import statements that import `X`, and all function calls to `X()`. Save these results to a JSON file.
3. **Analyze**: If the codebase is large, write a quick script to parse the JSON and list the files/functions that call `X`.
4. **Iterate (Transitive Callers)**: If necessary, repeat the process for the functions that call `X` to build a full call graph. (Alternatively, if this is a Python project, use the bundled `build-graph.py` script as shown in Phase 4).

### Workflow B: Safe Refactoring / Migration

1. **Search**: `ast-grep -p '<pattern>' src/` to find all matches of the old pattern.
2. **Review**: Add `--json` to inspect match details and ensure your pattern isn't capturing unintended code boundaries (e.g. ensure you used `$$$BODY` for blocks, not `$BODY`).
3. **Preview**: Add `-r '<rewrite>'` to see the replacement printed to stdout. Check a few edge cases.
4. **Apply**: Add `--interactive` to selectively apply changes, or remove `--interactive` if you're 100% confident (though you should usually trust but verify).
5. **Verify**: Re-run the search pattern `ast-grep -p '<pattern>'` and ensure it returns 0 matches.

---

## Phase 4: Bundled Graph Builders (Fallback)

While `ast-grep` + JSON pipelines are powerful, this skill includes bundled scripts for common graph building tasks when you need full AST traversal beyond simple pattern matching.

*Use these particularly when checking for dead code or circular dependencies.*

**Python codebases:**

```bash
python3 /home/user/.gemini/antigravity/skills/ast-code-graph/scripts/build-graph.py <directory> [flags]

# Common Flags:
# --callers <symbol>  (find direct and transitive callers)
# --unused            (find dead code / unreferenced symbols)
# --depends-on <mod>  (find reverse dependencies)
# --cycles            (detect circular imports)
```

**JavaScript/TypeScript codebases:**

```bash
# Export a quick symbol list with line numbers
node /home/user/.gemini/antigravity/skills/ast-code-graph/scripts/parse-js.mjs <file> --symbols
```

---

## Quick Reference

| I want to... | ast-grep command |
|---------------|-----------------|
| Find all calls to `foo()` | `ast-grep -p 'foo($$$ARGS)' src/` |
| Find function definitions | `ast-grep -p 'function $NAME($$$P) { $$$B }' src/` |
| Find unused imports | `ast-grep scan --inline-rules '...' src/` |
| Rename `oldFn` → `newFn` | `ast-grep -p 'oldFn($$$A)' -r 'newFn($$$A)' --interactive src/` |
| Convert `var` → `const` | `ast-grep -p 'var $N = $V' -r 'const $N = $V' --interactive src/` |
| JSON output for scripting | `ast-grep -p '<pattern>' --json src/ > out.json` |
| Check change impact | Build graph → find all transitive callers (reverse BFS) |

## Supporting Files

- **[ast-grep-cheatsheet.md](ast-grep-cheatsheet.md)** — Full ast-grep pattern and CLI reference
- **[graph-schema.md](graph-schema.md)** — Node and edge type definitions with ER diagram
- **[query-patterns.md](query-patterns.md)** — Detailed cookbook of query patterns with examples
- **[scripts/parse-js.mjs](scripts/parse-js.mjs)** — Cross-platform Node.js script for JS/TS AST parsing
- **[scripts/build-graph.py](scripts/build-graph.py)** — Python code graph builder
