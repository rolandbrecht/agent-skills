---
name: structural-refactor
description: >
  Use this skill for any structural code search or replacement task — it is the right choice
  whenever grep/sed would feel clunky or risky. Trigger on ANY of these patterns:

  **Structural find-and-replace across a codebase:** "replace all fetch(url, options) calls
  with the new fetchWithRetry signature", "rename the first argument of every logger.log
  call from msg to message", "swap the argument order of this helper across all files"

  **Cross-language or multi-format refactoring:** "update this API pattern in all .js and
  .ts files", "change all SQL SELECT * to SELECT col1, col2 in our query templates",
  "modernize these HTML button attributes"

  **Code migration / deprecated API patterns:** "migrate all createStore() calls to
  configureStore()", "update all axios.get(url) to the new axios({url, method}) form",
  "Python 2 print statements to Python 3 print() functions across the whole project",
  "modernize old Python 2 idioms to Python 3"

  **Safe multi-file replacements that regex would botch:** multiline expressions, nested
  parentheses, string literals that contain the search term, balanced brackets

  **Extracting structural patterns with JSON output for scripting:** "find all function
  calls that pass a hardcoded string as the first argument", "list every TODO comment with
  its location"

  Trigger keywords: structural replace, comby, code migration, refactor pattern, swap
  arguments, rename parameter, update API calls, deprecated pattern, multi-file replace,
  across all files, Python 2 to 3, 2to3, pyupgrade, modernize Python.

  Do NOT trigger for: pure text/string searches (use grep), AST-level semantic analysis
  like dead code or circular imports (use ast-code-graph), single-file edits you can just
  read and edit directly.
---

# Structural Code Refactoring

This skill covers three complementary tools for structural code transformation. Use the
right one for the job — they're not competitors, they're specialists.

## Pick the Right Tool

| Situation | Best tool |
|-----------|-----------|
| Cross-language pattern replace (JS, Go, SQL, HTML…) | **comby** |
| Rearrange/capture subexpressions across many files | **comby** |
| Python 2 → 3 migration (print, unicode, exec, dict…) | **2to3** |
| Modernizing Python 3 idioms (f-strings, type hints…) | **pyupgrade** |
| True AST analysis (dead code, call graphs, imports) | **ast-code-graph skill** |
| Simple string search | **grep / ripgrep** |

---

## comby — Structural Search and Replace

`comby` understands code shape: balanced delimiters, string boundaries, comment regions.
Unlike `sed`, you write patterns that look like the code you're targeting.

```
Match:   request.get(':[url]')
Rewrite: request({ url: ':[url]', method: 'get' })
```

**Wins over grep/sed when:**
- The pattern spans multiple lines or contains nested brackets
- The same text appears in comments/strings and you want to skip it
- You need to capture and rearrange subexpressions
- You're working across multiple languages in one pass

### Installation

```bash
which comby          # check first

brew install comby   # macOS
bash <(curl -sL get-comby.netlify.app)   # Ubuntu/Debian
cargo install comby  # any platform

# Docker — no install, prefix every command with:
# docker run --rm -it -v "$PWD":/src -w /src comby/comby
```

> Linux PCRE note: if comby complains about libpcre, run:
> `sudo ln -s /usr/lib/libpcre.so /usr/lib/libpcre.so.3`

### Hole Syntax

Holes are the wildcards in comby templates. Choose carefully to avoid over-matching.

| Hole | Matches | Use when |
|------|---------|----------|
| `:[x]` | Zero or more chars (lazy, respects delimiters) | General expressions, argument lists, bodies |
| `:[[x]]` | One or more word chars (`[a-zA-Z0-9_]`) | Identifiers, variable names |
| `:[x~regex]` | PCRE regex | Constrained patterns (e.g., `:[n~[0-9]+]`) |
| `:[?x]` | Optional — can be absent | Optional arguments, trailing commas |
| `...` or `:[_]` | Unnamed match (discard) | Skipping parts you don't need |

`:[x]` respects nested delimiters: `foo(:[args])` captures `bar(a, b), c` correctly
even though there are inner parentheses.

Reusing a hole name enforces equality: `(:[x], :[x])` only matches identical values.

**String converters** (rewrite side only): `:[x.to_camelCase]`, `:[x.to_snake_case]`,
`:[x.uppercase]`, `:[x.lowercase]`, `:[x.Capitalize]`, `:[x.length]`

Full reference: [references/hole-syntax.md](references/hole-syntax.md)

### Basic Usage

