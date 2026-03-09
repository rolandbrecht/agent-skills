# Comby Hole Syntax — Full Reference

## Named Holes

### `:[x]` — General hole (lazy, delimiter-aware)

Matches zero or more characters. Crucially, it respects balanced delimiters: if the hole
is inside `()`, it will not consume the closing `)`.

```text
Template: foo(:[a], :[b])
Input:    foo(bar(1, 2), baz)
Match:    a = "bar(1, 2)", b = "baz"
```

This is your default hole. Use it for:

- Argument lists: `someFunc(:[args])`
- Expression values: `const x = :[val]`
- Block bodies: `{ :[body] }`
- Multiline content

### `:[[x]]` — Word/identifier hole

Matches one or more characters matching `[a-zA-Z0-9_]` — i.e., a valid identifier.

```text
Template: :[[name]] = :[val]
Input:    myVar = 42 + other
Match:    name = "myVar", val = "42 + other"
```

Use when you specifically want to capture an identifier, not an arbitrary expression.
Prevents capturing spaces, operators, or nested calls.

### `:[x~regex]` — Regex-constrained hole

Matches using a PCRE regular expression. The regex is anchored to the hole's extent.

```text
Template: setTimeout(:[fn], :[ms~[0-9]+])
Input:    setTimeout(callback, 500)   ← matches
Input:    setTimeout(callback, delay) ← does NOT match
```

Examples:

```text
:[n~[0-9]+]           Integer literals
:[s~"[^"]*"]          Double-quoted strings
:[id~[a-z][a-zA-Z]+]  camelCase identifiers
:[x~.*]               Anything (explicit — same as :[x] but more explicit)
```

### `:[?x]` — Optional hole

Same matching behavior as `:[x]` but the entire hole (including surrounding whitespace)
can be absent. Useful when a pattern has optional components.

```text
Template: db.query(:[sql], :[?callback])
Input:    db.query("SELECT *")           ← matches, callback = ""
Input:    db.query("SELECT *", done)     ← matches, callback = "done"
```

### `:[x:e]` — Expression hole

Matches a non-whitespace sequence that may contain balanced structures. More restrictive
than `:[x]` — won't match across whitespace at the top level.

Useful when you want tight expression matching without capturing trailing whitespace.

### `:[id()]` — Fresh identifier generator (rewrite-side only)

In the rewrite template (not the match template), `:[id()]` generates a random
alphanumeric identifier. Use when you need to introduce a fresh unique variable name.

```text
Template: let :[x] = :[val]
Rewrite:  const :[id()] = :[val]; const :[x] = :[id()]
```

Each call to `:[id()]` generates the same value within one match substitution.

---

## Anonymous Holes

These match like named holes but don't bind a variable — use them when you need to skip
content you don't care about.

| Syntax | Matches | Notes |
|--------|---------|-------|
| `...` | Zero or more chars (lazy, delimiter-aware) | Shorthand for `:[_]` |
| `:[_]` | Zero or more chars | Same as `...` |
| `:[~regex]` | Regex, no binding | Anonymous version of `:[x~regex]` |

```bash
# Find any function call with at least one argument, don't care what
comby 'someFunc(..., :[last])' '' .js -match-only
```

---

## String Converters (rewrite-side only)

Append converters to hole references in the rewrite template to transform captured text.

### Case transformers

| Converter | Example input | Result |
|-----------|--------------|--------|
| `.uppercase` | `helloWorld` | `HELLOWORLD` |
| `.lowercase` | `HelloWorld` | `helloworld` |
| `.Capitalize` | `helloWorld` | `HelloWorld` |
| `.to_camelCase` | `hello_world` | `helloWorld` |
| `.to_snake_case` | `helloWorld` | `hello_world` |

```bash
# Convert a snake_case function name to camelCase
comby 'def :[[name]](:[args]):' 'function :[name.to_camelCase](:[args]) {' .py -diff
```

### Location / metadata

| Converter | Result |
|-----------|--------|
| `:[x.length]` | Character count of the captured text |
| `:[x.lines]` | Number of lines in the captured text |
| `:[x.line]` | Line number where the match starts |
| `:[x.column]` | Column number where the match starts |
| `:[x.offset]` | Byte offset from start of file |
| `:[x.file]` | Full file path |
| `:[x.file.name]` | Filename only (no directory) |
| `:[x.file.directory]` | Directory only |

These are useful for generating comments, logs, or documentation from matched code.

---

## Rule Expressions (where clauses)

After a structural match, `where` clauses filter results. Pass them via `-rule`.

### Equality / inequality

```bash
-rule 'where :[method] != "config"'      # Exclude when method is "config"
-rule 'where :[x] == :[y]'               # Only match when two holes are identical
```

### Pattern matching inside a rule

```bash
# Only keep matches where :[n] looks like a number
-rule 'where match :[n] { | "[0-9]+" -> true | _ -> false }'
```

### Rewrite inside a rule

```bash
# Transform the captured text before substituting
-rule 'where rewrite :[args] { | ":[a], :[b]" -> ":[b], :[a]" }'
```

---

## Template Files

For large migrations, write templates to files instead of shell args:

```text
migrations/rename-api/
├── match    (contains the match template, plain text)
├── rewrite  (contains the rewrite template, plain text)
└── rule     (optional, contains the where clause)
```

Run: `comby -templates migrations/ .js -i`

The `match` and `rewrite` files contain raw templates — no quotes, no escaping. This
avoids shell quoting issues for complex multiline patterns.

---

## Multiline Matching

`:[x]` naturally matches across lines when positioned inside balanced delimiters. For
patterns that must span multiple lines at the top level, put them in template files
(avoids shell newline handling issues).

**match file:**

```text
function :[[name]](:[args]) {
  :[body]
}
```

**rewrite file:**

```text
const :[[name]] = (:[args]) => {
  :[body]
}
```
