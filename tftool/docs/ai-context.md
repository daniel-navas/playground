# TFTOOL AI Context

This file is the durable handoff context for AI coding agents working on TFTOOL.
Read it before changing TFTOOL behavior, scoring, configuration, or documentation.

## Product

TFTOOL helps choose the best Teamfight Tactics composition based on multiple combined factors, not just one metric.

The goal is to find compositions that are easy, high-performing, and realistically forceable in LAN, with objective-specific ranking for climbing, playing for first, or playing safely for top 4.

## Current Stack

- Python.
- `requests` for MetaTFT HTTP calls.
- `PyYAML` for config loading.
- Configuration in `tftool/config.yaml`.
- Root launcher in `tftool.py`.

The correct run command from the repository root is:

```bash
python3 tftool.py
```

Use `.venv/bin/python` if the system Python does not have project dependencies installed.

## Data Sources

- MetaTFT API at `https://api-hc.metatft.com`.
- MetaTFT set lookup metadata at `https://data.metatft.com/lookups/TFTSet17_latest_en_us.json`.

TFTOOL fetches:

- Composition definitions from `tft-comps-api/comps_data`.
- Composition stats from `tft-comps-api/comps_stats`.
- LAN composition stats for availability.
- LAN unit stats for champion contestation.
- Set metadata for unit names, trait names, and unit costs.

API details live in `tftool/docs/api.md`.

## Product Rules

- Ranking should combine performance, availability, difficulty, reliability, and the configured objective.
- Difficulty label filters come from `tftool/config.yaml`.
- LAN is mapped to MetaTFT server code `LA1`.
- Unit and trait display names should come from MetaTFT lookup metadata when possible.
- Non-playable synthetic tokens should be excluded from display and unit-pressure calculations when metadata makes that possible.
- Seasonal unlockables can filter output to compositions that cover at least one pending unit or trait.
- Trait unlockables are computed from displayed champions through unit-to-traits metadata, not only from `traits_string`.
- Emblem signal is derived from `top_itemNames` plus overall average placement delta.
- `exclude_repeated_units_comps` is a temporary filter for duplicate-unit compositions while upstream augment/tag signals are unreliable.
- Do not activate half-baked situational or emblem heuristics without explicit user approval.

## Scoring Direction

Scoring details and formulas live in `tftool/docs/scoring.md`.

High-level direction:

- Performance uses global composition stats.
- Availability uses LAN composition contestation and LAN unit contestation.
- Availability should be dynamic within the current LAN context, not fixed to stale thresholds.
- Objective modes change how scores are weighted:
  - `climb`: consistency and forceability.
  - `first`: effective first-place probability.
  - `safe`: effective top-4 probability.
- If `max_avg_place` is set, sort by final score.
- If `max_avg_place` is not set, take the best performers by average placement and then prioritize availability inside that pool.

Scoring changes are sensitive. Treat them like balance patches: make small, measured changes and verify the specific scenario that motivated the change.

## Output

- Output is a terminal table.
- The table includes a resource health badge for:
  - `comps_data`
  - `comps_stats_primary`
  - `comps_stats_lan`
  - `units_lan`
- Table columns are configurable through `columns.*` in `tftool/config.yaml`.
- Composition labels include difficulty.
- Composition labels include an emblem trait name when an emblem signal exists.
- Champion lines use display order and may include covered seasonal unlockables.

## Workflow Expectations

- Keep TFT-related code and docs inside `tftool/` unless the task is repository-wide.
- Keep `tftool/docs/ai-context.md` updated when durable behavior, workflow expectations, scoring direction, or configuration surfaces change.
- Add an ADR under `tftool/docs/decisions/` for consequential TFTOOL decisions.
- Use `tftool/docs/api.md` for API reference.
- Use `tftool/docs/scoring.md` for scoring reference.
- Do not add overlapping entrypoints.
- Do not change import style just because a script was run from the wrong directory.
- When giving run instructions, prefer the single command `python3 tftool.py`.
