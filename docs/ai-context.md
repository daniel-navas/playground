# AI Project Context

Read `AGENTS.md`, `docs/project.md`, and `docs/quality.md` for the stable project
rules. This file contains only current working state.

## Current Workspace

- `ts-blueprint/main.ts`: copyable TypeScript Hello World starting point.
- `py-blueprint/main.py`: copyable Python Hello World starting point.
- `veridooh/`: an existing TypeScript interview exercise workspace. Run
  `node veridooh/main.ts`; preserve it independently of root scratch work.
- No project dependencies, package installation, build step, or virtual
  environment are required for the current examples.
- Node.js 24 and Python 3 are installed in the owner's current environment.

The previous root examples now live in the blueprint folders. New work happens
in named copies; see `docs/project.md` for the copy-and-run workflow. Do not
reintroduce competing root scratch entrypoints or document every experiment.

TFTOOL lives in sibling `../tftool/` and has its own dependencies and context.
Do not recreate it here. An ignored `.venv` may remain from its earlier life in
Playground; the current scratch workflow does not depend on it.

## Context Routing

Blueprint and exercise work uses the root documentation. For a named exercise, inspect its
files and any local instructions first. Add exercise-local context only when
there is durable information worth preserving.
