# Agent Instructions

This project uses the `agent-skills` repository to enforce strict coding constraints and avoid common LLM pitfalls.

As an AI coding agent, you MUST follow these directives when working in this repository:

## 1. Architectural Changes & Refactoring

**Trigger:** When asked to rename APIs, strip dead code, or perform sweeping changes across multiple files.
**Skill to use:** `ast-code-graph`
**Directive:** You MUST NOT use basic text search (`grep`) or guess at references. You must use the `ast-grep` CLI or graph builder to find structural references and perform safe, AST-aware rewrites.

## 2. Debugging & Test Failures

**Trigger:** When asked to fix a bug, investigate a test failure, or debug unexpected behavior.
**Skill to use:** `systematic-debugging`
**Directive:** You MUST NOT guess the solution or propose random fixes. You are constrained to the "No fixes without root cause" protocol. You must trace the error boundary and prove the failure before any code modification. If 3 fixes fail, you must escalate using the 3-strike protocol.

## 3. Post-Task Reflection

**Trigger:** When concluding a complex debugging session, discovering a project-specific architecture rule, or writing a reusable bash script.
**Skill to use:** `self-reflection`
**Directive:** You are not a temporary worker. Over time, you must codify project-specific quirks and lessons learned into reusable rules (e.g., adding them to this `AGENTS.md` file) using the `self-reflection` protocol.
