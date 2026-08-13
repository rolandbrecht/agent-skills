# ast-grep Pattern Syntax

Verified against **ast-grep 0.45.1**. Web reference: <https://ast-grep.github.io/guide/pattern-syntax>

A pattern is code that looks like the code you search for. ast-grep parses the pattern with tree-sitter and matches it against the syntax tree of the target files. Text details such as spacing do not matter. Structure matters.

## Contents

- [Metavariables](#metavariables)
- [Pattern requirements and limitations](#pattern-requirements-and-limitations)
- [Pattern object](#pattern-object-yaml-rules-only)
- [Strictness levels](#strictness-levels)
- [Language-specific pitfalls](#language-specific-pitfalls)
- [Renaming symbols](#renaming-symbols)
- [Debugging a pattern](#debugging-a-pattern-that-does-not-match)

## Metavariables

### `$VAR` — one node

- Matches exactly **one** named AST node.
- Name rules: `$` followed by upper-case letters `A-Z`, underscore `_`, or digits `1-9`.
- Valid: `$META`, `$META_VAR1`, `$_`, `$_123`.
- Invalid: `$invalid` (lower case), `$Svalue` (mixed case), `$123` (starts with digit), `$KEBAB-CASE` (hyphen).

Example: `console.log($GREETING)`

- Matches: `console.log('Hello')`
- Does NOT match: `console.log()` or `console.log(a, b)` — the argument count must be exactly one.

### `$$$VAR` — zero or more nodes

Matches zero or more nodes. Use for argument lists, parameter lists, and statement blocks.

Example: `console.log($$$ARGS)` matches:

```js
console.log()
console.log('hello')
console.log('debug:', key, value)
console.log(...args)
```

**Default to `$$$` for arguments and bodies.** The single-node form is the most common cause of missed matches.

### Capturing and back-references

Two metavariables with the same name must match identical content:

```text
Pattern: $A == $A
a == a            ✓
1 + 1 == 1 + 1    ✓
a == b            ✗
```

### `$_VAR` — non-capturing

A name that starts with `_` is not captured. Repeated `$_X` occurrences can match **different** content. Non-capturing match is also faster.

```text
Pattern: $_FUNC($_FUNC)
test(a)      ✓   (the two $_FUNC differ — allowed)
```

### `$$VAR` — unnamed nodes (rarely useful)

Tree-sitter distinguishes *named* nodes (expressions, identifiers) and *anonymous* nodes (operators, keywords, punctuation). `$VAR` matches only named nodes. `$$VAR` also matches anonymous nodes.

Verified limits on 0.45.1:

- `$A $$OP $B` is **rejected**: it parses as multiple root nodes ("Multiple AST nodes are detected", exit 8). You cannot match "any binary operator" this way.
- A bare `$$OP` pattern matches every node, named and unnamed — too broad to be useful alone.

To match keyword or operator variants, use a YAML rule with `kind` (e.g. `kind: binary_expression`) plus `regex` or `has`, instead of `$$VAR`.

## Pattern Requirements and Limitations

1. **One root node.** The pattern must parse to a single AST node. Multi-statement patterns fail: `let $A = $B; let $C = $D;` → "Multiple AST nodes are detected" (exit 8). Match one statement, or use a YAML rule with relational conditions (`follows`, `precedes`).
2. **Broken patterns degrade, they do not always fail.** An incomplete snippet like `foo(` is accepted via tree-sitter error recovery. ast-grep prints a warning ("Pattern contains an ERROR node and may cause unexpected results") and the results are unreliable. Treat that warning as an error and fix the pattern.
3. **No matching inside comments or strings.** Patterns match AST nodes. Comment text and string contents are opaque.
4. **Patterns match nested code.** `a + 1` also matches inside `f(a + 1)` and `{x: a + 1}`.
5. **Target files with syntax errors still work partially.** Tree-sitter error recovery matches the valid regions of a malformed file.
6. **Ambiguous snippets need context.** Some snippets do not parse standalone (e.g. a class field, an object key). Use a **pattern object** in a YAML rule.

## Pattern Object (YAML rules only)

When a snippet is ambiguous or does not parse standalone, give it context and select the target node:

```yaml
rule:
  pattern:
    context: 'class A { $FIELD = $INIT }'   # full parsable code
    selector: field_definition               # the node kind to extract and match
    strictness: relaxed                       # optional
```

The pattern matches only the `field_definition` part, in any class.

Find node kind names with:

```bash
ast-grep --debug-query=cst -p '<your code>' -l <lang>
```

## Strictness Levels

Controls how strictly the matching algorithm compares trees (`--strictness` flag or `strictness` field):

| Level | Behavior |
| --- | --- |
| `cst` | All nodes must match, including trivia. Strictest. |
| `smart` | **Default.** All nodes in the pattern must match, but unnamed target nodes are skipped where sensible. |
| `ast` | Only named AST nodes must match. |
| `relaxed` | Named nodes match; comments are ignored. |
| `signature` | Named nodes match; comments and text content are ignored (matches by shape only). |
| `template` | Like smart, but matches text only; node kinds are ignored. |

Use `relaxed` or `signature` when comments inside the target code break your match.

## Language-Specific Pitfalls

### TypeScript / TSX

- **Generics are separate nodes.** `useState($$$A)` does NOT match `useState<string>('')` — the type arguments live in their own AST node. Run two passes:

  ```bash
  ast-grep -p 'useState($$$A)' -l ts src/
  ast-grep -p 'useState<$T>($$$A)' -l ts src/
  ```

  Verified: `$T` matches a single type argument **including unions** (`string | null` is one node). Use `$$$T` only for **multiple** type arguments, e.g. `foo<string, number>()`.

- **`ts` and `tsx` are different languages.** Run both for React projects.

### General

- **Keywords are anonymous nodes.** A pattern like `async` parses as an *identifier*, not as the `async` keyword. To test for a keyword in a YAML rule, use `regex` on the node text (e.g. `regex: "^async"` on a `function_declaration`).
- **Statement vs expression.** A pattern parsed as an expression does not match a full statement node and vice versa. If a match fails unexpectedly, inspect both trees with `--debug-query=cst` and compare.

## Renaming Symbols

ast-grep renames are **exact syntactic** replaces: they skip comments, strings, and longer identifiers (`oldNameHelper` stays untouched). But they are **not scope-aware** — every syntactic occurrence in every scope changes. Prefer an LSP rename for true semantic renaming; use ast-grep when no LSP is available, and review the diff.

Definitions, call sites, references, and imports are distinct node kinds, so a rename needs multiple passes:

```bash
# definition
ast-grep -p 'function oldName($$$P) { $$$B }' -r 'function newName($$$P) { $$$B }' -l ts src/
# call sites
ast-grep -p 'oldName($$$A)' -r 'newName($$$A)' -l ts src/
# named imports
ast-grep -p 'import { oldName } from $MOD' -r 'import { newName } from $MOD' -l ts src/
```

## Debugging a Pattern That Does Not Match

0. Reproduce small: `echo '<target code>' | ast-grep -p '<pattern>' -l <lang> --stdin`, or use the playground at <https://ast-grep.github.io/playground.html>.
1. Print the pattern tree: `ast-grep --debug-query=cst -p '<pattern>' -l <lang>`.
2. Print the target tree: paste the target code as the pattern and inspect its CST the same way.
3. Compare node kinds. Adjust the pattern, use `$$$`, or switch to a `kind` rule with `inside`/`has` (see [rule-yaml.md](rule-yaml.md)).
4. Lower the strictness if trivia or comments block the match.
5. Never ignore the "Pattern contains an ERROR node" warning — the pattern did not parse cleanly.
