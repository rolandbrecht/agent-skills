# Comby Language Matchers

## How Matchers Work

Comby selects a parser based on file extension by default. Pass `-matcher .ext` to
override (useful when files lack extensions or use unusual ones).

Run `comby -list` to see the current list on your install.

## Supported Languages

| Language | Matcher flag | Common extensions |
|----------|-------------|-------------------|
| Assembly | `-matcher .s` | `.s`, `.asm` |
| Bash | `-matcher .sh` | `.sh`, `.bash` |
| C | `-matcher .c` | `.c` |
| C++ | `-matcher .cpp` | `.cpp`, `.cc`, `.cxx` |
| C# | `-matcher .cs` | `.cs` |
| Clojure | `-matcher .clj` | `.clj`, `.cljs` |
| CSS | `-matcher .css` | `.css` |
| Dart | `-matcher .dart` | `.dart` |
| Elixir | `-matcher .ex` | `.ex`, `.exs` |
| Elm | `-matcher .elm` | `.elm` |
| Erlang | `-matcher .erl` | `.erl` |
| Fortran | `-matcher .f` | `.f`, `.f90` |
| F# | `-matcher .fsx` | `.fsx`, `.fs` |
| Go | `-matcher .go` | `.go` |
| Haskell | `-matcher .hs` | `.hs` |
| HTML | `-matcher .html` | `.html`, `.htm` |
| Java | `-matcher .java` | `.java` |
| JavaScript | `-matcher .js` | `.js`, `.mjs`, `.cjs` |
| JSX | `-matcher .jsx` | `.jsx` |
| JSON | `-matcher .json` | `.json` |
| Julia | `-matcher .jl` | `.jl` |
| LaTeX | `-matcher .tex` | `.tex` |
| Lisp | `-matcher .lisp` | `.lisp`, `.el` |
| Nim | `-matcher .nim` | `.nim` |
| OCaml | `-matcher .ml` | `.ml`, `.mli` |
| Pascal | `-matcher .pas` | `.pas` |
| PHP | `-matcher .php` | `.php` |
| Python | `-matcher .py` | `.py` |
| Reason | `-matcher .re` | `.re` |
| Ruby | `-matcher .rb` | `.rb` |
| Rust | `-matcher .rs` | `.rs` |
| Scala | `-matcher .scala` | `.scala` |
| SQL | `-matcher .sql` | `.sql` |
| Swift | `-matcher .swift` | `.swift` |
| Plain text | `-matcher .txt` | `.txt`, `.md` |
| TSX | `-matcher .tsx` | `.tsx` |
| TypeScript | `-matcher .ts` | `.ts` |
| XML | `-matcher .xml` | `.xml` |

## Notes on Specific Languages

### JavaScript vs TypeScript vs JSX/TSX

These are separate matchers. If your project mixes `.js` and `.ts` files, you'll need
separate passes or use `rg -l` to pre-filter:

```bash
# TypeScript files only
comby 'import :[x] from ":[m]"' 'import type :[x] from ":[m]"' .ts -i

# All TS/TSX in one pass (process twice with different matchers)
comby 'import :[x] from ":[m]"' 'import type :[x] from ":[m]"' .ts -i
comby 'import :[x] from ":[m]"' 'import type :[x] from ":[m]"' .tsx -i
```

### Python

Comby does not model indentation as structure. Patterns that span indentation boundaries
(like a full `def` block with body) may produce unexpected results. Always use `-review`
or `-diff` before `-i` for Python refactors. For precise Python AST work, prefer
ast-code-graph with an AST-aware tool.

### Plain Text / Generic Matching

Use `-matcher .txt` when working with config files, Markdown, or any file format not
in the list above. This disables all language-specific comment/string handling and
treats the file as plain text.

```bash
# Update version strings in any config file
comby 'version: ":[v]"' 'version: "2.0.0"' .yml -i
comby '"version": ":[v]"' '"version": "2.0.0"' .json -i
```

### SQL

Comby understands SQL comment syntax (`--` and `/* */`) and string literals, making it
safer than regex for SQL migrations:

```bash
# Rename a table in all queries
comby 'FROM :[[old_table]]' 'FROM new_table_name' .sql -i
comby 'JOIN :[[old_table]]' 'JOIN new_table_name' .sql -i
```

## Custom Matchers

Define your own language grammar via a JSON config:

```bash
comby 'pattern' 'rewrite' -custom-matcher grammar.json
```

The JSON file specifies delimiters, comment syntax, string syntax, and escape characters.
Useful for proprietary config formats, DSLs, or template languages not in the built-in
list.
