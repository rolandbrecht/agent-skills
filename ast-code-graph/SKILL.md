---
name: ast-code-graph
description: Use AST parsing and code graph indexing for deep codebase analysis — refactoring, dead-code detection, dependency tracing, impact analysis, and safe symbol renaming
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

## Phase 1: Search — Find Code by Structure

### ast-grep (recommended — all languages)

ast-grep uses **pattern syntax** that looks like the code you're searching for, with `$METAVAR` wildcards that match any AST node.

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
- `$NAME` — matches a single AST node (like regex `.`)
- `$$$ARGS` — matches zero or more nodes (like regex `.*`)
- `$_` — anonymous match (don't need to reference it)

**Search with rewrite preview:**
```bash
# Preview replacing var with const
ast-grep -p 'var $NAME = $VALUE' -r 'const $NAME = $VALUE' -l js src/

# Apply interactively (prompts y/n per match)
ast-grep -p 'var $NAME = $VALUE' -r 'const $NAME = $VALUE' -l js --interactive src/
```

See [ast-grep-cheatsheet.md](ast-grep-cheatsheet.md) for the full pattern reference.

### Fallback: Language-Specific Parsers

When you need full AST traversal beyond pattern matching:

**JavaScript/TypeScript — bundled helper:**
```bash
# Export list with line numbers
node /home/user/.gemini/antigravity/skills/ast-code-graph/scripts/parse-js.mjs <file> --symbols

# Full JSON AST
node /home/user/.gemini/antigravity/skills/ast-code-graph/scripts/parse-js.mjs <file>
```

**Python — bundled graph builder:**
```bash
python3 /home/user/.gemini/antigravity/skills/ast-code-graph/scripts/build-graph.py <directory> [flags]
```

## Phase 2: Analyze — Use Rules for Complex Queries

ast-grep supports **YAML rule configurations** for combining multiple conditions with logical operators.

### Inline rules (ad-hoc, no file needed)

```bash
ast-grep scan --inline-rules '
id: find-unsafe-eval
language: JavaScript
rule:
  pattern: eval($CODE)
' src/
```

### Rule file (reusable)

Save as `rules/no-console-log.yml`:
```yaml
id: no-console-log
language: JavaScript
severity: warning
message: Remove console.log before committing
rule:
  pattern: console.log($$$ARGS)
```

Run:
```bash
ast-grep scan --rule rules/no-console-log.yml src/
```

### Composing rules

Rules support `all`, `any`, `not`, `has`, `inside`, `follows`, `precedes`:

```yaml
id: await-in-loop
language: JavaScript
rule:
  pattern: await $EXPR
  inside:
    any:
      - kind: for_statement
      - kind: for_in_statement
      - kind: while_statement
    stopBy: end
```

## Phase 3: Index — Build the Code Graph

For deeper analysis (call graphs, dependency trees, dead code), build a structured graph. See [graph-schema.md](graph-schema.md) for the node/edge schema.

### Using ast-grep for graph building

Combine ast-grep's `--json` output with graph construction:

```bash
# Export all function definitions as JSON
ast-grep -p 'function $NAME($$$PARAMS) { $$$BODY }' -l js --json src/

# Export all import statements as JSON
ast-grep -p 'import $$$SPECS from $MOD' -l js --json src/

# Export all require calls as JSON
ast-grep -p 'const $NAME = require($MOD)' -l js --json src/
```

### Using bundled scripts

**Python codebases:**
```bash
python3 scripts/build-graph.py <dir> --callers <symbol>  # find callers
python3 scripts/build-graph.py <dir> --unused            # dead code
python3 scripts/build-graph.py <dir> --depends-on <mod>  # reverse deps
python3 scripts/build-graph.py <dir> --cycles            # circular imports
```

## Phase 4: Act — Apply Changes Safely

### Structural rewriting with ast-grep

```bash
# Replace deprecated API calls
ast-grep -p 'oldApi($ARGS)' -r 'newApi($ARGS)' -l js --interactive src/

# Convert arrow functions to regular functions
ast-grep -p 'const $NAME = ($$$PARAMS) => { $$$BODY }' \
         -r 'function $NAME($$$PARAMS) { $$$BODY }' -l js --interactive src/

# Add error handling wrapper
ast-grep -p 'fetch($URL)' -r 'safeFetch($URL)' -l js --interactive src/
```

### Safe refactoring workflow

1. **Search** — `ast-grep -p '<pattern>' src/` to find all matches
2. **Review** — Add `--json` to inspect match details and context
3. **Preview** — Add `-r '<rewrite>'` to see the replacement
4. **Apply** — Add `--interactive` to selectively apply changes
5. **Verify** — Re-run the search to confirm zero remaining matches

## Quick Reference

| I want to... | ast-grep command |
|---------------|-----------------|
| Find all calls to `foo()` | `ast-grep -p 'foo($$$ARGS)' src/` |
| Find function definitions | `ast-grep -p 'function $NAME($$$P) { $$$B }' src/` |
| Find unused imports | `ast-grep scan --inline-rules '...' src/` |
| Rename `oldFn` → `newFn` | `ast-grep -p 'oldFn($$$A)' -r 'newFn($$$A)' --interactive src/` |
| Convert `var` → `const` | `ast-grep -p 'var $N = $V' -r 'const $N = $V' --interactive src/` |
| Find patterns in JSON output | `ast-grep -p '<pattern>' --json src/` |
| Run YAML lint rule | `ast-grep scan --rule rule.yml src/` |
| Check change impact | Build graph → find all transitive callers (reverse BFS) |

## Supporting Files

- **[ast-grep-cheatsheet.md](ast-grep-cheatsheet.md)** — Full ast-grep pattern and CLI reference
- **[graph-schema.md](graph-schema.md)** — Node and edge type definitions with ER diagram
- **[query-patterns.md](query-patterns.md)** — Detailed cookbook of query patterns with examples
- **[scripts/parse-js.mjs](scripts/parse-js.mjs)** — Cross-platform Node.js script for JS/TS AST parsing (fallback)
- **[scripts/build-graph.py](scripts/build-graph.py)** — Python code graph builder (stdlib only)
