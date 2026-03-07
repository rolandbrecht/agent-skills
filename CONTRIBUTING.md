# Contributing to Agent Skills

Thanks for your interest in contributing! This repository is driven by community contributions of valuable AI coding agent skills.

## What makes a good skill?

A good agent skill should:

1. Fix exactly ONE problem or scenario.
2. Be **highly prescriptive** ("Do this", "Don't do that") rather than descriptive.
3. Be fully self-contained in a directory.
4. Provide verifiable examples.

## Adding a new skill

1. Create a new directory for your skill (e.g., `systematic-debugging`).
2. Add a `SKILL.md` file in the root of your directory containing your instructions.
3. *Optional*: Add a `scripts/` directory if your skill requires helper runtimes.
4. Create a PR with your changes!

### SKILL.md Template

```markdown
---
name: your-skill-name
description: Brief description of when the agent should use this skill
---

# Skill Name

## Overview
Why this skill exists and the core philosophy.

## When to Use
List specific triggers/scenarios when the agent MUST adopt this paradigm.

## Phase 1: Planning
...

## Phase 2: Execution
...
```

## Running Tests

If you modify scripts within a skill, make sure to add tests and run them locally:

```bash
# JS tests
node --test tests/test-*.mjs

# Python tests
python3 -m unittest discover tests -v
```
