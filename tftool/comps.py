from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
import yaml


ROOT = Path(__file__).resolve().parent
META_BASE_URL = "https://api-hc.metatft.com"
UNITS_URL = f"{META_BASE_URL}/tft-stat-api/units"
UNITS_DISTRIBUTION_URL = f"{META_BASE_URL}/tft-stat-api/units_distribution"
GAMES_URL = f"{META_BASE_URL}/tft-stat-api/games"
COMPS_DATA_URL = f"{META_BASE_URL}/tft-comps-api/comps_data"
COMPS_STATS_URL = f"{META_BASE_URL}/tft-comps-api/comps_stats"
# Season-specific MetaTFT lookup payload. Update set id when season changes.
METATFT_SET_LOOKUP_URL = "https://data.metatft.com/lookups/TFTSet17_latest_en_us.json"

DEFAULT_RANK = "CHALLENGER,DIAMOND,EMERALD,GRANDMASTER,MASTER,PLATINUM"

# Alias -> MetaTFT API region code (matches client server list). Unlisted keys passed through as-is.
SERVER_ALIASES = {
    "BR": "BR1",
    "EUNE": "EUN1",
    "EUW": "EUW1",
    "JP": "JP1",
    "KR": "KR",
    "LAN": "LA1",
    "LAS": "LA2",
    "ME": "ME1",
    "NA": "NA1",
    "OCE": "OC1",
    "RU": "RU",
    "SEA": "SG2",
    "TR": "TR1",
    "TW": "TW2",
    "VN": "VN2",
}

CONFIG_PATH = ROOT / "config.yaml"
_TRAIT_DISPLAY_NAME_CACHE: Dict[str, str] | None = None
_UNIT_COST_CACHE: Dict[str, int] | None = None
_UNIT_NAME_CACHE: Dict[str, str] | None = None
_UNIT_TRAITS_CACHE: Dict[str, List[str]] | None = None
_METATFT_LOOKUP_CACHE: Dict[str, Any] | None = None


def _clean_tft_token(value: str) -> str:
    """Strip TFT set prefix from API tokens, e.g. TFT17_Viktor -> Viktor."""
    return re.sub(r"^TFT\d+_", "", (value or "").strip())


