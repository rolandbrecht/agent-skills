# Lesson Template (for `.cursorrules` / `llms.txt`)

When a project-specific convention or architectural "gotcha" causes friction, the agent must document it using this format to guarantee future agents recognize and adhere to it.

Append these entries to the project's LLM instruction file (e.g., `.cursorrules`, `CLAUDE.md`, or `llms.txt`).

## The Format

```markdown
### 🧠 Lesson Learned: [Short Title of the Gotcha]

**The Trap:**
[Briefly describe the intuitive-but-wrong approach that an LLM will naturally want to take. E.g., "Agents will try to use the standard DB `DELETE` command when asked to remove a user."]

**The Correct Protocol:**
[State the exact, strict convention that must be used instead. E.g., "In this project, we NEVER hard-delete. You must set `deleted_at = NOW()` and `status = 'archived'` using the `SoftDeleteRepository`."]

**Trigger:**
[When should future agents apply this rule? E.g., "Apply this whenever modifying database records or writing migration scripts."]
```

## Example Application

```markdown
### 🧠 Lesson Learned: React State & Race Conditions
**The Trap:** 
When updating the user profile, agents frequently attempt to fetch the old state, mutate it, and send it back, leading to race conditions from stale closures.

**The Correct Protocol:**
You must ALWAYS use the functional state update pattern `setProfile(prev => ({ ...prev, newField }))` rather than `setProfile(newField)`.

**Trigger:** 
Anytime a React component's state depends on the previous render cycle state.
```
