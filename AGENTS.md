# Instructions for AI Agents

All project files must be written in English, including file names, code,
comments, documentation, UI copy, commit messages, and test names. The owner may
speak Spanish and use voice dictation. Infer likely transcription errors from
context before asking for clarification.

## Start Here

For non-trivial work, read:

1. `docs/project.md` for purpose, scope, and constraints.
2. `docs/ai-context.md` for the current working state.
3. `docs/quality.md` for verification expectations.
4. Relevant exercise-local context and `docs/decisions/` when needed.

## Working Principles

- Optimize for quickly writing and running code during live coding interviews.
- Start individual work in a named copy of `ts-blueprint/` or `py-blueprint/`.
  Keep blueprints clean and exercise files local to their own block.
- Make the smallest coherent change that meets the current request.
- Treat an explicit implementation request as authorization to proceed within
  scope. Ask only when a missing decision materially affects the result.
- Before important changes, explain in one sentence what will be touched and why.
- Preserve the owner's current exercise and unrelated local changes. Never reset
  scratch files or delete an exercise without clear permission.
- Prefer one way to run each language. Give a single highlighted command for the
  relevant file, run from the repository root.
- Do not change entrypoints or imports merely to accommodate an incorrect run
  command. Explain the correct command instead.
- Avoid dependencies, abstractions, and infrastructure for hypothetical needs.
- Use `rg` for search and `apply_patch` for manual edits.
- Keep answers concise and verify claims before reporting success.

## Durable Project Memory

Repository files are the handoff between chats:

- `docs/project.md`: stable purpose, supported workflow, and constraints.
- `docs/ai-context.md`: short current-state index and handoff notes.
- `docs/quality.md`: proportional verification policy.
- `docs/decisions/`: consequential decisions and rationale.
- `<exercise>/docs/ai-context.md`: exercise-specific context, only when useful.

Keep documentation oriented toward agents continuing the work. A public-facing
project presentation is unnecessary. Keep the README as a short entrypoint.
Update the authoritative source when behavior changes; avoid duplicating rules
or recording a chronological diary. Store reusable lessons from owner corrections
in the narrowest appropriate source. Do not rely on another chat's history.

During a live coding exercise, follow the requested level of assistance. Do not
expand the problem, replace the owner's approach, or solve beyond the request.
