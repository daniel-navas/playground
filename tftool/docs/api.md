# MetaTFT API reference

Base URL: https://api-hc.metatft.com

All endpoints return JSON. Unknown query params are ignored.

## tft-comps-api/comps_data

GET — Composition definitions (clusters, units, traits, items) for a queue.

Params:
  queue   (required)  e.g. 1100 (Ranked)

Response top-level: results, updated, tft_set, queue_id, cluster_id

Response results:
  results.data.cluster_details — map cluster id → composition object
  results.data.portals, results.data.cluster_id, results.data.tft_set
  results.games — game counts / metadata

cluster_details[id] fields:
  Cluster, centroid, units_string, traits_string, name, name_string
  top_headliner, overall (avg, count), stars, stars_4
  builds, build_items, top_itemNames, top_items, trends, top_augments
  diff_pick, diff_place, difficulty, levelling

Mission-critical:
  units_string — comma-separated unit IDs (champions in comp)
  stars — unit IDs typically 3-starred (9 copies); others 2-star (3 copies). Used for availability weighting.
  name_string — comp name, e.g. TFT16_Piltover, TFT16_Seraphine
  difficulty — numeric (negative = easier). Lower = easier.
  overall.avg — average placement (comps_data; less current than comps_stats)
  overall.count — total games (comps_data)

Note: Tier (S/A/B) is not in API; likely computed client-side from avg_place.

## tft-comps-api/comps_stats

GET — Composition statistics (placements, counts) for given filters.

Params:
  queue   (required)  e.g. 1100
  patch   (required)  e.g. current, 16.4
  days    (required)  e.g. 3
  rank    (required)  Comma-separated: CHALLENGER, DIAMOND, EMERALD, GRANDMASTER, MASTER, PLATINUM
  region  (optional)  Comma-separated: NA1, LA1, EUW1, etc. Omit = all.
  situational  (optional)  true = situational comps only
  permit_filter_adjustment  (optional)  true recommended

Response top-level: results, updated, tft_set, queue_id, cluster_id, filter_adjustment

filter_adjustment: override_applied (bool), rank_filter (string), sample_size (int). tftool prints it at top of output.

results[] — array of objects:
  cluster — cluster id (string or number). First entry may be empty/global.
  places — length 8 or 9: counts for 1st–8th; optional 9th = total.
  count — optional; total games for this cluster.

Derived in tftool: avg_place = weighted sum of places / count, win_rate = places[0]/count, top4_rate = sum(places[0:4])/count.

Pick rate by region: use region param (e.g. region=LA1). Pick rate = count / total_games (filter_adjustment.sample_size) * 100.

## tft-stat-api/units

GET — Per-unit placement counts and sample size (champion usage).

Params:
  queue, patch, days, rank  (required)  same style as comps_stats
  region  (optional)  Comma-separated platform codes
  permit_filter_adjustment  (optional)  true recommended

Response top-level: results, games, updated, tft_set, queue_id, filter_adjustment

results[]: unit (id), places (counts 1st–8th)
games[]: e.g. patch, b_patch_version, count — total games for usage %.

## tft-stat-api/games

GET — Game counts over time (per day, queue, rank).

Params:
  days  (optional)  e.g. 7

Response top-level: games, updated, patch, current_patch

games[]: day, srq, patch, count

## tft-comps-api/unit_items_processed

GET — Per-unit item performance (pick, avg placement, top item combos).

No query params used in tftool.

Response top-level: units, items, itemNames, updated, overall, tft_set, queue_id

## data.metatft.com/lookups/TFTSet17_latest_en_us.json

GET — Set metadata lookup (season-specific labels and references).

This endpoint is used for display and metadata, not ranking stats:
  - Unit display names (e.g. TFT17_IvernMinion -> Meepsie)
  - Unit cost metadata
  - Trait display names (e.g. TFT17_ManaTrait -> Conduit)
  - Trait effects/minUnits breakpoints (when needed for set-specific logic)

Headers:
  Browser-like headers are recommended (User-Agent + Referer) because data.metatft.com may reject generic clients.

Response top-level (observed):
  items, units, augments, traits, armory_items, augmentOdds, portals, encounters, roles, set17

units[] (observed keys):
  apiName, name, cost, traits, role, stats, ability, en_name, icon

traits[] (observed keys):
  apiName, name, desc, effects, units, en_name, icon

Important:
  URL is season-bound (TFTSet17). Update path for new sets.

## Region codes

Used as region (comma-separated) in comps_stats and units. tftool aliases in comps.SERVER_ALIASES: LAN→LA1, NA→NA1, EUW→EUW1, EUNE→EUN1, KR, JP→JP1, BR→BR1, OCE→OC1, TR→TR1, RU, TW→TW2, VN→VN2, SEA→SG2, ME→ME1.
