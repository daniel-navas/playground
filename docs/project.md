# Playground

## Purpose

A personal local workspace primarily for live coding interviews, usually in
TypeScript and occasionally in Python. The owner needs to open a file, write
code, run it immediately, and inspect the output with minimal setup.

The secondary use is small disposable experiments: trying a loop syntax,
language feature, algorithm, or short code idea.

This documentation is durable context for coding agents helping the owner.
It is not intended as a public-facing repository presentation.

## Workflow

Keep both languages in one repository. TypeScript is the default when a new
exercise has no specified language. Use Python when the owner or interview
requires it. Start each interview or experiment by copying its language blueprint
folder and renaming the copy. Copy/paste in the file manager or editor is enough;
there is no project generator or shared launcher.

| Language | Blueprint | Command for a copy named `my-interview`, from the repository root |
| --- | --- | --- |
| TypeScript | `ts-blueprint/` | `node my-interview/main.ts` |
| Python | `py-blueprint/` | `python3 my-interview/main.py` |

For example, `cp -R ts-blueprint my-interview` creates a new TypeScript block.
Choose an unused destination name. Each blueprint contains only a runnable
Hello World `main` file. Keep the blueprints as clean starting points and write
exercise code in copies. Copies do not import from blueprints or one another.

Each entrypoint has a concise top-of-file command labeled `Run (Playground root)`.
Place the `main` definition first, followed by `helloWorld` (TypeScript) or
`hello_world` (Python), and invoke `main` at the bottom. In Python, keep the
invocation inside the standard `if __name__ == "__main__"` guard so all helper
definitions have executed before the call. This ordering is a readability
preference, not a universal style requirement. Avoid comments that explain
obvious editing steps or how to rename a copied folder.

Use Node.js 24 for direct execution of TypeScript with erasable type syntax.
This execution removes types; it does not type-check the program. Avoid syntax
requiring TypeScript compilation, such as enums and parameter properties, in the
default scratch workflow. Do not add a compiler or runner unless a concrete
exercise needs one.

Python examples use the standard library by default. Add external dependencies
only for a specific need, isolated to the exercise that needs them.

Each named folder is an individual working block, like the existing `veridooh/`.
Add helper files inside that block as needed. Preserve its contents unless the
owner requests a reset. Reuse an existing experiment block for tiny throwaway
checks when convenient; do not require a documentation set for every block.

## Constraints

- Prioritize a short edit-run-output loop and readable code under interview
  time pressure.
- Keep setup lightweight. Current blueprints require no dependencies,
  build, server, or environment activation.
- Do not add an app UI, language selector, generalized launcher, monorepo tools,
  or separate repositories for these two language workflows.
- Do not assume an editor or add editor-specific launch settings unless requested.
- Prefer one execution workflow per language over overlapping shortcuts.
- Follow the requested interview assistance level and problem scope.
- A growing independent application belongs in its own project when the owner
  chooses to extract it, as happened with TFTOOL.