def _get_metatft_set_lookup() -> Dict[str, Any]:
    """Fetch MetaTFT set lookup payload (season-specific metadata)."""
    global _METATFT_LOOKUP_CACHE
    if _METATFT_LOOKUP_CACHE is not None:
        return _METATFT_LOOKUP_CACHE
    try:
        # This host may require browser-like headers.
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.metatft.com/",
            "Accept": "application/json, text/plain, */*",
        }
        resp = requests.get(METATFT_SET_LOOKUP_URL, headers=headers, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            _METATFT_LOOKUP_CACHE = data
        else:
            _METATFT_LOOKUP_CACHE = {}
    except Exception:
        _METATFT_LOOKUP_CACHE = {}
    return _METATFT_LOOKUP_CACHE


def get_unit_display_name(unit_id: str) -> str:
    """Return user-friendly champion name for a TFT unit id."""
    _, unit_name_map = _get_unit_meta_maps()
    return unit_name_map.get((unit_id or "").strip(), _clean_tft_token(unit_id))


def _get_trait_display_name_map() -> Dict[str, str]:
    """Return trait API id -> display name (e.g. TFT17_ManaTrait -> Conduit)."""
    global _TRAIT_DISPLAY_NAME_CACHE
    if _TRAIT_DISPLAY_NAME_CACHE is not None:
        return _TRAIT_DISPLAY_NAME_CACHE

    # Prefer season lookup from MetaTFT (same ecosystem as comps endpoints).
    lookup = _get_metatft_set_lookup()
    traits = lookup.get("traits", []) if isinstance(lookup, dict) else []
    out: Dict[str, str] = {}
    if isinstance(traits, list):
        for t in traits:
            if not isinstance(t, dict):
                continue
            api_id = str(t.get("apiName", "")).strip()
            display = str(t.get("name", "")).strip()
            if api_id and display:
                out[api_id] = display
    _TRAIT_DISPLAY_NAME_CACHE = out
    return _TRAIT_DISPLAY_NAME_CACHE


def _get_unit_meta_maps() -> tuple[Dict[str, int], Dict[str, str]]:
    """Return (unit_cost_map, unit_name_map) keyed by short API id (e.g. TFT17_Viktor)."""
    global _UNIT_COST_CACHE, _UNIT_NAME_CACHE
    if _UNIT_COST_CACHE is not None and _UNIT_NAME_CACHE is not None:
        return _UNIT_COST_CACHE, _UNIT_NAME_CACHE

    lookup = _get_metatft_set_lookup()
    units = lookup.get("units", []) if isinstance(lookup, dict) else []
    if isinstance(units, list):
        out_cost: Dict[str, int] = {}
        out_name: Dict[str, str] = {}
        for u in units:
            if not isinstance(u, dict):
                continue
            short_id = str(u.get("apiName", "")).strip()
            if not short_id:
                continue
            display_name = str(u.get("name", "")).strip()
            if display_name:
                out_name[short_id] = display_name
            cost = u.get("cost")
            try:
                if cost is not None:
                    out_cost[short_id] = int(cost)
            except Exception:
                pass
        _UNIT_COST_CACHE = out_cost
        _UNIT_NAME_CACHE = out_name
        return _UNIT_COST_CACHE, _UNIT_NAME_CACHE

    _UNIT_COST_CACHE = {}
    _UNIT_NAME_CACHE = {}

    return _UNIT_COST_CACHE, _UNIT_NAME_CACHE


def _get_unit_traits_map() -> Dict[str, List[str]]:
    """Return unit API id -> list of user-facing trait names from MetaTFT lookup."""
    global _UNIT_TRAITS_CACHE
    if _UNIT_TRAITS_CACHE is not None:
        return _UNIT_TRAITS_CACHE

    lookup = _get_metatft_set_lookup()
    units = lookup.get("units", []) if isinstance(lookup, dict) else []
    out: Dict[str, List[str]] = {}
    if isinstance(units, list):
        for u in units:
            if not isinstance(u, dict):
                continue
            short_id = str(u.get("apiName", "")).strip()
            if not short_id:
                continue
            traits = u.get("traits") or []
            if isinstance(traits, list):
                out[short_id] = [str(t).strip() for t in traits if str(t).strip()]
    _UNIT_TRAITS_CACHE = out
    return _UNIT_TRAITS_CACHE


def _percentile_rank(values: List[float], value: float) -> float:
    """Return percentile rank in [0,1]. Higher value => higher percentile."""
    if not values:
        return 0.5
    n = len(values)
    lower = sum(1 for v in values if v < value)
    equal = sum(1 for v in values if v == value)
    # Midrank percentile
    return max(0.0, min(1.0, (lower + 0.5 * equal) / n))


def _timing_pressure_from_levelling(levelling: str) -> float:
    """Heuristic pressure (0-1) by game plan timing. Lower is better availability."""
    lev = (levelling or "").strip()
    if lev == "Fast 9":
        return 0.35
    if lev == "Fast 8":
        return 0.45
    if lev.startswith("lvl"):
        return 0.65  # reroll-style spikes are often highly contested early
    return 0.55  # Standard / unknown


def _norm_unlock_key(value: str) -> str:
    """Normalize user-facing names for robust comparisons (case/punctuation insensitive)."""
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def _parse_unlock_trait_label(label: str) -> tuple[str, int | None]:
    """Split a label like 'N.O.V.A. 5' into ('nova', 5)."""
    raw = str(label or "").strip()
    m = re.match(r"^(.*?)(?:\s+(\d+))?$", raw)
    if not m:
        return _norm_unlock_key(raw), None
    base = _norm_unlock_key(m.group(1) or raw)
    lvl = int(m.group(2)) if m.group(2) else None
    return base, lvl


def _server_to_region(server: str | None) -> str | None:
    """Convert config server value (aliases or codes, comma-separated) to API region param."""
    if not server or not server.strip():
        return None
    parts = [p.strip() for p in server.split(",") if p.strip()]
    if not parts:
        return None
    mapped = [SERVER_ALIASES.get(p.upper(), p) for p in parts]
    return ",".join(mapped)


def _extract_emblem_signals_from_cluster(info: Dict[str, Any]) -> List[Dict[str, float | str]]:
    """
    Mirror MetaTFT frontend emblem tooltip inputs from comps_data:
    - top_itemNames[*].pcnt
    - top_itemNames[*].avg
    - overall.avg
    """
    overall = info.get("overall") or {}
    try:
        overall_avg = float(overall.get("avg", 0.0))
    except Exception:
        overall_avg = 0.0
    out: List[Dict[str, float | str]] = []
    top_items = info.get("top_itemNames") or []
    if not isinstance(top_items, list):
        return out
    for entry in top_items:
        if not isinstance(entry, dict):
            continue
        item_id = str(entry.get("itemNames") or "").strip()
        # Frontend checks icon.includes("Spatula"); API ids with EmblemItem map to those.
        if not item_id or "EmblemItem" not in item_id:
            continue
        try:
            pcnt = float(entry.get("pcnt", 0.0))
            item_avg = float(entry.get("avg", 0.0))
        except Exception:
            continue
        emblem_name = _clean_tft_token(item_id).replace("EmblemItem", "").strip()
        if emblem_name.startswith("Item_"):
            emblem_name = emblem_name[len("Item_") :]
        emblem_name = emblem_name.replace("_", " ").strip()
        emblem_name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", emblem_name).strip()
        if emblem_name.endswith(" Emblem"):
            emblem_name = emblem_name[: -len(" Emblem")].strip()
        placement_gain = overall_avg - item_avg
        # Keep only positive gains, matching "improves the placement by X".
        if placement_gain <= 0:
            continue
        out.append(
            {
                "item_id": item_id,
                "emblem_name": emblem_name,
                "pcnt": pcnt,
                "item_avg": item_avg,
                "placement_gain": placement_gain,
                "required": pcnt > 0.8,
            }
        )
    return out


def _get_units_pick_rate_lan(
    queue: int,
    patch: str,
    days: int,
    rank: str,
) -> tuple[Dict[str, float], bool]:
    """Fetch per-unit pick rate (usage %) in LAN from units_distribution (web-aligned)."""
    lan_region = _server_to_region("LAN")
    if not lan_region:
        return {}, False
    params = {
        "queue": queue,
        "patch": patch,
        "days": days,
        "rank": rank,
        # Match MetaTFT web requests: server=LA1 (etc), not region.
        "server": lan_region,
        "permit_filter_adjustment": "true",
    }
    try:
        resp = requests.get(UNITS_DISTRIBUTION_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException:
        # LAN unit pick rates improve availability precision, but they are optional.
        # If this endpoint times out, continue with comp-level availability only.
        return {}, False
    games_list = data.get("games") or []
    total_games = float(games_list[0].get("count", 0)) if games_list else 0.0
    if total_games <= 0:
        return {}, False
    out: Dict[str, float] = {}
    unit_appearances: Dict[str, float] = Counter()
    for entry in data.get("results", []):
        unit_id = str(entry.get("unit") or "").strip()
        if not unit_id:
            continue
        places = entry.get("places") or []
        appearances = float(sum(places[:8]) if len(places) >= 8 else sum(places))
        if appearances <= 0:
            continue
        # units_distribution is split by numItems, so aggregate all bins per unit.
        unit_appearances[unit_id] += appearances
    for unit_id, appearances in unit_appearances.items():
        out[unit_id] = (appearances / total_games) * 100.0
    return out, True


def get_current_live_patch(*, days: int = 7) -> str | None:
    """Return live patch label (e.g. 17.2b) from MetaTFT games endpoint."""
    try:
        resp = requests.get(GAMES_URL, params={"days": days}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current_patch") or {}
        patch = str(current.get("patch") or "").strip()
        b = str(current.get("b_patch_version") or "").strip()
        if not patch:
            return None
        return f"{patch}{b}" if b else patch
    except requests.exceptions.RequestException:
        return None


def load_config() -> Dict[str, Any]:
    """Load tftool/config.yaml. Missing file or key => use defaults. Returns flat dict of filter keys."""
    defaults = {
        "queue": 1100,
        "patch": "current",
        "days": 3,
        "server": None,
        "rank": DEFAULT_RANK,
        "limit": 15,
        "max_avg_place": None,
        "exclude_emblem_comps": True,
        "exclude_repeated_units_comps": False,
        "difficulty": None,
        "objective": "climb",
        "season_unlockables_filter_enabled": False,
        "season_unlockables": {"units": [], "traits": []},
        "columns": {
            "avg": True,
            "win_rate": True,
            "top4_rate": True,
            "pick_rate": True,
            "performance": True,
            "availability": True,
            "score": True,
            "games": True,
        },
    }
    if not CONFIG_PATH.exists():
        return defaults
    try:
        raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return defaults
    for k in defaults:
        if k in raw and raw[k] is not None:
            v = raw[k]
            if k == "rank" and isinstance(v, list):
                v = ",".join(str(x).strip() for x in v if x)
            elif k == "server" and isinstance(v, list):
                v = ",".join(str(x).strip() for x in v if x) or None
            elif k == "exclude_emblem_comps":
                v = bool(v) if isinstance(v, bool) else str(v).strip().lower() in ("1", "true", "yes")
            elif k == "exclude_repeated_units_comps":
                v = bool(v) if isinstance(v, bool) else str(v).strip().lower() in ("1", "true", "yes")
            elif k == "difficulty":
                if v is None:
                    pass
                elif isinstance(v, list):
                    v = [str(x).strip() for x in v if x and str(x).strip()]
                else:
                    v = [str(v).strip()] if str(v).strip() else None
            elif k == "limit":
                v = max(1, int(v)) if v is not None else defaults["limit"]
            elif k == "max_avg_place":
                v = float(v) if v is not None else None
            elif k == "objective":
                v = str(v).strip().lower() if v is not None else "climb"
                if v not in ("climb", "first", "safe"):
                    v = "climb"
            elif k == "season_unlockables_filter_enabled":
                v = bool(v) if isinstance(v, bool) else str(v).strip().lower() in ("1", "true", "yes")
            elif k == "season_unlockables":
                parsed = {"units": [], "traits": []}
                if isinstance(v, dict):
                    units = v.get("units", [])
                    traits = v.get("traits", [])
                    if isinstance(units, list):
                        parsed["units"] = [str(x).strip() for x in units if str(x).strip()]
                    if isinstance(traits, list):
                        parsed["traits"] = [str(x).strip() for x in traits if str(x).strip()]
                v = parsed
            elif k == "columns":
                parsed = dict(defaults["columns"])
                if isinstance(v, dict):
                    for ck in parsed:
                        if ck in v:
                            cv = v[ck]
                            parsed[ck] = (
                                bool(cv) if isinstance(cv, bool)
                                else str(cv).strip().lower() in ("1", "true", "yes", "on")
                            )
                v = parsed
            defaults[k] = v
    return defaults


@dataclass
class CompositionStats:
    name: str
    avg_place: float
    count: int
    cluster_id: str
    win_rate: float = 0.0
    top4_rate: float = 0.0
    units_string: str = ""
    difficulty: float = 0.0
    pick_rate_lan: float = 0.0
    score: float = 0.0  # Composite score combining avg_place, win_rate, top4_rate
    performance_score: float = 0.0  # 0-100: how well the comp performs
    availability_score: float = 0.0  # 0-100: how uncontested it is in LAN
    stars_3_ids: List[str] = None  # Unit IDs typically 3-starred in this comp (9 copies)
    units_display_order: List[str] = None  # Unit IDs in display order (name order first, then rest)
    levelling: str = ""  # e.g. "Fast 9", "Fast 8", "Standard", "lvl 6"
    covered_unlockables: List[str] = None  # Seasonal unlockables this comp helps complete
    emblem_required: bool = False  # True when MetaTFT signal marks emblem as required (pcnt > 0.8)
    emblem_recommended: bool = False  # True when emblem signal exists with positive gain but not required
    emblem_name: str = ""  # Display name of the main emblem signal (e.g. "Dark Star")
    expected_games_to_first: float = 0.0  # For objective=first: expected attempts to hit 1st once
    expected_games_to_top4: float = 0.0  # For objective=safe: expected attempts to hit top4 once

    def __post_init__(self) -> None:
        if self.stars_3_ids is None:
            self.stars_3_ids = []
        if self.units_display_order is None:
            self.units_display_order = []
        if self.covered_unlockables is None:
            self.covered_unlockables = []


def difficulty_label(levelling: str, difficulty: float) -> str:
    """Infer Easy/Medium/Hard from levelling tag + numeric difficulty (matches MetaTFT-style tags)."""
    lev = (levelling or "").strip()
    if lev == "Fast 9":
        return "Hard"
    if lev == "Standard":
        if difficulty <= -0.05:
            return "Easy"
        if difficulty <= -0.02:
            return "Hard"
        return "Medium"
    if lev == "Fast 8":
        if difficulty > 0.08:
            return "Hard"
        if difficulty < -0.05:
            return "Easy"
        if -0.005 <= difficulty <= 0.005:
            return "Easy"
        return "Medium"
    if lev.startswith("lvl"):
        return "Easy" if difficulty <= -0.05 else "Medium"
    return "Medium"


def fetch_compositions_by_avg_place(
    *,
    queue: int = 1100,
    patch: str | None = "current",
    days: int | None = 3,
    server: str | None = None,
    rank: str | None = DEFAULT_RANK,
    max_avg_place: float | None = None,
    limit: int = 15,
    situational: bool = False,
    exclude_emblem_comps: bool = True,
    exclude_repeated_units_comps: bool = False,
    difficulty_filter: List[str] | None = None,
    objective: str = "climb",
    season_unlockables_filter_enabled: bool = False,
    season_unlockables: Dict[str, List[str]] | None = None,
) -> tuple[List[CompositionStats], Dict[str, Any] | None, Dict[str, str]]:
    """
    Fetch composition clusters from MetaTFT and sort by composite score (performance + availability).
    Returns (comps, applied_filters, resource_status).
    applied_filters is what the API reports (filter_adjustment, tft_set, etc.);
    resource_status shows endpoint health for visibility (ok/fail/skipped).

    Filters:
      queue: 1100 = Ranked (default).
      patch: e.g. "current"; None = use comps_data only (no time filter).
      days: e.g. 3; only used with comps_stats when patch/rank are set.
      server: e.g. NA1, EUW1; None = all servers. Sent as region to API.
      rank: e.g. CHALLENGER,DIAMOND,...; None = use comps_data only.
      max_avg_place: drop comps with avg place above this (client-side).
      limit: max number of comps to return (default 15).
    """
    resource_status: Dict[str, str] = {
        "comps_data": "fail",
        "comps_stats_primary": "skipped",
        "comps_stats_lan": "skipped",
        "units_lan": "skipped",
    }
    cluster_details, comps_data_ok = _get_comps_data_cluster_details(queue)
    resource_status["comps_data"] = "ok" if comps_data_ok else "fail"

    applied_filters: Dict[str, Any] | None = None
    stats_by_cluster = None
    stats_lan_by_cluster = None
    total_games_lan = 0.0
    units_pick_lan: Dict[str, float] = {}

    if patch is not None and rank is not None:
        region = _server_to_region(server)
        stats_by_cluster, applied_filters, stats_primary_ok = _get_comps_stats_by_cluster(
            queue=queue,
            patch=patch,
            days=days or 3,
            rank=rank,
            region=region,
            situational=situational,
        )
        resource_status["comps_stats_primary"] = "ok" if stats_primary_ok else "fail"
        # Always get LAN stats for pick_rate calculation (even if user filters by LAN)
        lan_region = _server_to_region("LAN")
        if lan_region:
            stats_lan_by_cluster, lan_filters, stats_lan_ok = _get_comps_stats_by_cluster(
                queue=queue,
                patch=patch,
                days=days or 3,
                rank=rank,
                region=lan_region,
                situational=situational,
            )
            resource_status["comps_stats_lan"] = "ok" if stats_lan_ok else "fail"
            total_games_lan = float(lan_filters.get("filter_adjustment", {}).get("sample_size", 0))
        # Per-unit pick rates in LAN for champion-level contestation
        if lan_region:
            units_pick_lan, units_lan_ok = _get_units_pick_rate_lan(
                queue=queue,
                patch=patch,
                days=days or 3,
                rank=rank,
            )
            resource_status["units_lan"] = "ok" if units_lan_ok else "fail"
        else:
            resource_status["comps_stats_lan"] = "skipped"
            resource_status["units_lan"] = "skipped"

    trait_display_name_map = _get_trait_display_name_map()
    unit_cost_map, unit_name_map = _get_unit_meta_maps()
    unit_traits_map = _get_unit_traits_map()
    all_lan_comp_pick_rates: List[float] = []
    all_lan_comp_counts: List[float] = []
    if stats_lan_by_cluster is not None and total_games_lan > 0:
        for _, (_, lan_count, _, _) in stats_lan_by_cluster.items():
            all_lan_comp_pick_rates.append((lan_count / total_games_lan) * 100.0)
            all_lan_comp_counts.append(float(lan_count))
    all_unit_pick_rates = list(units_pick_lan.values())
    unlock_units_norm = {
        _norm_unlock_key(x)
        for x in ((season_unlockables or {}).get("units") or [])
        if str(x).strip()
    }
    unlock_traits_norm = {
        _norm_unlock_key(x)
        for x in ((season_unlockables or {}).get("traits") or [])
        if str(x).strip()
    }
    unlock_units_labels = [str(x).strip() for x in ((season_unlockables or {}).get("units") or []) if str(x).strip()]
    unlock_traits_labels = [str(x).strip() for x in ((season_unlockables or {}).get("traits") or []) if str(x).strip()]
    objective_mode = (objective or "climb").strip().lower()
    if objective_mode not in ("climb", "first", "safe"):
        objective_mode = "climb"

    # Objective profiles (practical ladder behavior):
    # - climb: forceable LP consistency (avg/top4 first, availability as contest penalty)
    # - first: maximize 1st-place spikes (win rate dominates, availability secondary)
    # - safe: maximize consistency/top4 frequency (availability and top4 dominate)
    if objective_mode == "first":
        perf_w_avg, perf_w_win, perf_w_top4 = 0.15, 0.70, 0.15
        score_w_perf, score_w_avail = 0.75, 0.25
    elif objective_mode == "safe":
        perf_w_avg, perf_w_win, perf_w_top4 = 0.30, 0.10, 0.60
        score_w_perf, score_w_avail = 0.50, 0.50
    else:  # climb
        perf_w_avg, perf_w_win, perf_w_top4 = 0.50, 0.15, 0.35
        score_w_perf, score_w_avail = 0.75, 0.25

    comps: List[CompositionStats] = []
    for cid, info in cluster_details.items():
        name_str = str(info.get("name_string", "") or "")

        # Exclude situational comps (identified by "Augment" in name_string)
        if not situational:
            if "Augment" in name_str:
                continue
                
        if stats_by_cluster is not None and cid in stats_by_cluster:
            avg, count, win_r, top4_r = stats_by_cluster[cid]
        else:
            overall = info.get("overall") or {}
            avg = float(overall.get("avg", 0.0))
            count = int(overall.get("count", 0))
            win_r, top4_r = 0.0, 0.0

        if max_avg_place is not None and avg > max_avg_place:
            continue

        # Get difficulty and units_string from comps_data
        difficulty = float(info.get("difficulty", 0.0))
        levelling = (info.get("levelling") or "").strip()

        units_str = info.get("units_string", "")
        unit_ids_raw = [u.strip() for u in units_str.split(",") if u.strip()]
        unit_occurrences = Counter(unit_ids_raw)
        repeated_units_count = sum(1 for _, occ in unit_occurrences.items() if occ > 1)
        # Temporary safeguard while augment/tag data is bugged upstream.
        # Exclude comps that rely on duplicate-unit patterns (>= 2 repeated champions).
        if exclude_repeated_units_comps and repeated_units_count >= 2:
            continue
        # Units expected at 3-star (9 copies) vs 2-star (3 copies) for availability weighting
        stars_raw = info.get("stars") or []
        stars_3_set = {str(u).strip() for u in stars_raw if u}
        stars_4_raw = info.get("stars_4") or []
        stars_4_set = {str(u).strip() for u in stars_4_raw if u}
        # For availability weighting, simplify 4-star edge cases as 3-star pressure (9 copies).
        starred_set = stars_3_set | stars_4_set
        # Emblem filter uses the same statistical signal shown in MetaTFT tooltip:
        # top_itemNames[*].pcnt + (overall.avg - item.avg).
        emblem_signals = _extract_emblem_signals_from_cluster(info)
        if exclude_emblem_comps and emblem_signals:
            continue
        emblem_required = any(bool(s.get("required")) for s in emblem_signals)
        emblem_recommended = bool(emblem_signals) and not emblem_required
        emblem_name = ""
        if emblem_signals:
            top_signal = max(emblem_signals, key=lambda s: float(s.get("pcnt", 0.0)))
            emblem_name = str(top_signal.get("emblem_name") or "").strip()
        # Build readable name and champion display order from 'name' (same order as guide)
        # e.g. "Zaun Warwick", "Zaun Warwick Swain"; champions shown in that order
        name_list = info.get("name", [])
        all_unit_ids = unit_ids_raw
        name_units_order: List[str] = []  # unit IDs in order as in name
        if name_list and isinstance(name_list, list):
            trait_ids = [str(n.get("name", "")).strip() for n in name_list if n.get("type") == "trait" and n.get("name")]
            traits = [trait_display_name_map.get(tid, _clean_tft_token(tid)) for tid in trait_ids]
            name_unit_ids = [str(n.get("name", "")).strip() for n in name_list if n.get("type") == "unit" and n.get("name")]
            if name_unit_ids:
                name_units_order = name_unit_ids
            if traits and name_units_order:
                units_display_names = [unit_name_map.get(u, _clean_tft_token(u)) for u in name_units_order]
                name = f"{traits[0]} {' '.join(units_display_names)}"
            elif traits:
                name = traits[0]
            elif name_units_order:
                name = " ".join(unit_name_map.get(u, _clean_tft_token(u)) for u in name_units_order)
            else:
                name = info.get("name_string", "") or units_str or str(cid)
        else:
            name = info.get("name_string", "") or units_str or str(cid)
        # Display order: name order first, then any remaining from units_string
        if name_units_order:
            # Preserve duplicate units from units_string (e.g. Samira x2, Ornn x2)
            # while still honoring name order first.
            remaining = Counter(all_unit_ids)
            for uid in name_units_order:
                if remaining[uid] > 0:
                    remaining[uid] -= 1
            rest: List[str] = []
            for uid in all_unit_ids:
                if remaining[uid] > 0:
                    rest.append(uid)
                    remaining[uid] -= 1
            units_display_order = name_units_order + rest
        else:
            units_display_order = all_unit_ids
        # Keep only playable units from Riot dataset (dynamic, no hardcoded IDs).
        # Example: Summon is excluded, while TFT17_IvernMinion maps to Meepsie and stays.
        if unit_name_map:
            units_display_order = [uid for uid in units_display_order if uid in unit_name_map]

        covered_unlockables: List[str] = []
        if unlock_units_norm or unlock_traits_norm:
            comp_units_norm = {
                _norm_unlock_key(unit_name_map.get(uid, _clean_tft_token(uid)))
                for uid in units_display_order
            }
            traits_string = str(info.get("traits_string", "") or "")
            comp_traits_norm = set()
            comp_trait_counts: Dict[str, int] = Counter()
            # Primary source for unlockable traits: champions actually shown in the output table.
            # This is more reliable for missions than traits_string when the API under-reports tiers.
            for uid in units_display_order:
                for trait_name in unit_traits_map.get(uid, []):
                    comp_trait_counts[_norm_unlock_key(trait_name)] += 1
            if traits_string:
                for raw_trait in [t.strip() for t in traits_string.split(",") if t.strip()]:
                    # Example: TFT17_SpaceGroove_7 -> ("TFT17_SpaceGroove", "7")
                    trait_id, lvl = (raw_trait.rsplit("_", 1) + [""])[:2] if "_" in raw_trait else (raw_trait, "")
                    trait_name = trait_display_name_map.get(trait_id, _clean_tft_token(trait_id))
                    trait_with_level = f"{trait_name} {lvl}".strip() if lvl else trait_name
                    comp_traits_norm.add(_norm_unlock_key(trait_with_level))
                    comp_traits_norm.add(_norm_unlock_key(trait_name))
                    base_norm = _norm_unlock_key(trait_name)
                    try:
                        lvl_int = int(lvl)
                    except Exception:
                        lvl_int = None
                    if base_norm and lvl_int is not None:
                        comp_trait_counts[base_norm] = max(comp_trait_counts.get(base_norm, 0), lvl_int)

            has_unit_match = bool(comp_units_norm & unlock_units_norm) if unlock_units_norm else False
            has_trait_match = False
            for label in unlock_units_labels:
                if _norm_unlock_key(label) in comp_units_norm:
                    covered_unlockables.append(label)
            for label in unlock_traits_labels:
                trait_norm, needed_count = _parse_unlock_trait_label(label)
                actual_count = comp_trait_counts.get(trait_norm, 0)
                if (
                    (needed_count is not None and actual_count >= needed_count)
                    or _norm_unlock_key(label) in comp_traits_norm
                ):
                    covered_unlockables.append(label)
                    has_trait_match = True

            if season_unlockables_filter_enabled and not has_unit_match and not has_trait_match:
                continue

        # Comp pick_rate in LAN
        pick_rate_lan = 0.0
        lan_count = 0
        if stats_lan_by_cluster is not None and cid in stats_lan_by_cluster:
            lan_count = stats_lan_by_cluster[cid][1]  # count from tuple
            if total_games_lan > 0:
                pick_rate_lan = (lan_count / total_games_lan) * 100.0

        # Performance score (0-100): weighted combination of avg_place, win_rate, top4_rate
        # Based on TFT LP system: top 4 gains LP, bottom 4 loses LP
        # avg_place: 1.0 = perfect (100), 4.5 = neutral/top4 threshold (50), 8.0 = worst (0)
        avg_place_score = max(0.0, min(100.0, ((8.0 - avg) / 7.0) * 100.0))
        # win_rate and top4_rate already in 0-100 range
        win_rate_score = max(0.0, min(100.0, win_r))
        top4_rate_score = max(0.0, min(100.0, top4_r))
        # Objective-based performance weights (climb/first/safe).
        performance_score = (
            perf_w_avg * avg_place_score +
            perf_w_win * win_rate_score +
            perf_w_top4 * top4_rate_score
        )

        # Availability score (0-100): comp + champion contestation in LAN
        # Combines: (1) comp pick rate, (2) avg pick rate of this comp's champions in LAN
        # Dynamic pressure model:
        # - comp pressure percentile in current LAN meta
        # - weighted champion pressure percentile (cost + 3-star needs)
        # - timing pressure (levelling heuristic)
        # - confidence penalty for low LAN sample size
        comp_pressure = _percentile_rank(all_lan_comp_pick_rates, pick_rate_lan)
        weighted_unit_pressure = 0.5
        if units_str:
            unit_ids = list(unit_occurrences.keys())
            total_weight = 0.0
            weighted_sum = 0.0
            for uid in unit_ids:
                if unit_name_map and uid not in unit_name_map:
                    # Skip non-playable/synthetic tokens not present in Riot champion dataset.
                    continue
                if uid in units_pick_lan:
                    unit_pick = units_pick_lan[uid]
                    unit_pressure = _percentile_rank(all_unit_pick_rates, unit_pick)
                else:
                    # Neutral pressure for unmapped/special IDs (e.g. summons), avoid false "free" signal.
                    unit_pressure = 0.5
                # Repeated non-starred units require extra copies (2x unit -> 6 copies, etc).
                # Repeated starred units are simplified to a single 3-star requirement (9 copies total).
                copies = 9 if uid in starred_set else (3 * unit_occurrences.get(uid, 1))
                cost = unit_cost_map.get(uid, 3)
                cost_weight = 1.0 + (max(1, min(5, cost)) - 1) * 0.25
                w = copies * cost_weight
                weighted_sum += unit_pressure * w
                total_weight += w
            if total_weight > 0:
                weighted_unit_pressure = weighted_sum / total_weight

        timing_pressure = _timing_pressure_from_levelling(levelling)
        if all_lan_comp_counts:
            # Relative confidence in current sample context (days/rank/patch), not fixed absolute threshold.
            confidence_penalty = 1.0 - _percentile_rank(all_lan_comp_counts, float(lan_count))
        else:
            confidence_penalty = 0.5

        pressure_score = (
            0.35 * comp_pressure
            + 0.45 * weighted_unit_pressure
            + 0.15 * timing_pressure
            + 0.05 * confidence_penalty
        )
        pressure_score = max(0.0, min(1.0, pressure_score))
        availability_score = (1.0 - pressure_score) * 100.0

        # Composite score:
        # - first: optimize expected number of games needed to get a single 1st place
        #          p(first in one attempt) ~= p_win * p_playable(availability)
        #          expected_games_to_first = 1 / p(first)
        # - safe: optimize expected number of games needed to secure top4
        #         p(top4 in one attempt) ~= p_top4 * p_playable(availability)
        #         expected_games_to_top4 = 1 / p(top4)
        # - climb: weighted blend of performance + availability
        expected_games_to_first = 0.0
        expected_games_to_top4 = 0.0
        if objective_mode == "first":
            p_win = max(0.0, min(1.0, win_r / 100.0))
            # Availability is treated as "can execute this comp cleanly in a given lobby".
            # Keep a non-zero floor so very contested comps are penalized but not invalid.
            p_playable = 0.35 + 0.65 * max(0.0, min(100.0, availability_score)) / 100.0
            p_first_effective = max(1e-6, p_win * p_playable)
            expected_games_to_first = 1.0 / p_first_effective
            # Higher score is better; equivalent to maximizing effective first probability.
            score = p_first_effective * 100.0
        elif objective_mode == "safe":
            p_top4 = max(0.0, min(1.0, top4_r / 100.0))
            # In safe mode, contestation hurts consistency directly, so availability stays explicit.
            p_playable = 0.35 + 0.65 * max(0.0, min(100.0, availability_score)) / 100.0
            p_top4_effective = max(1e-6, p_top4 * p_playable)
            expected_games_to_top4 = 1.0 / p_top4_effective
            # Higher score is better; equivalent to maximizing effective top4 probability.
            score = p_top4_effective * 100.0
        else:
            score = score_w_perf * performance_score + score_w_avail * availability_score

        # Filter by difficulty label (Easy/Medium/Hard) if configured
        if difficulty_filter:
            label = difficulty_label(levelling, difficulty)
            if label not in difficulty_filter:
                continue

        comps.append(
            CompositionStats(
                name=name,
                avg_place=avg,
                count=count,
                cluster_id=str(cid),
                win_rate=win_r,
                top4_rate=top4_r,
                units_string=units_str,
                difficulty=difficulty,
                pick_rate_lan=pick_rate_lan,
                score=score,
                performance_score=performance_score,
                availability_score=availability_score,
                stars_3_ids=list(starred_set),
                units_display_order=units_display_order,
                levelling=levelling,
                covered_unlockables=covered_unlockables,
                emblem_required=emblem_required,
                emblem_recommended=emblem_recommended,
                emblem_name=emblem_name,
                expected_games_to_first=expected_games_to_first,
                expected_games_to_top4=expected_games_to_top4,
            )
        )

    if max_avg_place is None:
        # No avg cap configured:
        # 1) keep only the best performers by avg_place
        # 2) among those, prioritize availability (more playable right now)
        top_by_avg = sorted(comps, key=lambda c: (c.avg_place, -c.score))[:limit]
        top_by_avg.sort(key=lambda c: (-c.availability_score, c.avg_place, -c.score))
        return top_by_avg, applied_filters, resource_status

    # Avg cap configured: keep the original score-first behavior.
    comps.sort(key=lambda c: -c.score)
    return comps[:limit], applied_filters, resource_status


def _get_comps_data_cluster_details(queue: int) -> tuple[dict, bool]:
    try:
        resp = requests.get(COMPS_DATA_URL, params={"queue": queue}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return (data.get("results", {}).get("data", {}).get("cluster_details", {})) or {}, True
    except requests.exceptions.RequestException:
        return {}, False


def _get_comps_stats_by_cluster(
    queue: int,
    patch: str,
    days: int,
    rank: str,
    region: str | None = None,
    situational: bool = False,
) -> tuple[dict[str, tuple[float, int, float, float]], dict[str, Any], bool]:
    """Return (cluster_id -> (avg_place, count, win_rate, top4_rate), applied_filters).
    applied_filters is what the API reports: filter_adjustment, tft_set, queue_id, updated."""
    params = {
        "queue": queue,
        "patch": patch,
        "days": days,
        "rank": rank,
        "permit_filter_adjustment": "true",
    }
    if region:
        # Match MetaTFT web requests: server=LA1 (etc), not region.
        params["server"] = region
    if situational:
        params["situational"] = "true"
    try:
        resp = requests.get(COMPS_STATS_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException:
        return {}, {
            "filter_adjustment": None,
            "tft_set": None,
            "queue_id": queue,
            "updated": None,
        }, False

    applied: dict[str, Any] = {
        "filter_adjustment": data.get("filter_adjustment"),
        "tft_set": data.get("tft_set"),
        "queue_id": data.get("queue_id"),
        "updated": data.get("updated"),
    }

    out: dict[str, tuple[float, int, float, float]] = {}
    for entry in data.get("results", []):
        cid = entry.get("cluster")
        if cid is None or cid == "" or str(cid) == "-1":
            continue
        places = entry.get("places") or []
        place_counts = places[:8]
        if len(place_counts) < 8:
            continue
        count = int(entry.get("count", 0)) or sum(place_counts)
        if count <= 0:
            continue
        weighted = sum((i + 1) * place_counts[i] for i in range(8))
        avg = weighted / count
        wins = place_counts[0]
        top4 = sum(place_counts[:4])
        win_rate = (wins / count) * 100.0
        top4_rate = (top4 / count) * 100.0
        out[str(cid)] = (avg, count, win_rate, top4_rate)
    return out, applied, True
