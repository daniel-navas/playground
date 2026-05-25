# AI Project Context

This file is the root durable handoff context for AI coding agents working on this repository.
Read it before non-trivial work, then read the relevant mini-project context.

## Repository

This repository is a personal playground for small experiments and mini-projects.

Root-level context should stay small. Mini-project-specific rules, product notes, scoring models, API references, and workflow details should live inside each mini-project.

## Current Mini-Projects

- TFTOOL: a Python command-line tool for choosing Teamfight Tactics compositions.
  - Context: `tftool/docs/ai-context.md`
  - API reference: `tftool/docs/api.md`
  - Scoring reference: `tftool/docs/scoring.md`
  - Entry point: `python3 tftool.py`

## Structure

- `AGENTS.md`: repository-wide instructions for AI coding agents.
- `docs/ai-context.md`: lightweight root context and mini-project index.
- `docs/decisions/`: repository-level decision records.
- `<mini-project>/docs/ai-context.md`: durable context for a mini-project.
- `<mini-project>/docs/decisions/`: decision records for that mini-project.

## Conventions

- Repository files must be written in English.
- The user may speak Spanish in chat.
- Keep root documentation focused on the playground as a whole.
- Keep mini-project documentation close to the mini-project code.
- Avoid duplicate sources of truth.
- Prefer one config source, one run command, and one workflow per task.
- When a mini-project changes in a durable way, update that mini-project's `docs/ai-context.md`.
- When a decision needs rationale and history, add an ADR under the relevant `docs/decisions/` folder.

## Workflow Expectations

- Read `AGENTS.md` and this file before non-trivial work.
- Read the relevant mini-project context before touching that mini-project.
- Use `rg` for search.
- Use `apply_patch` for manual edits.
- Keep changes scoped to the mini-project unless the task is repository-wide.
- Preserve unrelated user changes in the worktree.
