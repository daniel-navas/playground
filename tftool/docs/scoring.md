# TFTOOL Scoring Reference

This file documents the current scoring model used to rank compositions.
It should match `tftool/comps.py`.

## Mission-Critical API Fields

From `comps_data` cluster details:

- `units_string`: comma-separated unit IDs in the composition.
- `stars`: unit IDs typically expected at 3-star.
- `stars_4`: unit IDs with 4-star signals. TFTOOL simplifies these as 3-star copy pressure for availability.
- `name_string`: raw composition name.
- `name`: structured composition label pieces.
- `traits_string`: raw trait activation string.
- `difficulty`: numeric difficulty signal.
- `levelling`: timing label such as `Fast 9`, `Fast 8`, `Standard`, or `lvl 6`.
- `overall.avg`: average placement from composition definitions.
- `overall.count`: total games from composition definitions.
- `top_itemNames`: item/emblem signal inputs.

From primary `comps_stats`:

- `places`: placement counts for first through eighth.
- `count`: games played.
- Derived `avg_place`: weighted average placement.
- Derived `win_rate`: first-place count divided by total count.
- Derived `top4_rate`: top-four count divided by total count.

From LAN `comps_stats`:

- `pick_rate_lan`: composition count divided by LAN sample size.
- LAN composition counts for relative confidence.

From LAN `units_distribution`:

- Per-unit pick rate in LAN, aggregated across item-count bins.

## Performance Score

Performance is a 0-100 score based on objective-specific weights over:

- `avg_place_score = ((8.0 - avg_place) / 7.0) * 100`
- `win_rate_score = win_rate`
- `top4_rate_score = top4_rate`

The average placement score maps:

- `1.0` to `100`
- `4.5` to `50`
- `8.0` to `0`

Objective profiles:

- `climb`: average placement `0.50`, win rate `0.15`, top-four rate `0.35`.
- `first`: average placement `0.15`, win rate `0.70`, top-four rate `0.15`.
- `safe`: average placement `0.30`, win rate `0.10`, top-four rate `0.60`.

## Availability Score

Availability is a 0-100 score based on a dynamic pressure model within the current LAN context.

Pressure inputs:

- Composition pressure: percentile rank of the composition pick rate in LAN.
- Unit pressure: weighted percentile rank of unit pick rates in LAN.
- Timing pressure: heuristic from the levelling label.
- Confidence penalty: relative penalty based on LAN sample percentile.

Pressure weights:

- Composition pressure: `0.35`.
- Weighted unit pressure: `0.45`.
- Timing pressure: `0.15`.
- Confidence penalty: `0.05`.

Final availability:

```text
availability_score = (1.0 - pressure_score) * 100
```

## Unit Pressure Weighting

Unit pressure weights copy needs and unit cost.

- Starred units from `stars` or `stars_4`: 9 copies total.
- Non-starred units: 3 copies per occurrence.
- Duplicate non-starred units increase copy pressure.
- Duplicate starred units are simplified to one 3-star requirement.
- Higher-cost units increase weight.

Cost weight:

```text
cost_weight = 1.0 + (clamped_cost - 1) * 0.25
```

Where `clamped_cost` is clamped from 1 to 5.

## Timing Pressure

Current timing heuristic:

- `Fast 9`: `0.35`
- `Fast 8`: `0.45`
- Labels starting with `lvl`: `0.65`
- Standard or unknown: `0.55`

Lower pressure means better availability.

## Final Objective Score

For `climb`:

```text
score = 0.75 * performance_score + 0.25 * availability_score
```

For `first`:

```text
p_playable = 0.35 + 0.65 * (availability_score / 100)
p_first_effective = (win_rate / 100) * p_playable
score = p_first_effective * 100
expected_games_to_first = 1 / p_first_effective
```

For `safe`:

```text
p_playable = 0.35 + 0.65 * (availability_score / 100)
p_top4_effective = (top4_rate / 100) * p_playable
score = p_top4_effective * 100
expected_games_to_top4 = 1 / p_top4_effective
```

## Filtering And Ordering

Filters:

- Exclude situational compositions unless situational mode is enabled.
- Exclude emblem compositions when `exclude_emblem_comps` is enabled and an emblem signal exists.
- Exclude duplicate-unit compositions with at least two repeated champions when `exclude_repeated_units_comps` is enabled.
- Exclude compositions above `max_avg_place` when configured.
- Apply difficulty label filters when configured.
- Apply seasonal unlockable filters when enabled.

Ordering:

- If `max_avg_place` is set, sort by final score descending.
- If `max_avg_place` is not set:
  - Take the top `limit` compositions by average placement.
  - Sort that pool by availability descending, then average placement, then score.

## Not In The API

Tier labels such as S, A, or B are not exposed by the MetaTFT API.
They appear to be computed client-side and are not used by TFTOOL.
