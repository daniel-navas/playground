# 0004. Copyable Language Blueprints

## Status

Accepted

## Context

The owner wants an individual block for each interview or experiment, created
by copying and renaming a folder that already contains Hello World. Shared root
scratch files do not make that workflow clear.

## Decision

Move the minimal root examples into `ts-blueprint/` and `py-blueprint/`.
Keep each blueprint limited to its runnable `main` file. Create independent
named copies for work and execute their entrypoints directly from the repository
root with Node.js 24 or Python 3. Preserve the existing `veridooh/` exercise.

## Consequences

Copy/paste creates a new block without installation or generation tooling.
Each block can grow helper files without affecting other blocks. Blueprints
remain clean starting points; changes to them do not modify existing copies.
The earlier root scratch entrypoints are replaced rather than kept as a second
workflow.
