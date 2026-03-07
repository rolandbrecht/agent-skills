---
name: self-reflection
description: A mandatory meta-skill to be executed at the end of complex tasks or debugging sessions to codify hard-won lessons into reusable project rules.
---

# Self-Reflection (Continuous Improvement Protocol)

## Overview

AI coding agents are naturally "stateless." You might spend 2 hours debugging a complex Webpack configuration or a subtle race condition, eventually fix it, and then completely "forget" the lesson when a new conversation starts.

The goal of this skill is to turn you from a "temporary worker" into a "systematic documenter."

**Core Principle:** Hard-won knowledge must be persisted. If a task was difficult because of an undocumented project quirk or architectural gotcha, you must write a rule so the *next* agent doesn't repeat your mistakes.

## When to Use

You must trigger this protocol **automatically** before declaring a task "done" and notifying the user in the following scenarios:

- After successfully fixing a complex bug (especially if it took multiple attempts).
- After struggling with a framework configuration.
- After discovering a codebase-specific convention ("In this project, we always use X instead of Y").

## The Protocol

Before concluding your task, answer these three questions internally:

1. **"Did I struggle with anything because I didn't know a project convention?"**
2. **"Did I encounter an architectural 'gotcha' that another agent will likely trip over tomorrow?"**
3. **"Did I write a custom CLI tool, `ast-grep` pattern, or bash script to solve this that I could reuse?"**

---

## Action: Codifying the Lesson

If the answer to any of the above is **"Yes"**, you MUST NOT just mention it to the user in chat. You must persist it to the codebase.

Choose the appropriate output format:

### 1. Project-Specific Rules (`llms.txt` / `.cursorrules` / `CLAUDE.md`)

If you learned a project specific convention (e.g., "Always use `logger.info`, never `console.log`" or "The `User` model requires a `tenant_id` on creation"):

- **Action:** Append the rule to the local AI instruction file (`llms.txt`, `.cursorrules`, etc.).
- *Format:* See `references/lesson-template.md` for standard phrasing.

### 2. General Agent Skills (`skills/`)

If you developed a multi-step workflow or a reliable way to accomplish a complex task (e.g., "How to safely migrate our legacy database schema"):

- **Action:** Create a new `SKILL.md` inside a dedicated `skills/[skill-name]/` directory.
- This gives future agents a prescriptive, step-by-step guide.

### 3. Reusable AST Rules (`.ast-grep/rules/` or similar linters)

If you found an anti-pattern that you successfully removed (e.g., "Hardcoded API URLs"):

- **Action:** If the `ast-code-graph` skill is available, write an `ast-grep` YAML rule to automatically flag or fix this in the future, and save it to the project's rule folder.

## Final Review

Once you have codified the lesson into a permanent file, inform the user:
> "Task complete. I also noticed [X] was a recurring gotcha, so I have codified a rule for it in [File] to ensure future agents (and myself) handle it correctly."
