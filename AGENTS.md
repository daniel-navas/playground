# Instructions for Codex

All project files must be written in English.

This includes file names, folder names, code, comments, documentation, UI copy, commit messages, test names, and any generated project text.

The user may speak Spanish in chat, but files in the repository must stay in English.

The user may use voice dictation. If a request has odd wording or likely transcription mistakes, infer the most likely meaning from context before asking for clarification.

This repository is a personal playground for small experiments and mini-projects. Keep root-level context light and route project-specific knowledge to each mini-project.

For non-trivial work, read `docs/ai-context.md` first, then read the relevant mini-project context listed there.

Each mini-project should keep its durable AI handoff context in `docs/ai-context.md` inside that mini-project folder.

Use `docs/decisions/` for repository-level decisions. Use `<mini-project>/docs/decisions/` for decisions that belong to one mini-project.

Keep context files updated when durable behavior, workflow expectations, scoring rules, configuration surfaces, or project direction changes.

Preserve user intent and the current project vibe. Keep configuration surfaces simple and centralized.

When giving run instructions, prefer extremely short answers with a single clearly highlighted command.

Do not change entrypoints or import styles just to match how the user ran a script. Tell them the correct command to run from the repository root.

Prefer one way to do each thing: one config source, one run command, one workflow. If the user specifies a way, use that; otherwise choose the single best way and avoid adding overlapping alternatives.

Before important changes, explain in one sentence what will be touched and why.

Use `rg` for search. Use `apply_patch` for manual edits.

Do not make destructive changes without clear permission from the user.
