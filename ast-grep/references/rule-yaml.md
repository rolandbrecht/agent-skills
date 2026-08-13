# ast-grep YAML Rules, Rule Object, and Project Setup

Sources: <https://ast-grep.github.io/reference/yaml>, <https://ast-grep.github.io/reference/rule>, <https://ast-grep.github.io/reference/sgconfig>

Verified against **ast-grep 0.45.1**.

Use YAML rules when a plain pattern is not enough: relational conditions ("inside a loop", "has no try-catch"), constraints on metavariables, reusable lint rules, or complex fixes.

## Contents

- [Rule file — top-level fields](#rule-file--top-level-fields)
- [The rule object](#the-rule-object) (atomic, relational, composite)
- [Worked examples](#worked-examples)
- [Project setup — sgconfig.yml](#project-setup--sgconfigyml)
- [Config discovery](#config-discovery)
- [Testing rules](#testing-rules)
- [CI usage](#ci-usage)

## Rule File — Top-Level Fields

```yaml
id: no-console-log            # required, unique, descriptive
language: typescript          # required, see language table in cli-reference.md
severity: warning             # hint | info | warning | error | off
message: "Do not use console.log in production code."
note: |
  Markdown explanation. No metavariables here.
url: https://example.com/docs/no-console-log
files:                        # only apply to these globs
  - src/**/*.ts
ignores:                      # never apply to these globs
  - "**/*.test.ts"
rule:                         # required — the Rule Object, see below
  pattern: console.log($$$ARGS)
constraints:                  # extra checks on metavariables
  ARGS:
    regex: "^[^']"
fix: logger.debug($$$ARGS)    # auto-fix; empty string "" deletes the node
transform: {}                 # derive new variables from captured ones
utils: {}                     # local reusable sub-rules, used via matches
rewriters: []                 # advanced multi-step rewrites
labels: {}                    # custom highlight per metavariable
metadata: {}                  # free-form data (e.g. CVE, OWASP)
```

Required: `id`, `language`, `rule`. Everything else is optional.

Run a single rule file: `ast-grep scan -r rule.yml src/`
Run inline without a file: `ast-grep scan --inline-rules '<yaml>' src/` (separate multiple rules with `---`).

## The Rule Object

Three categories. Combine them freely.

### Atomic rules

| Key | Matches |
| --- | --- |
| `pattern` | Pattern syntax (string, or object with `context` + `selector` + `strictness` for ambiguous snippets). |
| `kind` | Node type name, e.g. `call_expression`, `function_declaration`. Since v0.39: limited ESQuery, e.g. `call_expression > identifier`. Find kind names via `--debug-query=cst`. |
| `regex` | Rust regex against the node text. |
| `nthChild` | Position among **named** siblings, 1-based. Number, `An+B` formula, or object `{position, reverse, ofRule}`. |
| `range` | Exact position: `{start: {line, column}, end: {line, column}}`, 0-based, end exclusive. **Not usable alone** — combine with `kind`, or the rule fails with "Rule must specify a set of AST kinds to match" (exit 8). |

### Relational rules

| Key | Meaning |
| --- | --- |
| `inside` | The target node is inside a node that matches the sub-rule. |
| `has` | The target node contains a descendant that matches the sub-rule. |
| `precedes` | The target appears before a matching node. |
| `follows` | The target appears after a matching node. |

Options for `inside`/`has`:

- `stopBy` — how far to search. `neighbor` (default: direct parent/children only), `end` (walk the full tree), or a rule object (stop at nodes that match it). **Most "inside a function" rules need `stopBy: end`.**
- `field` — restrict to a named field of the node (e.g. `body`, `condition`).

### Composite rules

| Key | Meaning |
| --- | --- |
| `all: [...]` | Every sub-rule must match the **same node**. Preserves metavariable order. |
| `any: [...]` | At least one sub-rule matches. |
| `not: {...}` | The sub-rule must not match. |
| `matches: <util-id>` | Apply a utility rule from `utils` or a util directory. Enables reuse and recursion. |

Note: `all`/`any` combine **rules on one node**. They do not mean "multiple nodes".

## Worked Examples

All examples below are verified against ast-grep 0.45.

Async function without try-catch. Note: the `async` keyword is an **anonymous** node. `pattern: "async"` parses as an identifier and does not match it. Use `regex` on the node text instead:

```yaml
id: async-without-try
language: typescript
severity: warning
message: "Async function has no try-catch."
rule:
  kind: function_declaration
  regex: "^async"
  not:
    has:
      kind: try_statement
      stopBy: end
```

`await` outside an async function. The `stopBy` rule stops the ancestor walk at the **first** function boundary. With `stopBy: end` the walk continues past a nested async arrow function and produces false positives:

```yaml
id: await-in-sync
language: typescript
severity: error
message: "await used outside an async function."
rule:
  pattern: await $EXPR
  inside:
    any:
      - kind: function_declaration
      - kind: arrow_function
      - kind: method_definition
    stopBy:
      any:
        - kind: function_declaration
        - kind: arrow_function
        - kind: method_definition
    not:
      regex: "^async"
```

Constraint on a metavariable:

```yaml
id: no-magic-timeout
language: javascript
rule:
  pattern: setTimeout($FN, $DELAY)
constraints:
  DELAY:
    regex: '^\d{4,}$'   # 1000ms or more
```

`transform` — derive variables for the fix:

```yaml
transform:
  NEW_NAME:
    replace:
      source: $NAME
      replace: 'Impl$'
      by: ''
fix: $NEW_NAME($$$ARGS)
```

## Project Setup — sgconfig.yml

`sgconfig.yml` is the project root config, like `.eslintrc`. Create a project with `ast-grep new project`.

```yaml
ruleDirs:            # required — where YAML rules live
  - rules
testConfigs:         # optional — rule tests
  - testDir: rule-tests
    snapshotDir: __snapshots__
utilDirs:            # optional — global utility rules
  - utils
languageGlobs:       # optional — map extra extensions to languages
  html: ['*.vue', '*.svelte', '*.astro']
  json: ['.eslintrc']
customLanguages:     # optional — tree-sitter parsers as dynamic libraries
  mojo:
    libraryPath: mojo.so
    extensions: ['mojo']
languageInjections:  # experimental — embedded languages
  - hostLanguage: js
    rule:
      pattern: styled.$TAG`$CONTENT`
    injected: css
```

With this in place, `ast-grep scan` (no flags) runs all rules from `ruleDirs`.

## Config Discovery

- `ast-grep scan` looks for `sgconfig.yml` in the current directory. Run it from the project root, or pass the config explicitly: `ast-grep scan -c path/to/sgconfig.yml`.
- All paths in `sgconfig.yml` (`ruleDirs`, `utilDirs`, `testDir`, `snapshotDir`) resolve **relative to the sgconfig.yml file**, not to the current directory.
- `files:` and `ignores:` globs in a rule match against paths as scanned. For predictable results, run the scan from the project root.
- No project setup is needed for a single rule: use `ast-grep scan -r rule.yml` or `--inline-rules`.

## Testing Rules

1. `ast-grep new test` scaffolds a test file.
2. A test file lists `valid` code (must not match) and `invalid` code (must match):

   ```yaml
   id: no-console-log        # must equal the rule id
   valid:
     - logger.debug('ok')
   invalid:
     - console.log('bad')
   ```

3. Run `ast-grep test`. Snapshots of matches and fixes go to `__snapshots__`.
4. Update snapshots after intended changes: `ast-grep test -U` (or `-i` for interactive review).

## CI Usage

```bash
ast-grep scan --format github .    # GitHub Actions annotations
ast-grep scan --format sarif . > results.sarif
ast-grep scan --report-style short .
```

Exit code is `1` when error-severity rules match, `0` when the scan is clean. Override severities per run with `--error=<rule-id>`, `--warning=<rule-id>`, `--off=<rule-id>`.

**The `=` is required.** `--error my-rule` does NOT target `my-rule` — it sets ALL rules to error and treats `my-rule` as a path argument. In pipelines, add `set -o pipefail` so the scan exit code survives.
