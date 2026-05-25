# 0001. Adopt Agent Context Structure

## Status

Accepted

## Context

This repository is a playground that may contain many small mini-projects.
The previous context structure used plain `.context` files:

- `REPO.context` for repository-level context.
- `<mini-project>/<name>.context` for mini-project context.

That structure was simple, but less aligned with common AI coding agent conventions and less discoverable by tools that look for Markdown project guidance.

A single root context file would not scale well because mini-project-specific details could make the root context too large and noisy.

## Decision

Use a modular Markdown-based context structure:

- `AGENTS.md` for repository-wide AI agent instructions.
- `docs/ai-context.md` for lightweight repository context and a mini-project index.
- `docs/decisions/` for repository-level decision records.
- `<mini-project>/docs/ai-context.md` for each mini-project's durable context.
- `<mini-project>/docs/decisions/` for mini-project decision records.

Mini-project context should stay close to the mini-project code. Root context should point agents to the correct deeper context instead of duplicating it.

## Consequences

New AI sessions can onboard from standard Markdown files.
The repository root stays lightweight even as more mini-projects are added.
Each mini-project can evolve its own context, technical references, and decision history.
Context files must be kept current to avoid stale guidance.
