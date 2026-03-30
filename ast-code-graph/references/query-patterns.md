# Query Patterns Cookbook

Common AST and code graph query patterns with step-by-step instructions. Each pattern shows both the **ast-grep approach** (fast, great for search/rewrite) and the **graph approach** (deeper analysis).

---

## 1. Find All Callers of a Function

**When to use:** Before refactoring, renaming, or changing the signature of a function.

### ast-grep approach (quick)

```bash
# Find all calls to analyzeArticle
ast-grep -p 'analyzeArticle($$$ARGS)' -l js src/

# Find method calls on an object
ast-grep -p '$OBJ.analyzeArticle($$$ARGS)' -l js src/

# JSON output for programmatic use
ast-grep -p 'analyzeArticle($$$ARGS)' -l js --json src/
```

### Graph approach (exhaustive)

```bash
python3 <SKILL_DIR>/scripts/build-graph.py /path/to/project --callers analyzeArticle
```

**Why both?** ast-grep finds pattern matches instantly but may miss indirect calls (e.g., `const fn = analyzeArticle; fn()`). The graph approach traces through variable assignments.

---

## 2. Detect Unused Exports (Dead Code)

**When to use:** During cleanup, before releases, or to reduce bundle size.

### ast-grep approach (find exports)

```bash
# List all named exports
ast-grep -p 'export function $NAME($$$P) { $$$B }' -l js src/
ast-grep -p 'export const $NAME = $VALUE' -l js src/
ast-grep -p 'module.exports = { $$$EXPORTS }' -l js src/
```

Then cross-reference with imports:

```bash
# For each export, check if it's imported anywhere
ast-grep -p 'import { $$$NAMES } from $MOD' -l js --json src/ | grep "symbolName"
```

### Graph approach (automated)

```bash
python3 <SKILL_DIR>/scripts/build-graph.py /path/to/project --unused
```

**Caveats:**

- Dynamic imports (`require(variable)`) won't be detected by either approach
- Entry points (e.g., `main.js`, test files) should be excluded from "unused" results

---

## 3. Map the Import Dependency Tree

**When to use:** Understanding module organization, planning code splits, or identifying coupling.

### ast-grep approach (extract imports)

```bash
# List all import statements as JSON
ast-grep -p 'import $$$SPECS from $MOD' -l js --json src/
ast-grep -p 'const $N = require($M)' -l js --json src/

# Find all files that import a specific module
ast-grep -p 'import $$$_ from "./config"' -l js src/
```

### Graph approach (full tree)

```bash
python3 <SKILL_DIR>/scripts/build-graph.py /path/to/project --depends-on config
```

**Visualization:**

```text
src/digest-generator.js
├── src/llm/analyzer.js
│   └── src/config.js
├── src/storage/article-store.js
│   └── src/storage/db.js
└── src/config.js
```

---

## 4. Safe Structural Rewriting

**When to use:** Migrating APIs, modernizing syntax, enforcing patterns.

### ast-grep approach (this is where it shines)

```bash
# var → const
ast-grep -p 'var $N = $V' -r 'const $N = $V' -l js --interactive src/

# Modernize optional chaining
ast-grep -p '$A && $A.$B' -r '$A?.$B' -l js --interactive src/

# Replace deprecated API calls
ast-grep -p 'oldApi($$$ARGS)' -r 'newApi($$$ARGS)' -l js --interactive src/

# Wrap fetch calls with error handling
ast-grep -p 'await fetch($URL)' -r 'await safeFetch($URL)' -l js --interactive src/
```

**Rewriting is ast-grep's strongest use case.** The `--interactive` flag lets you review each change before applying.

---

## 5. Identify Circular Dependencies

**When to use:** Diagnosing mysterious load-order bugs, import errors, or planning modularization.

### Graph approach (required)

```bash
python3 <SKILL_DIR>/scripts/build-graph.py /path/to/project --cycles
```

This runs DFS cycle detection on the import graph. ast-grep can't detect cycles since it processes files independently without building a dependency graph.

---

## 6. Impact Analysis for a Proposed Change

**When to use:** Before making changes to a shared function — estimating blast radius.

### ast-grep approach (direct callers)

```bash
# Find direct callers (1 hop)
ast-grep -p 'analyzeArticle($$$ARGS)' -l js src/
```

### Graph approach (transitive impact)

```bash
python3 <SKILL_DIR>/scripts/build-graph.py /path/to/project --callers analyzeArticle
```

**Risk classification:**

| Callers | Risk | Action |
| --------- | ------ | -------- |
| 0 | None | Safe to change freely |
| 1–3 | Low | Review each caller |
| 4–10 | Medium | Test thoroughly |
| 10+ | High | Consider backward-compatible approach |

---

## 7. Advanced YAML Rule Scenarios

**When to use:** Enforcing project-specific conventions, finding missing patterns, or searching within specific contexts.

### Scenario A: Enforcing a Contextual Code Pattern

Find `console.log` but ONLY if it's inside a class method:

```yaml
id: console-in-class
language: javascript
rule:
  pattern: console.log($$$ARG)
  inside:
    kind: method_definition
    stopBy: end
```

### Scenario B: Finding Missing Safety Patterns

Find `async` functions that lack a `try-catch` block:

```yaml
id: async-no-trycatch
language: javascript
rule:
  all:
    - kind: function_declaration
    - has:
        pattern: await $EXPR
        stopBy: end
    - not:
        has:
          pattern: try { $$$ } catch ($E) { $$$ }
          stopBy: end
```

### Scenario C: Complex Auto-Fixing

Preventing `console.log` in production using environment variables:

```yaml
id: no-console-in-production
language: JavaScript
severity: warning
message: Use logger instead of console.log in production code
rule:
  pattern: console.log($$$ARGS)
  not:
    inside:
      kind: if_statement
      has:
        pattern: process.env.NODE_ENV === 'development'
fix: logger.info($$$ARGS)
```

**Usage:**

```bash
ast-grep scan --rule rules/my-rule.yml src/
```

---

## Pattern Selection Guide

| Question | Best tool | Pattern |
| ---------- | ----------- | --------- |
| "Who calls this function?" | ast-grep (quick) / graph (exhaustive) | #1 |
| "Is this code used anywhere?" | graph | #2 |
| "What does this module depend on?" | graph | #3 |
| "Rewrite all usages of X to Y" | **ast-grep** | #4 |
| "Are there circular imports?" | graph | #5 |
| "What breaks if I change this?" | ast-grep + graph | #6 |
| "Enforce a code convention" | **ast-grep** | #7 |
