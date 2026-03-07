---
name: self-reflection
description: Execute this meta-skill ALWAYS at the end of complex tasks, debugging sessions, or when learning a new project codebase quirk. You MUST trigger this skill to codify hard-won lessons into reusable project rules (saving them to llms.txt, .cursorrules, CLAUDE.md or a new SKILL.md). Do NOT close a complex task without running this skill to ensure future agents don't make the same mistakes you did!
---

# Self-Reflection (Continuous Improvement Protocol)

## Overview

AI coding agents are naturally "stateless." You might spend 2 hours debugging a complex Webpack configuration, a subtle race condition, or a confusing project directory layout, eventually fix it, and then completely "forget" the lesson when a new conversation starts.

The core goal of this skill is to turn you from a "temporary worker" into a "systematic documenter." 

**Core Principle:** Hard-won knowledge must be persisted. If a task was difficult because of an undocumented project quirk or architectural gotcha, you MUST write a rule so the *next* agent (or yourself in the future) doesn't repeat your mistakes.

## When to Use

You must trigger this protocol **automatically** before declaring a task "done" and notifying the user in the following scenarios:

- After successfully fixing a complex or confusing bug (especially if it took multiple attempts, required new context, or reading multiple files).
- After struggling with a framework configuration.
- After discovering a codebase-specific convention ("In this project, we always use `X` instead of `Y`").
- After creating a complex workflow or tool sequence that could be reused.

---

## The Protocol: How to Reflect

Before concluding your task, pause and answer these three questions internally:

1. **"Did I struggle with anything because I didn't know a project convention?"**
2. **"Did I encounter an architectural 'gotcha' that another agent will likely trip over tomorrow?"**
3. **"Did I write a custom CLI tool, `ast-grep` pattern, or bash script to solve this that I could reuse?"**

If the answer to *any* of the above is **"Yes"**, you MUST NOT just mention it to the user in chat. You must persist it to the codebase.

---

## Action: Codifying the Lesson

Based on your internal reflection, choose the appropriate output format below and write the rule. Try to generalize the lesson.

### 1. Project-Specific Rules (`llms.txt` / `.cursorrules` / `CLAUDE.md`)

Use this when you learned a specific convention for the current repository. 

*If none of these files exist yet, ask the user if they'd like you to create one (preferring `CLAUDE.md` or `llms.txt`).*

- **Example Good Lesson:** "When creating new API endpoints, ALWAYS include the `@require_tenant` decorator, and never return the raw SQLAlchemy model. Always use a Pydantic `UserOut` schema."
- **Example Bad Lesson (Too Specific):** "I fixed the `POST /users` route by adding `@require_tenant` to line 42."

**Action:** Append the rule to the local AI instruction file.

### 2. General Agent Skills (`skills/`)

Use this when you developed a multi-step workflow or a reliable, highly-reusable way to accomplish a complex task.

- **Example Good Lesson:** Creating a new skill called `safe-db-migration` that details the 5 exact steps required to pull the staging DB, run Alembic locally, and verify the downgrade path.
- **Example Bad Lesson:** Appending a 500-line bash script directly into `.cursorrules`.

**Action:** Create a new `SKILL.md` inside a dedicated `skills/[skill-name]/` directory. This gives future agents a prescriptive, step-by-step guide.

### 3. Reusable AST Rules (`.ast-grep/rules/` or similar linters)

Use this when you found an anti-pattern that you successfully removed and want to prevent from happening again.

- **Example Good Lesson:** "Developers keep using `console.log()` instead of our `LogEngine.track()`. I will create an ast-grep rule to flag this automatically."

**Action:** If the `ast-code-graph` skill is available (or `ast-grep` is installed), write a YAML rule to automatically flag or fix this in the future, and save it to the project's `.ast-grep/rules` directory.

---

## Final Review

Once you have codified the lesson into a permanent file, inform the user:

> "Task complete. I also noticed [X] was a recurring gotcha, so I have codified a rule for it in [File] to ensure future agents (and myself) handle it correctly."
