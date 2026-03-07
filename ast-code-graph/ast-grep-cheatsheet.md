# ast-grep Cheatsheet

Quick reference for [ast-grep](https://ast-grep.github.io/) (`ast-grep` or `sg` on non-Linux).

## Installation

```bash
# Any of:
pip install ast-grep-cli
npm i @ast-grep/cli -g
brew install ast-grep
cargo install ast-grep --locked
```

## Core Concepts

ast-grep matches **AST nodes**, not text. You write patterns that look like real code, and ast-grep finds all structurally equivalent matches.

### Metavariables

| Syntax | Matches | Analogy |
|--------|---------|---------|
| `$NAME` | Exactly one AST node | regex `.+` |
| `$$$LIST` | Zero or more AST nodes | regex `.*` |
| `$_` | One node (anonymous, no capture) | regex `.` |

Metavariables that appear multiple times in a pattern must match the **same** code:
```bash
# Finds: x && x()  but NOT: x && y()
ast-grep -p '$A && $A()' src/
```

## CLI Commands

### `ast-grep run` (default — search & rewrite)

```bash
# Search for a pattern (run is the default subcommand)
ast-grep -p '<pattern>' [--lang <lang>] [paths...]

# Search with rewrite preview
ast-grep -p '<pattern>' -r '<rewrite>' [paths...]

# Apply rewrite interactively
ast-grep -p '<pattern>' -r '<rewrite>' --interactive [paths...]

# Output as JSON (for programmatic use)
ast-grep -p '<pattern>' --json [paths...]
```

**Key flags:**
| Flag | Short | Description |
|------|-------|-------------|
| `--pattern` | `-p` | The pattern to search for |
| `--rewrite` | `-r` | Replacement pattern (uses same metavars) |
| `--lang` | `-l` | Language (js, ts, py, rust, go, java, etc.) |
| `--interactive` | `-i` | Prompt before each replacement |
| `--json` | | Machine-readable JSON output |

### `ast-grep scan` (rule-based linting)

```bash
# Run a single YAML rule file
ast-grep scan --rule <rule.yml> [paths...]

# Run inline rule (no file needed)
ast-grep scan --inline-rules '<yaml>' [paths...]

# Run all rules in a project (requires sgconfig.yml)
ast-grep scan [paths...]
```

## Pattern Examples by Language

### JavaScript / TypeScript

```bash
# Function calls
ast-grep -p 'console.log($MSG)' -l js src/
ast-grep -p 'require($MOD)' -l js src/
ast-grep -p 'fetch($URL, $OPTS)' -l js src/

# Imports
ast-grep -p 'import $NAME from $MOD' -l js src/
ast-grep -p 'import { $$$NAMES } from $MOD' -l js src/

# Function definitions
ast-grep -p 'function $NAME($$$PARAMS) { $$$BODY }' -l js src/
ast-grep -p 'const $NAME = ($$$PARAMS) => $BODY' -l js src/
ast-grep -p 'async function $NAME($$$PARAMS) { $$$BODY }' -l js src/

# Class patterns
ast-grep -p 'class $NAME extends $BASE { $$$BODY }' -l js src/
ast-grep -p 'class $NAME { $$$BODY }' -l js src/

# Control flow
ast-grep -p 'if ($COND) { $$$THEN }' -l js src/
ast-grep -p 'try { $$$TRY } catch ($ERR) { $$$CATCH }' -l js src/

# Variable declarations
ast-grep -p 'var $NAME = $VALUE' -l js src/
ast-grep -p 'const $NAME = $VALUE' -l js src/
```

### Python

```bash
# Function definitions
ast-grep -p 'def $NAME($$$PARAMS): $$$BODY' -l py src/
ast-grep -p 'async def $NAME($$$PARAMS): $$$BODY' -l py src/

# Imports
ast-grep -p 'import $MOD' -l py src/
ast-grep -p 'from $MOD import $$$NAMES' -l py src/

# Class definitions
ast-grep -p 'class $NAME($$$BASES): $$$BODY' -l py src/

# Decorators
ast-grep -p '@$DECORATOR' -l py src/
```

## Rewrite Examples

```bash
# var → const
ast-grep -p 'var $N = $V' -r 'const $N = $V' -l js -i src/

# console.log → logger.debug
ast-grep -p 'console.log($$$ARGS)' -r 'logger.debug($$$ARGS)' -l js -i src/

# require → import
ast-grep -p 'const $N = require($M)' -r 'import $N from $M' -l js -i src/

# Optional chaining
ast-grep -p '$A && $A.$B' -r '$A?.$B' -l js -i src/

# Null coalescing
ast-grep -p '$A || $DEFAULT' -r '$A ?? $DEFAULT' -l js -i src/
```

## YAML Rule Syntax

```yaml
id: rule-name                # unique identifier
language: JavaScript         # target language
severity: warning            # error | warning | info | hint
message: Human-readable msg  # shown to user

rule:
  # Atomic rules (match the node itself)
  pattern: 'code.pattern($X)'        # structural match
  kind: 'function_declaration'       # tree-sitter node kind
  regex: 'some.*regex'               # regex on node text

  # Relational rules (match based on surrounding nodes)
  has:                               # node contains child matching...
    pattern: 'await $_'
    stopBy: end                      # search all descendants
  inside:                            # node is inside parent matching...
    kind: for_statement
  follows:                           # node comes after sibling matching...
    pattern: 'const $_ = require($_)'
  precedes:                          # node comes before sibling matching...
    kind: return_statement

  # Composite rules (combine sub-rules)
  all:                               # AND — all must match
    - pattern: '$A($$$)'
    - not: { pattern: 'console.$_($$$)' }
  any:                               # OR — any can match
    - pattern: 'var $_ = $_'
    - pattern: 'let $_ = $_'
  not:                               # NOT — must not match
    pattern: 'const $_ = $_'

fix: 'replacement.code($X)'         # auto-fix pattern
```

## Tips

- **Use single quotes** around patterns in bash to prevent `$` expansion
- **Language is auto-detected** from file extensions if `--lang` is omitted
- **On Linux**, use `ast-grep` (not `sg`, which is `setgroups`)
- **Test patterns** at the [online playground](https://ast-grep.github.io/playground.html)
- `--json` output includes file, line, column, matched text, and metavar bindings
