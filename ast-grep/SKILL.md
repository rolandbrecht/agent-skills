---
name: ast-grep
description: >
  Use this skill ANY time you must search, lint, or rewrite code by its syntax structure.
  ast-grep is an AST-based CLI tool. It matches code by syntax tree, not by text.
  ALWAYS prefer it over grep/ripgrep when the query is about code structure.
  Trigger categories: structural code search (find all calls to X, functions without Y),
  bulk code rewrite/codemod (replace API calls, migrate deprecated patterns),
  custom lint rules (enforce project patterns), multi-pass symbol renaming,
  code outline/structure exploration, ast-grep rule authoring.
  Trigger keywords: ast-grep, sg, structural search, codemod, rewrite pattern,
  metavariable, tree-sitter pattern, lint rule, sgconfig, find all calls,
  refactor across files, AST.
  Do NOT trigger for: plain string or regex searches, file-name lookups,
  log/config searches, single-file edits you can do by hand.
---

# ast-grep — Structural Code Search, Lint, and Rewrite

Content verified against ast-grep 0.45.1. Flags can drift between versions — when a command fails, check `ast-grep <cmd> --help`.

## Overview

ast-grep is a fast, Rust-based CLI tool. It parses code with tree-sitter and matches the syntax tree, not the text. You write patterns that look like the code you search for. Metavariables (`$NAME`, `$$$ARGS`) act as wildcards for AST nodes.

Three main modes:

| Mode | Command | Use for |
| --- | --- | --- |
| Search / rewrite | `ast-grep run -p '<pattern>'` (default command) | One-time queries and codemods |
| Lint | `ast-grep scan` | YAML rule sets, CI checks, complex rules |
| Explore | `ast-grep outline` | Symbols, imports, exports of files |

It supports 25+ languages: JavaScript, TypeScript, TSX, Python, Rust, Go, Java, C, C++, C#, Kotlin, Swift, Ruby, PHP, and more. See the language table in [references/cli-reference.md](references/cli-reference.md).

## Installation

Check first: `which ast-grep`. If it is not installed, run the bundled helper:

```bash
bash <SKILL_DIR>/scripts/install.sh
```

The script tries brew, cargo, npm, pip3, and MacPorts in order, and verifies the result. For manual installation see <https://ast-grep.github.io/guide/quick-start.html>.

Note: some systems have a different `sg` binary (shell group). Always use the full name `ast-grep`.

## Tool Selection: grep vs ast-grep vs LSP

| The question is about... | Use |
| --- | --- |
| Text: strings, error messages, config values, file names | `grep` / `rg` / `fd` |
| Syntax: "all calls that look like X", pattern rewrites, codemods, lint rules | **ast-grep** |
| Semantics: go-to-definition, find-references across scopes, types, scope-aware rename | LSP / compiler tooling |
| Graphs: transitive callers, circular imports, dead-code detection across a whole codebase | A graph script over `ast-grep --json` output; ast-grep alone sees only per-file matches |

ast-grep matches syntax, not semantics. It cannot tell two same-named symbols in different scopes apart. A rename with ast-grep is an **exact syntactic** replace (it skips comments, strings, and `oldNameHelper`), but it hits *every* scope. For a true semantic rename, prefer an LSP rename; use ast-grep when no LSP is available and verify the diff.

There is no runtime conflict with LSP tools: the ast-grep CLI is stateless — it reads files, matches, and exits. It starts no server and builds no index.

Also do NOT use ast-grep when:

- The pattern spans comments or string contents — patterns cannot match inside them.
- The codebase is tiny (< 5 files) — just read the files.

Files with syntax errors are usually fine: tree-sitter error recovery still matches the valid regions.

## Quick Start