```bash
# Match-only (no changes)
comby 'console.log(:[msg])' '' .js -match-only
comby 'console.log(:[msg])' '' .js -match-only -json-lines   # structured output with line numbers

# Preview changes
comby 'var :[[n]] = :[v]' 'const :[[n]] = :[v]' .js -diff

# Apply
comby 'var :[[n]] = :[v]' 'const :[[n]] = :[v]' .js -i          # in-place
comby 'var :[[n]] = :[v]' 'const :[[n]] = :[v]' .js -review     # interactive y/n per match

# Scope to a directory
comby 'oldFunc(:[args])' 'newFunc(:[args])' .js -d src/

# Force a language parser
comby 'fmt.Println(:[args])' 'log.Printf("[DEBUG] %v", :[args])' -matcher .go -i
```

See [references/language-matchers.md](references/language-matchers.md) for all ~40 supported languages.

### Standard Safe-Refactoring Loop

1. **Search** — preview matches, zero risk: `comby 'pattern' '' .ext -d src/ -match-only`
2. **Inspect** — verify hole captures with JSON: add `-json-lines | jq '.matches[].environment'`
3. **Diff** — see exact changes: `comby 'pattern' 'rewrite' .ext -d src/ -diff`
4. **Apply** — interactively or bulk: `-review` or `-i`
5. **Verify** — re-run match-only and confirm zero results

### Multi-Pattern Migrations (templates directory)

For several related patterns (e.g., an API overhaul), use a templates directory:

```
migrations/
├── get-to-fetch/
│   ├── match      ← plain text match template
│   └── rewrite    ← plain text rewrite template
└── post-to-fetch/
    ├── match
    └── rewrite
```

```bash
comby -templates migrations/ .js -i
```

Name directories with `1-`, `2-` prefixes when order matters (more-specific patterns first).

### JSON Pipeline for Scripting

```bash
# Extract all hardcoded strings from logger.error() calls with file + line
comby 'logger.error(":[msg]", :[rest])' '' .ts -d src/ -match-only -json-lines \
  | jq -r '.uri + ":" + (.matches[].range.start.line | tostring) + "  " + .matches[].environment.msg'

# Cover both quote styles
{
  comby 'logger.error(":[msg]":[?rest])' '' .ts -d src/ -match-only -json-lines
  comby "logger.error(':[msg]':[?rest])" '' .ts -d src/ -match-only -json-lines
} | jq -r '.uri + ":" + (.matches[].range.start.line | tostring)' | sort -u
```

JSON structure: `{ "uri": "...", "matches": [{ "range": { "start": { "line": N } }, "environment": { "varname": "..." } }] }`

### Pre-filtering Large Codebases

```bash
rg -l 'createStore' --include='*.js' \
  | xargs comby 'createStore(:[args])' 'configureStore(:[args])' -matcher .js -i
```

### Advanced: Rules, Regex Holes, Parallelism

```bash
# where clauses filter after structural match
comby ':[obj].:[method](:[args])' ':[obj].:[method]_v2(:[args])' .js \
  -rule 'where :[method] != "config"'

# regex constraint in hole
comby 'setTimeout(:[fn], :[ms~[0-9]+])' 'setTimeout(:[fn], 0)' .js -i

# optional hole (matches with or without the argument)
comby 'db.query(:[sql], :[?cb])' 'db.queryAsync(:[sql])' .js -i

# parallel jobs for speed
comby 'pattern' 'rewrite' .py -i -jobs 8
```

### comby Quick Reference

| I want to… | Command |
|---|---|
| Find matches (no changes) | `comby 'pattern' '' .ext -match-only` |
| Preview as diff | `comby 'pattern' 'rewrite' .ext -diff` |
| Interactive apply | `comby 'pattern' 'rewrite' .ext -review` |
| Bulk apply | `comby 'pattern' 'rewrite' .ext -i` |
| Scope to directory | add `-d src/` |
| Get JSON with line numbers | add `-match-only -json-lines` |
| Multiple patterns | `comby -templates dir/ .ext -i` |
| Filter matches | add `-rule 'where :[var] != "value"'` |

### Common Pitfalls

- **`:[x]` vs `:[[x]]`**: use `:[[x]]` for identifiers; `:[x]` captures spaces and expressions too.
- **Don't start templates with a hole**: `:[x] = val` is slow. Lead with a literal token.
- **Python / indentation-sensitive languages**: comby doesn't model indentation. Always use `-review` or `-diff` first, and consider `2to3`/`pyupgrade` for Python-specific migrations (see below).
- **Empty rewrite = deletion**: `comby 'pattern' '' .ext -i` deletes all matches.

---

## 2to3 — Python 2 → 3 Migration

