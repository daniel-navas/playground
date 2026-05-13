# 0001. Objective Scoring and Availability

## Status

Accepted

## Context

TFTOOL should recommend compositions using more than raw average placement.
The user wants recommendations that balance composition strength with whether the composition is realistically forceable in LAN.

Different ladder goals need different scoring behavior:

- Climbing needs consistency and availability.
- Playing for first needs high win-rate spike potential.
- Playing safely needs reliable top-four outcomes.

Fixed availability thresholds can become stale as the local meta shifts, so availability should be relative to the current LAN context.

## Decision

Use objective-specific scoring modes:

- `climb`: weighted performance plus availability.
- `first`: effective first-place probability, combining win rate with playability.
- `safe`: effective top-four probability, combining top-four rate with playability.

Use a dynamic availability model based on LAN composition pressure, LAN unit pressure, levelling timing pressure, and a relative confidence penalty.

Keep detailed formulas in `tftool/docs/scoring.md`.

## Consequences

The same composition can rank differently depending on the configured objective.
LAN contestation affects whether a strong composition is practical to force.
Scoring changes should be made carefully and verified against concrete examples.
Future scoring work should update both code and `tftool/docs/scoring.md`.
