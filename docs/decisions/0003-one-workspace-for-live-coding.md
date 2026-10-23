# 0003. One Workspace for Live Coding

## Status

Accepted. The root scratch-file layout is superseded by
`0004-copyable-language-blueprints.md`; the single-repository decision remains.

## Context

Playground's primary use is live coding interviews in TypeScript or Python.
It also supports tiny language experiments. Both uses need minimal setup and
immediate execution. The owner wants durable documentation for coding agents,
following the purpose, current-state, and verification split used in sibling
projects.

## Decision

Keep one Playground with a root scratch file per language: `main.ts` and
`main.py`. Run them directly with Node.js 24 and Python 3. Use TypeScript by
default and preserve named exercises separately when needed.

Keep agent instructions in `AGENTS.md`, stable purpose in `docs/project.md`,
current state in `docs/ai-context.md`, and verification policy in
`docs/quality.md`. Exercise-local context remains optional and proportional.

## Consequences

Switching languages does not require another repository or a language-selection
tool. The default examples need no dependencies or build step. Node execution
does not type-check TypeScript, and compilation-only syntax is outside the
default workflow. Specific exercises can justify additional tooling later.
