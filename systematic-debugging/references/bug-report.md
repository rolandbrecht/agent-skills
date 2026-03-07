# The "3 Strikes" Escalation Report

If you (the agent) have attempted **3 separate fixes** for a single bug and the system is still failing, you must stop modifying code.

Continuing to guess will likely entangle the architecture, introduce regressions, and waste time.

Instead, fill out the markdown template below and present it to the user. This forces a step back from symptom-chasing to evaluate if there is a fundamental architectural flaw or misunderstanding of the requirements.

---

## Copy and fill out the section below

```markdown
🚨 **Systematic Debugging: 3-Strikes Limit Reached** 🚨

I have attempted 3 different minimal fixes for this issue, and none have resolved the root cause without side effects. Per the systematic debugging protocol, I am escalating this to you to determine if we are fighting an architectural flaw.

### The Original Symptom
[1-2 sentences describing what is breaking]

### The Fixes Attempted
1. **Hypothesis 1:** [What I thought was wrong]
   **The Fix:** [What I changed]
   **Why it failed:** [What the result was]
2. **Hypothesis 2:** ...
3. **Hypothesis 3:** ...

### The Underlying Tension
[Explain the fundamental conflict. e.g., "The UI requires synchronous state updates, but the database wrapper strictly returns Promises. Every attempt to wrap the async call is creating race conditions in the React rendering cycle."]

### Proposed Paths Forward
Option A: [A larger refactor to address the actual correct pattern]
Option B: [A recognized compromise or hack, with explicit acknowledgment of the tech debt]

How would you like to proceed?
```
