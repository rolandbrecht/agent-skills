---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing any code fixes
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues. As an AI agent, it is tempting to guess the solution based on symptoms because it is fast. **You must resist this temptation.**

**Core principle:** ALWAYS find the root cause before attempting fixes.
**The Iron Law:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

## When to Use

Use for ANY technical issue:

- Test failures
- Bugs in production or local development
- Build or CI pipeline failures
- Unexplained performance issues

**Do not skip this process even if:**

- The issue seems "simple" or "obvious"
- You are under time pressure
- The user asks for a "quick fix"

---

## Phase 1: Planning (Root Cause Investigation)

**BEFORE attempting ANY code modification or fix:**

1. **Read Error Messages Carefully**
   - Do not skim stack traces.
   - Note exact line numbers, file paths, and error codes.

2. **Reproduce and Isolate**
   - Can you trigger the bug reliably?
   - What are the exact steps?
   - If you cannot reproduce it, you must gather more data. Do not guess.

3. **Map the Boundaries (Multi-Component Systems)**
   - If the system has multiple layers (e.g., Frontend → API → Database), do not guess which layer failed.
   - **Inject telemetry:** Add `console.log`, `print()`, or logger statements at the boundary of each component.
   - Run the system once to see exactly what data entered and exited each layer.
   - *Reference:* `references/tracing.md` for boundary logging patterns.

4. **Trace the Data Flow**
   - Where did the bad value originate?
   - Trace backward up the call stack. Do not fix the symptom where the system crashed; find the source where the bad data was created.

---

## Phase 2: Execution (Hypothesis & Minimal Fix)

**Once the root cause is proven (not guessed):**

1. **Form a Single Hypothesis**
   - State clearly: *"I think X is the root cause because the logs showed Y."*

2. **Test Minimally**
   - Make the SMALLEST possible change to test your hypothesis.
   - Change exactly one variable at a time.
   - Do not bundle refactoring or "cleanups" into a bug fix.

3. **Create a Failing Test Case (If Possible)**
   - Write a minimal automated test that reproduces the bug *before* applying your fix.
   - If the test passes after your fix, you have proven resolution.

---

## Phase 3: Verification (The "3 Strikes" Rule)

1. **Verify the Fix**
   - Did your minimal change resolve the issue?
   - Did it break any adjacent tests?

2. **If the Fix Failed: STOP**
   - Undo your change. Do not stack fixes on top of failed fixes.
   - Re-evaluate your hypothesis.

3. **The 3 Strikes Rule**
   - If you have attempted 3 different fixes and the system is still failing, **STOP CHANGING CODE.**
   - You are likely fighting a fundamental architectural flaw or incorrect assumption, not a simple bug.
   - You must fill out the `references/bug-report.md` template and present it to the user for an architectural alignment discussion.

---

## Red Flags (When to STOP and Restart Phase 1)

If you catch yourself doing any of the following, you are violating the systematic debugging protocol. STOP and return to Phase 1:

- *"Quick fix for now, investigate later"*
- *"Let me just try changing X and see if it works"*
- Proposing solutions before tracing the data flow
- Applying 3 or more unrelated changes in a single fix attempt
- Encountering a new, unrelated bug every time you fix the previous one (indicates architectural rot)
