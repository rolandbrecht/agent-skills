# Agent Instructions

This project uses the `agent-skills` repository to enforce strict coding constraints and avoid common LLM pitfalls.

As an AI coding agent, you MUST follow these directives when working in this repository:

## 1. Architectural Changes & Refactoring

**Trigger:** ANY time you need to search for code structure, refactor symbols, analyze impact, find dead code, or trace dependencies. (e.g., "find all calls to fetch", "rename oldApi to newApi safely").
**Skill to use:** `ast-code-graph`
**Directive:** You MUST NOT use basic text search (`grep`) or guess at references for structural modifications. You must use this skill's `ast-grep` CLI instructions to parse the AST semantically, generate JSON outputs, and safely perform refactoring or impact analysis.

## 2. Debugging & Test Failures

**Trigger:** AUTOMATICALLY anytime you encounter a stack trace, test failure, production bug, or unexpected behavior.
**Skill to use:** `systematic-debugging`
**Directive:** You MUST NOT guess the solution or propose random fixes. You are constrained to the "No fixes without root cause" protocol. You must trace the error boundary, heavily utilize `grep_search` to understand context, and prove the failure with a reproduction script before any code modification. If 3 fixes fail, you MUST escalate and stop modifying code.

## 3. Post-Task Reflection

**Trigger:** ALWAYS at the end of complex tasks, debugging sessions, or when learning a new project codebase quirk.
**Skill to use:** `self-reflection`
**Directive:** You MUST trigger this skill before closing a complex task to codify hard-won lessons into reusable project rules (saving them to `CLAUDE.md`, `.cursorrules`, etc.). Future agents should not have to repeat your mistakes.
