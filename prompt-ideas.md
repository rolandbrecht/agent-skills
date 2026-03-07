# Prompt for Generating High-Leverage Agent Skills

Copy and paste this prompt into a fresh session to brainstorm new, high-value skills for LLM coding agents:

***

**System Prompt / Context:**
I am building a collection of "Agent Skills" (like `systematic-debugging` or `ast-code-graph`). These are prescriptive, constraint-based markdown files (`SKILL.md`) that teach LLM coding agents how to overcome their inherent flaws and work more reliably on complex codebases.

An ideal Agent Skill does NOT just say "write good code." It identifies a specific, known weakness of LLMs (e.g., losing context, writing insecure queries, guessing at bugs, breaking APIs) and enforces a strict methodology or introduces a specific CLI tool to solve it.

**The Request:**
Brainstorm 3-5 highly specific, new Agent Skill ideas.

For each idea, provide:

1. **The Name:** (e.g., `api-contract-enforcer`)
2. **The Problem:** Describe the specific LLM behavioral flaw or limitation this solves (What chaos does an unsupervised agent cause here?).
3. **The Skill:** The prescriptive methodology, strict checklist, or external tool the skill will use to enforce better behavior.
4. **How it helps:** The exact workflow the agent must execute before presenting a result to the user.

**Constraints for the ideas:**

- Do NOT suggest generic coding advice (e.g., "write clear comments" or "use DRY principles").
- Focus on areas where agents cause regressions, security gaps, architectural drift, or context-loss.
- Focus on systemic, industrial-grade workflows (e.g., enforcing backward compatibility, mandating ownership checks, managing token limits).
