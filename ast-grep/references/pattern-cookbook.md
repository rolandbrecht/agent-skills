# ast-grep Pattern Cookbook

Ready-to-use patterns by language and task. Patterns verified against **ast-grep 0.45.1**.

## Contents

- [Quick pattern testing](#quick-pattern-testing)
- [JavaScript / TypeScript](#javascript--typescript)
- [Python](#python)
- [Rewrite recipes](#rewrite-recipes)
- [Task recipes](#task-recipes)
- [YAML rule scenarios](#yaml-rule-scenarios)
- [Caveats](#caveats)

## Quick Pattern Testing

Test a pattern without files — pipe code through stdin:

```bash
echo 'var x = 1' | ast-grep -p 'var $N = $V' -l js --stdin
echo 'const x = await fetch()' | ast-grep scan --inline-rules '<yaml>' --stdin
```

Or use the online playground: <https://ast-grep.github.io/playground.html>

Shell tip: always put patterns in **single quotes**. Double quotes let the shell expand `$NAME` before ast-grep sees it.

## JavaScript / TypeScript

```bash
# Function calls
ast-grep -p 'console.log($$$ARGS)' -l js src/
ast-grep -p '$OBJ.myMethod($$$ARGS)' -l js src/          # method calls on any object
ast-grep -p 'require($MOD)' -l js src/
ast-grep -p 'fetch($URL, $OPTS)' -l js src/              # exactly two arguments!

# Imports
ast-grep -p 'import $NAME from $MOD' -l js src/           # default import
ast-grep -p 'import { $$$NAMES } from $MOD' -l js src/    # named imports
ast-grep -p 'const $N = require($M)' -l js src/           # CommonJS

# Function definitions
ast-grep -p 'function $NAME($$$PARAMS) { $$$BODY }' -l js src/
ast-grep -p 'async function $NAME($$$PARAMS) { $$$BODY }' -l js src/
ast-grep -p 'const $NAME = ($$$PARAMS) => $BODY' -l js src/

# Classes
ast-grep -p 'class $NAME { $$$BODY }' -l js src/
ast-grep -p 'class $NAME extends $BASE { $$$BODY }' -l js src/

# Control flow
ast-grep -p 'if ($COND) { $$$THEN }' -l js src/
ast-grep -p 'try { $$$TRY } catch ($ERR) { $$$CATCH }' -l js src/
```

TypeScript-only:

```bash
# Interfaces and type aliases
ast-grep -p 'interface $NAME { $$$BODY }' -l ts src/
ast-grep -p 'type $NAME = $TYPE' -l ts src/

# Typed arrow functions
ast-grep -p 'const $NAME = ($$$P): $RET => $BODY' -l ts src/

# Decorators
ast-grep -p '@$DECORATOR($$$ARGS)' -l ts src/
ast-grep -p '@$DECORATOR' -l ts src/

# Generic calls need a second pass (see pattern-syntax.md)
ast-grep -p 'myFn($$$A)' -l ts src/
ast-grep -p 'myFn<$T>($$$A)' -l ts src/      # $T also matches unions; $$$T for <A, B>
```

Remember: run patterns with both `-l ts` and `-l tsx` in React projects.

## Python

```bash
# Function definitions
ast-grep -p 'def $NAME($$$PARAMS): $$$BODY' -l py src/
ast-grep -p 'async def $NAME($$$PARAMS): $$$BODY' -l py src/

# Imports
ast-grep -p 'import $MOD' -l py src/
ast-grep -p 'from $MOD import $$$NAMES' -l py src/

# Classes and decorators
ast-grep -p 'class $NAME($$$BASES): $$$BODY' -l py src/
ast-grep -p '@$DECORATOR' -l py src/
```

## Rewrite Recipes

```bash
# var -> const
ast-grep -p 'var $N = $V' -r 'const $N = $V' -l js -i src/

# console.log -> logger.debug
ast-grep -p 'console.log($$$ARGS)' -r 'logger.debug($$$ARGS)' -l js -i src/

# Deprecated API migration
ast-grep -p 'oldApi($$$ARGS)' -r 'newApi($$$ARGS)' -l js -i src/

# Wrap calls
ast-grep -p 'await fetch($URL)' -r 'await safeFetch($URL)' -l js -i src/

# Optional chaining
ast-grep -p '$A && $A.$B' -r '$A?.$B' -l js -i src/
```

**Warning — rewrites can change semantics.** A structural match does not prove behavioral equivalence. Example: `$A || $DEFAULT` → `$A ?? $DEFAULT` looks like a modernization, but `||` triggers on all falsy values (`0`, `''`, `false`) while `??` triggers only on `null`/`undefined`. Review such rewrites case by case (`--interactive`), and run the tests after.

## Task Recipes

**Find all callers of a function** (before a signature change):

```bash
ast-grep -p 'myFunc($$$ARGS)' -l ts src/          # direct calls
ast-grep -p '$OBJ.myFunc($$$ARGS)' -l ts src/     # method-style calls
```

Caveat: this misses indirect calls through aliases (`const fn = myFunc; fn()`). Verified: the alias call does not match the pattern. For exhaustive impact analysis, use semantic tooling (LSP find-references) on top.

**Find candidate dead exports:**

```bash
ast-grep -p 'export function $NAME($$$P) { $$$B }' -l ts --json=compact src/ > exports.json
ast-grep -p 'import { $$$NAMES } from $MOD' -l ts --json=compact src/ > imports.json
# then cross-reference the two JSON files with a script
```

Caveats: dynamic imports (`require(variable)`, `import(expr)`) are invisible to this approach. Exclude entry points and test files before you call an export dead.

**Extract all imports of a module:**

```bash
ast-grep -p 'import $$$SPECS from "./config"' -l ts src/
```

## YAML Rule Scenarios

Note: a rule scans only files that match its `language`. A `language: javascript` rule silently ignores `.ts` files — write a separate rule (or duplicate with `language: typescript`) for TypeScript.

Match only in context — `console.log` inside class methods:

```yaml
id: console-in-class
language: javascript
rule:
  pattern: console.log($$$ARGS)
  inside:
    kind: method_definition
    stopBy: end
```

Missing safety pattern — functions that `await` without any try-catch:

```yaml
id: await-no-trycatch
language: javascript
severity: warning
message: "This function awaits without a try-catch."
rule:
  kind: function_declaration
  all:
    - has:
        pattern: await $EXPR
        stopBy: end
    - not:
        has:
          kind: try_statement
          stopBy: end
```

Rule of thumb: relational rules (`has`, `inside`) check only direct children/parents by default. Add `stopBy: end` for "anywhere inside" semantics — but use a `stopBy` rule at function boundaries when nesting matters (see the verified `await-in-sync` example in [rule-yaml.md](rule-yaml.md)).

## Caveats

- **Argument counts are exact.** `fetch($URL, $OPTS)` matches only two-argument calls. Use `fetch($$$ARGS)` to catch all arities, then filter.
- **Aliased/indirect calls do not match call patterns.** Combine with LSP references for completeness.
- **Dynamic imports are invisible** to import patterns.
- **`--json` output includes the metavariable bindings** (`metaVariables` field), file, range, and matched text — use it when a recipe needs post-processing.