```bash
# Find all console.log calls in TypeScript
ast-grep -p 'console.log($$$ARGS)' -l ts src/

# Rewrite: var -> const, interactive review per match
ast-grep -p 'var $N = $V' -r 'const $N = $V' -l js --interactive src/

# Apply all rewrites without confirmation
ast-grep -p '$P && $P()' -r '$P?.()' -l ts -U src/

# Only list files that contain a match
ast-grep -p 'eval($$$A)' -l js --files-with-matches src/

# JSON output for scripts (note: --json requires `=` for its value)
ast-grep -p 'function $NAME($$$P) { $$$B }' -l ts --json=compact src/ > matches.json

# Run one inline YAML rule without a file
ast-grep scan --inline-rules 'id: no-eval
language: typescript
severity: error
rule: {pattern: "eval($$$A)"}' src/

# Show the structure of a file
ast-grep outline src/parser.ts --type class,function

# Test a pattern without files, via stdin
echo 'var x = 1' | ast-grep -p 'var $N = $V' -l js --stdin
```

Always put patterns in **single quotes** — double quotes let the shell expand `$NAME` first. For interactive pattern experiments there is an online playground: <https://ast-grep.github.io/playground.html>

## Metavariables — Minimal Reminder

- `$VAR` matches exactly **one** AST node. `$$$ARGS` matches **zero or more**.
- **Default to `$$$` for arguments, parameters, and bodies.** `foo($ARG)` matches only one-argument calls — this is the most common cause of missed matches.
- Repeated names must match identical content: `$A == $A` matches `x == x`, not `x == y`.
- Names use `A-Z`, `_`, digits. `$var` is invalid. `$_NAME` is non-capturing.

Full syntax, pattern objects, strictness, and language pitfalls (TypeScript generics, keywords, statement-vs-expression): [references/pattern-syntax.md](references/pattern-syntax.md).

## Standard Workflow: Rewrite

1. **Search:** `ast-grep -p '<pattern>' -l <lang> <path>` — check the matches.
2. **Inspect:** add `--json=compact` if you must verify match boundaries.
3. **Preview:** add `-r '<rewrite>'` — the diff prints to stdout, nothing is written.
4. **Apply:** add `--interactive` for per-match review, or `-U` to apply all.
5. **Verify:** run the search again and expect exit code 1 (no matches). Then run the project tests.

A rename needs multiple passes (definition, call sites, imports are distinct node kinds) — see [references/pattern-syntax.md](references/pattern-syntax.md).

## Exit Codes

- `run`: `0` = at least one match, `1` = no match. In scripts, "no matches" is not an error.
- `scan`: `0` = clean, `1` = diagnostics with `error` severity found. Use this as a CI gate.
- Other non-zero codes signal usage or config errors (e.g. `2` bad flag, `8` invalid pattern/rule).
- **Pipelines mask exit codes.** `ast-grep ... | other-tool` reports the last command's status. Set `set -o pipefail` (bash/zsh) when the ast-grep status matters.

## Reference Files

Read these on demand. Do not load them all at once.

- [references/cli-reference.md](references/cli-reference.md) — All subcommands and flags (verified against 0.45.1), flag syntax rules, language table.
- [references/pattern-syntax.md](references/pattern-syntax.md) — Full pattern syntax, pattern objects, strictness levels, pitfalls with examples.
- [references/rule-yaml.md](references/rule-yaml.md) — YAML rule files, rule object (atomic/relational/composite), `sgconfig.yml` project setup, rule testing, CI.
- [references/pattern-cookbook.md](references/pattern-cookbook.md) — Ready-to-use patterns for JS/TS/Python, rewrite recipes with semantic warnings, task recipes (find callers, dead exports), YAML rule scenarios.

## Bundled Scripts

Replace `<SKILL_DIR>` with the absolute directory of this SKILL.md file.

- `scripts/install.sh` — Try available package managers in order and install ast-grep.
- `scripts/json-summary.py` — Summarize `ast-grep --json` output: match counts per file plus a compact match list. Usage:

  ```bash
  set -o pipefail   # keep ast-grep's exit code visible
  ast-grep -p '<pattern>' --json=compact <path> | python3 <SKILL_DIR>/scripts/json-summary.py
  ```
