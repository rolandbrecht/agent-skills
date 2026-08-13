# ast-grep CLI Reference

Verified against **ast-grep 0.45.1** (`--help` output). Flags can drift between versions — when a command rejects a flag, check `ast-grep <cmd> --help`. Web reference: <https://ast-grep.github.io/reference/cli>

The binary names `ast-grep` and `sg` are equivalent. Prefer `ast-grep` — some systems ship a different `sg` (shell group) binary.

## Contents

- [Flag syntax rules](#flag-syntax-rules)
- [ast-grep run](#ast-grep-run) · [scan](#ast-grep-scan) · [test](#ast-grep-test) · [new](#ast-grep-new) · [outline](#ast-grep-outline) · [lsp](#ast-grep-lsp) · [completions](#ast-grep-completions)
- [Exit codes](#exit-codes)
- [Supported languages](#supported-languages)

## Flag Syntax Rules

Flags with an **optional** value require `=`:

- `--json=compact` works. `--json compact` treats `compact` as a path.
- `--error=my-rule` works. `--error my-rule` sets ALL rules to error and treats `my-rule` as a path.
- Same for `--warning=`, `--info=`, `--hint=`, `--off=`, `--debug-query=`.

## Subcommand Overview

| Command | Purpose |
| --- | --- |
| `run` | One-time search or rewrite. This is the **default** command: `ast-grep -p '...'` equals `ast-grep run -p '...'`. |
| `scan` | Scan and rewrite code by YAML rule configuration. |
| `test` | Test ast-grep rules against test cases and snapshots. |
| `new` | Scaffold a new project, rule, test, or utility rule. |
| `outline` | Explore code structure: symbols, imports, exports, members. |
| `lsp` | Start a language server for editor diagnostics. |
| `completions` | Generate a shell completion script. |

---

## ast-grep run

```text
ast-grep run [OPTIONS] <--pattern <PATTERN>|--selector <KIND>|--strictness <STRICTNESS>|--kind <KIND>> [PATHS]...
```

Run a one-time search or rewrite. `PATHS` defaults to the current directory.

### Pattern options

| Flag | Description |
| --- | --- |
| `-p, --pattern <PATTERN>` | AST pattern to match. |
| `-r, --rewrite <FIX>` | String to replace the matched AST node. Can use metavariables from the pattern. |
| `-l, --lang <LANG>` | Language of the pattern. Inferred from file extensions if omitted. Required for `--stdin`. |
| `-k, --kind <KIND>` | AST kind to match instead of a pattern. Accepts ESQuery-style selectors (e.g. `call_expression > identifier`). |
| `--selector <KIND>` | AST kind that is the actual matcher inside the pattern (pattern-object style on the CLI). |
| `--strictness <S>` | Match algorithm strictness. Values: `cst`, `smart` (default), `ast`, `relaxed`, `signature`, `template`. Stricter matches less code. |
| `--debug-query[=<format>]` | Print the query's tree-sitter AST. Requires explicit `--lang`. Values: `pattern`, `ast`, `cst`, `sexp`. Use this to debug patterns that do not match. |
| `-c, --config <FILE>` | Path to project config. Default: `sgconfig.yml`. |

### Input options

| Flag | Description |
| --- | --- |
| `--stdin` | Read source code from standard input. |
| `--globs <GLOBS>` | Include or exclude paths by gitignore-style glob. Prefix `!` excludes: `--globs '!**/test/**'`. Repeatable; later globs win. |
| `--no-ignore <TYPE>` | Do not respect ignore files. Values: `hidden`, `dot`, `exclude`, `global`, `parent`, `vcs`. Repeatable. |
| `--follow` | Follow symbolic links. |

### Output options

| Flag | Description |
| --- | --- |
| `-i, --interactive` | Interactive edit session: confirm each rewrite (y/n). |
| `-U, --update-all` | Apply all rewrites without confirmation. |
| `--files-with-matches` | Print only paths with at least one match. Conflicts with `--interactive`, `--json`, `--update-all`. |
| `--json[=<STYLE>]` | Structured JSON output. Values: `pretty` (default), `stream` (one object per line), `compact`. **Must use `=`.** Each match object contains `file`, `range`, `text`, `lines`, `language`, `charCount`, and `metaVariables` (the captured metavariable bindings). |
| `-A, --after <NUM>` / `-B, --before <NUM>` / `-C, --context <NUM>` | Context lines. `-C` conflicts with `-A`/`-B`. |
| `--color <WHEN>` | Values: `auto` (default), `always`, `ansi`, `never`. |
| `--heading <WHEN>` | Print file name as heading. Values: `auto` (default), `always`, `never`. |
| `--inspect <G>` | Debug file/rule discovery (to stderr). Values: `nothing` (default), `summary`, `entity`. |
| `-j, --threads <NUM>` | Thread count. `0` (default) = auto. |

---

## ast-grep scan

```text
ast-grep scan [OPTIONS] [PATHS]...
```

Scan and rewrite code by rule configuration.

### Rule source options

| Flag | Description |
| --- | --- |
| `-c, --config <FILE>` | Path to project config. Default: `sgconfig.yml`. |
| `-r, --rule <FILE>` | Scan with a single rule file. No project setup needed. Conflicts with `--filter` and `--inline-rules`. |
| `--inline-rules <TEXT>` | Rules as inline YAML text. Separate multiple rules with `---`. Good for one-off complex rules without a file. |
| `--filter <REGEX>` | Run only rules whose ids match the regex. |

### Severity overrides

All of these **must use `=`** for the rule id. Without a value, they apply to all rules. Repeat the flag for multiple rules: `--error=rule-1 --error=rule-2`.

| Flag | Description |
| --- | --- |
| `--error[=<RULE_ID>...]` | Set rule(s) to error severity. |
| `--warning[=<RULE_ID>...]` | Set rule(s) to warning. |
| `--info[=<RULE_ID>...]` | Set rule(s) to info. |
| `--hint[=<RULE_ID>...]` | Set rule(s) to hint. |
| `--off[=<RULE_ID>...]` | Disable rule(s). |

**Input options:** same as `run` — `--stdin`, `--globs`, `--no-ignore`, `--follow`.

### Scan output options

| Flag | Description |
| --- | --- |
| `-i, --interactive` | Interactive fix session. |
| `-U, --update-all` | Apply all fixes without confirmation. |
| `--files-with-matches` | Print only paths with at least one match. |
| `--max-results <NUM>` | Stop after NUM results. |
| `--json[=<STYLE>]` | JSON output: `pretty`, `stream`, `compact`. **Must use `=`.** |
| `--include-metadata` | Include rule metadata in JSON output (requires `--json`). |
| `--format <FORMAT>` | CI output format. Values: `github` (workflow annotations), `sarif`. |
| `--report-style <S>` | Diagnostic style. Values: `rich` (default), `medium`, `short`. |
| `-A/-B/-C <NUM>` | Context lines, as in `run`. |
| `--color <WHEN>`, `--inspect <G>`, `-j <NUM>` | As in `run`. |

---

## ast-grep test

```text
ast-grep test [OPTIONS]
```

Test rules against `valid`/`invalid` test cases and snapshots.

| Flag | Description |
| --- | --- |
| `-c, --config <FILE>` | Path to project config YAML. |
| `-t, --test-dir <DIR>` | Directories that contain test files. |
| `--snapshot-dir <DIR>` | Snapshot directory. Default: `__snapshots__`. |
| `-f, --filter <REGEX>` | Filter test cases by **regex** (not glob). |
| `-i, --interactive` | Review and select snapshot updates interactively. |
| `-U, --update-all` | Update all changed snapshots. |
| `--skip-snapshot-tests` | Only check pass/fail, ignore snapshots. |
| `--include-off` | Also test rules with `severity: off` (skipped by default). |
| `--follow` | Follow symbolic links. |
| `--color <WHEN>` | As in `run`. |

---

## ast-grep new

```text
ast-grep new [OPTIONS] [NAME] [COMMAND]
```

Scaffold new items. Subcommands: `project`, `rule`, `test`, `util`. `NAME` is the id of the item to create.

| Flag | Description |
| --- | --- |
| `-l, --lang <LANG>` | Language of the new item (for `rule` and `util` only). |
| `-y, --yes` | Accept all defaults, no interactive prompts. |
| `-c, --config <FILE>` | Path to project config. |

Typical flow: `ast-grep new project` creates `sgconfig.yml` plus `rules/`, `rule-tests/`, `utils/` folders. Then `ast-grep new rule my-rule -l ts -y` adds a rule.

---

## ast-grep outline

```text
ast-grep outline [OPTIONS] [PATHS]...
```

Explore code structure: symbols, imports, exports, and members. Use this before you read full source files.

| Flag | Description |
| --- | --- |
| `--items <ITEMS>` | Top-level item selection. Values: `auto` (default: `structure` for files/stdin, `exports` for directories), `structure`, `exports`, `imports`, `all`. |
| `--view <VIEW>` | Presentation. Values: `auto` (default: `digest` for files/stdin, `names` for directories), `names`, `signatures`, `digest`, `expanded`. |
| `--match <REGEX>` | Filter items by regex on name, signature, and first source line. Case-sensitive. |
| `--type <T[,T...]>` | Filter by symbol type, lower camel case: `class`, `function`, `struct`, `enumMember`, ... |
| `--pub-members` | Show only public members (digest/expanded views). |
| `--outline-rules <FILE>` | Load custom outline extractor definitions. |
| `--no-default-outline-rules` | Disable bundled extractors. |
| `-l, --lang <LANG>` | Input language. Required for stdin. |
| `-c, --config <FILE>` | Project config. Default: `sgconfig.yml`. |
| `--stdin`, `--globs`, `--no-ignore`, `--follow`, `-j` | As in `run`. |
| `--json[=<STYLE>]`, `--color <WHEN>` | As in `run`. |

Examples:

```bash
ast-grep outline src/parser.ts --match Parser --type class
ast-grep outline crates --type struct,enum,interface --view names
cat src/parser.ts | ast-grep outline --stdin --lang ts
```

---

## ast-grep lsp

```text
ast-grep lsp [-c <CONFIG_FILE>]
```

Start a language server that reports rule diagnostics. Requires a project with `sgconfig.yml`. Used by editor extensions.

## ast-grep completions

```text
ast-grep completions [SHELL]
```

Generate a shell completion script. Shells: `bash`, `zsh`, `fish`, `elvish`, `powershell`. The shell is inferred if omitted.

---

## Exit Codes

Verified on 0.45.1:

| Code | Meaning |
| --- | --- |
| 0 | `run`: at least one match. `scan`: no error-severity diagnostics. |
| 1 | `run`: no match found. `scan`: error-severity diagnostics found. |
| 2 | CLI usage error (unknown flag, invalid flag value). |
| 8 | Invalid pattern or rule (e.g. multiple root nodes, rule without kind). |

In pipelines the last command's status wins. Set `set -o pipefail` when the ast-grep status matters.

---

## Supported Languages

Values for `-l, --lang` and the `language` field in YAML rules.

| Language | Alias(es) | Default extensions |
| --- | --- | --- |
| Bash | `bash` | sh, bash, zsh, ksh, env, ... |
| C | `c` | c, h |
| C++ | `cpp`, `cc`, `c++`, `cxx` | cc, cpp, hpp, hh, cxx, cu, ino |
| C# | `cs`, `csharp` | cs |
| CSS | `css` | css |
| Elixir | `ex`, `elixir` | ex, exs |
| Go | `go`, `golang` | go |
| Haskell | `hs`, `haskell` | hs |
| HCL | `hcl` | hcl |
| HTML | `html` | html, htm, xhtml |
| Java | `java` | java |
| JavaScript | `js`, `javascript`, `jsx` | js, mjs, cjs, jsx |
| JSON | `json` | json |
| Kotlin | `kotlin`, `kt` | kt, ktm, kts |
| Lua | `lua` | lua |
| Nix | `nix` | nix |
| PHP | `php` | php |
| Python | `py`, `python` | py, py3, pyi, bzl |
| Ruby | `rb`, `ruby` | rb, rbw, gemspec |
| Rust | `rs`, `rust` | rs |
| Scala | `scala` | scala, sc, sbt |
| Solidity | `sol`, `solidity` | sol |
| Swift | `swift` | swift |
| TypeScript | `ts`, `typescript` | ts, cts, mts |
| TSX | `tsx` | tsx |
| YAML | `yml` | yml, yaml |

Notes:

- TypeScript and TSX are **separate** languages. For React codebases, run patterns with both `-l ts` and `-l tsx`.
- Map non-standard extensions (e.g. `.vue`, `.svelte`) to a language with `languageGlobs` in `sgconfig.yml`.