`2to3` ships with Python and is the right tool for Python 2 → 3 migrations. It is
AST-based, meaning it understands the language precisely — it handles every edge case that
comby would struggle with: `print >> sys.stderr`, trailing commas, bare `print`, `unicode`,
`exec`, `dict.iteritems()`, and more.

Use `2to3` instead of comby when migrating Python 2 code. Use comby for cross-language
or library-API refactoring in Python 3 codebases.

### Installation

Included with Python. Verify:

```bash
2to3 --version    # should print "2to3 X.Y"
```

### Common fixers

Each `-f` flag applies a specific transformation:

| Fixer | What it does |
|-------|-------------|
| `print` | `print "x"` → `print("x")`, handles all edge cases |
| `unicode` | `u"string"` → `"string"`, `unicode` → `str` |
| `exec` | `exec "code"` → `exec("code")` |
| `dict` | `.iteritems()` → `.items()`, `.itervalues()` → `.values()` |
| `xrange` | `xrange()` → `range()` |
| `raise` | `raise E, V` → `raise E(V)` |
| `except` | `except E, e` → `except E as e` |
| `has_key` | `d.has_key(k)` → `k in d` |
| `basestring` | `basestring` → `str` |

Run `2to3 --list-fixes` for the full list.

### Usage

```bash
# Preview diffs without writing (safe)
2to3 -f print lib/

# Apply print fixer to all .py files in lib/
2to3 -f print -w lib/

# Apply ALL Python 2 → 3 fixers at once
2to3 -w lib/

# Apply multiple specific fixers
2to3 -f print -f unicode -f dict -w lib/

# No backup files (safe if you're in git)
2to3 -f print -w -n lib/
```

### Safe Migration Workflow

```bash
# 1. Commit first — gives you a clean rollback point
git add lib/ && git commit -m "chore: snapshot before Python 3 migration"

# 2. Preview what will change
2to3 -f print lib/ 2>&1 | less

# 3. Apply
2to3 -f print -w -n lib/    # -n skips .bak files since you're in git

# 4. Verify no statements remain
grep -rn '\bprint ' lib/ --include='*.py' | grep -v 'print('

# 5. Syntax check every file
find lib/ -name '*.py' | xargs python3 -m py_compile && echo "All OK"

# 6. Run tests
python -m pytest lib/
```

### Edge cases 2to3 handles correctly (that comby/sed would not)

| Python 2 pattern | Python 3 equivalent |
|-----------------|---------------------|
| `print "msg"` | `print("msg")` |
| `print "a", "b"` | `print("a", "b")` |
| `print "msg",` (suppress newline) | `print("msg", end="")` |
| `print >> sys.stderr, "msg"` | `print("msg", file=sys.stderr)` |
| `print` (bare, no args) | `print()` |

---

## pyupgrade — Modernize Python 3 Code

`pyupgrade` upgrades Python 3 code to use modern idioms. It is not about Python 2 → 3 —
it is about moving from old Python 3 style to current best practices. Use it on codebases
that are already Python 3 but were written a long time ago.

### Installation

```bash
pip install pyupgrade
# or: pipx install pyupgrade
```

### Usage

```bash
# Upgrade to minimum Python 3.8+ idioms
find lib/ -name '*.py' | xargs pyupgrade --py38-plus

# Upgrade to Python 3.10+ (adds match statement patterns, etc.)
find lib/ -name '*.py' | xargs pyupgrade --py310-plus

# Preview mode (dry run)
pyupgrade --py38-plus --check myfile.py
```

### What pyupgrade does

| Old style | Modern equivalent |
|-----------|------------------|
| `'hello %s' % name` | `f'hello {name}'` (f-strings) |
| `'{}'.format(x)` | `f'{x}'` |
| `from typing import List, Dict` | `list`, `dict` (built-in generics, 3.9+) |
| `Optional[X]` | `X \| None` (union syntax, 3.10+) |
| `super(Cls, self).__init__()` | `super().__init__()` |
| `six.text_type` | `str` |
| Old-style `u""` string prefixes | plain `""` |

### Combine with 2to3 for a full Python 2 → modern Python 3 migration

```bash
# Step 1: Migrate Python 2 → 3
2to3 -w -n lib/

# Step 2: Modernize Python 3 idioms
find lib/ -name '*.py' | xargs pyupgrade --py38-plus

# Step 3: Format
black lib/

# Step 4: Verify
python -m pytest lib/
```

---

## Reference Files

- **[references/hole-syntax.md](references/hole-syntax.md)** — Full comby hole type reference with examples for every variant
- **[references/language-matchers.md](references/language-matchers.md)** — All ~40 supported comby language matchers
