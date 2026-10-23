# Quality and Verification

Verification should support quick experiments, not slow them down with a
production application workflow.

## Runnable Workspace

After changing a language entrypoint or its execution setup, run the documented
command from the repository root and check the exit status and output:

- TypeScript blueprint: `node ts-blueprint/main.ts`.
- Python blueprint: `python3 py-blueprint/main.py`.

After changing a blueprint, also copy it into a temporary exercise folder and
run the copy's entrypoint from the repository root. Confirm it works without
imports or configuration from the original folder. Remove only that temporary
verification copy afterward.

After changing a named exercise, run that exercise's documented command. Check
only affected languages unless the shared workspace setup changed.

Running TypeScript directly does not prove type correctness. Distinguish runtime
execution from type-checking in verification reports.

## Exercises and Experiments

For a small syntax experiment, inspecting the output is normally enough. For an
algorithm or interview problem, check representative inputs and relevant edge
cases, such as empty input, duplicates, and boundary values. Use the problem's
actual expected behavior rather than adding a general test framework by default.

Do not write tests that only repeat a trivial example's implementation. Add
focused regression checks for durable, reproducible behavior when useful.

## Documentation and Delivery

Keep paths and commands accurate, and update the narrow authoritative document
when a change makes it stale. Inspect the diff for unintended changes. Preserve
existing exercises, unrelated work, and private state.

Report what was run and any material limitation. Do not claim an editor Play
button was verified when only terminal execution was checked.
