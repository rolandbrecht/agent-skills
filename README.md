# Agent Skills

[![CI](https://github.com/rolandbrecht/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/rolandbrecht/agent-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A collection of shareable, high-quality AI coding agent skills and workflows. These skills provide structured guidance, recipes, and helper scripts to make LLM agents significantly more effective at complex codebase tasks.

## Why do agents need specialized skills?

While LLM agents have deep semantic understanding, they are fundamentally limited by their context windows and token constraints.

For example, when asked to **"rename an API across the project"** or **"find all dead code"**:

- **Without skills:** An agent must use error-prone text search (`grep`) which breaks on comments or formatting, or painstakingly open and read hundreds of files sequentially, burning through tokens and forgetting earlier context.
- **With skills (like `ast-code-graph`):** The agent is taught to use industrial-grade tools like [ast-grep](https://ast-grep.github.io/) to instantly perform mathematically sound, structural refactoring across thousands of files in a single step, while using deterministic graph builders to trace global dependencies without reading every file.

These skills provide the **industrial tools** that let an agent execute systemic changes safely, instantly, and globally.

## Skills

### [ast-code-graph](./ast-code-graph/)

AST parsing and code graph indexing for structural code search, refactoring, dead-code detection, dependency tracing, impact analysis, and safe symbol renaming.

**Primary tool:** [ast-grep](https://ast-grep.github.io/) for structural search and rewrite, with custom scripts for code graph analysis.

**Files:**

- `SKILL.md` — Main skill instructions
- `ast-grep-cheatsheet.md` — ast-grep CLI and pattern reference
- `graph-schema.md` — Code graph node/edge schema
- `query-patterns.md` — Query patterns cookbook
- `scripts/parse-js.mjs` — Cross-platform JS/TS AST parser
- `scripts/build-graph.py` — Python code graph builder

### [systematic-debugging](./systematic-debugging/)

Use when encountering any bug, test failure, or unexpected behavior. This skill forces the agent to use the scientific method—tracing root causes and injecting boundary telemetry—before attempting any code fixes. It includes a strict "3 Strikes" escalation protocol to prevent architecture-breaking guesswork.

**Files:**

- `SKILL.md` — The 3-phase systematic debugging framework
- `references/bug-report.md` — The 3-strike escalation template
- `references/tracing.md` — Actionable boundary-logging patterns (frontend, backend, DB, CI)

### [self-reflection](./self-reflection/)

A "meta-skill" executed at the end of complex tasks. It solves the LLM "stateless learner" problem by forcing the agent to codify its hard-won lessons into reusable YAML/Markdown rules before it is allowed to close a task.

**Files:**

- `SKILL.md` — The continuous improvement protocol
- `references/lesson-template.md` — Checklists for adding architectural gotchas to project instruction files

## Installation

### Via skills.sh (Recommended)

The easiest way to install these skills is using [skills.sh](https://skills.sh/).

```bash
# Example: Install the ast-code-graph skill
npx skills install github.com/rolandbrecht/agent-skills/ast-code-graph
```

### Manual Installation

You can also install skills manually by copying the skill directories into your platform's skills location.

**Claude Code:**

```bash
# User-level (available in all projects)
cp -r * ~/.claude/skills/

# Or project-level (shared via git)
mkdir -p .claude/skills
cp -r * .claude/skills/
```

**Gemini CLI / Antigravity:**

```bash
mkdir -p ~/.gemini/antigravity/skills
cp -r * ~/.gemini/antigravity/skills/
```

**OpenAI Codex:**

```bash
# User-level
mkdir -p ~/.codex/skills
cp -r * ~/.codex/skills/
```

## License

MIT
