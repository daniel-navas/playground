from typing import List
from collections import defaultdict

from .comps import (
    CompositionStats,
    load_config,
    fetch_compositions_by_avg_place,
    difficulty_label,
    get_unit_display_name,
    get_current_live_patch,
)


def _resource_badge(resource_status: dict[str, str]) -> str:
    keys = ("comps_data", "comps_stats_primary", "comps_stats_lan", "units_lan")
    total = len(keys)
    ok = sum(1 for k in keys if resource_status.get(k) == "ok")
    mark = "✓" if ok == total else "✗"
    raw = f"{mark} {ok}/{total}"
    # ANSI terminal colors: green when complete, red otherwise.
    return f"\033[92m{raw}\033[0m" if ok == total else f"\033[91m{raw}\033[0m"


def _format_comps(
    comps: List[CompositionStats],
    *,
    show_unlockables: bool = False,
    columns: dict[str, bool] | None = None,
    resource_status: dict[str, str] | None = None,
    version_label: str | None = None,
) -> str:
    lines = []
    # Column widths must match data row exactly for alignment
    w_num, w_name, w_avg, w_pct, w_top4, w_score, w_games = 2, 52, 5, 5, 6, 6, 6
    cfg = columns or {}
    specs = [
        ("avg", "Avg", w_avg, lambda c: f"{c.avg_place:>{w_avg}.2f}"),
        ("win_rate", "Win%", w_pct, lambda c: f"{c.win_rate:>{w_pct}.1f}"),
        ("top4_rate", "Top4%", w_top4, lambda c: f"{c.top4_rate:>{w_top4}.1f}"),
        # Web pick-rate style: average players per lobby running this comp (out of 8).
        ("pick_rate", "Pick", w_pct, lambda c: f"{(c.pick_rate_lan * 8.0 / 100.0):>{w_pct}.2f}"),
        ("performance", "Perf", w_pct, lambda c: f"{c.performance_score:>{w_pct}.1f}"),
        ("availability", "Avail", w_pct, lambda c: f"{c.availability_score:>{w_pct}.1f}"),
        ("score", "Score", w_score, lambda c: f"{c.score:>{w_score}.1f}"),
        ("games", "Games", w_games, lambda c: f"{c.count:>{w_games}}"),
    ]
    active_specs = [s for s in specs if cfg.get(s[0], True)]
    comp_title = "Composition"
    if version_label:
        comp_title += f" | {version_label}"
    if resource_status is not None:
        comp_title += f" | Data Health: [{_resource_badge(resource_status)}]"
    header = f"  {'#':<{w_num}}  {comp_title:<{w_name}}"
    for _, title, width, _ in active_specs:
        header += f"  {title:>{width}}"
    sep_len = len(header)
    lines.append(header)
    lines.append("-" * sep_len)
    for i, c in enumerate(comps, 1):
        label = difficulty_label(c.levelling, c.difficulty)
        suffix = f"  [{label}]"
        if c.emblem_name:
            suffix += f" [{c.emblem_name}]"
        name_max = w_name - len(suffix)
        name_part = c.name if len(c.name) <= name_max else c.name[: name_max - 3] + "..."
        name = name_part + suffix
        row = f"  {i:<{w_num}}  {name:<{w_name}}"
        for _, _, _, formatter in active_specs:
            row += f"  {formatter(c)}"
        lines.append(row)
        order = c.units_display_order or [u.strip() for u in (c.units_string or "").split(",") if u.strip()]
        if order:
            stars_3 = set(c.stars_3_ids or [])
            starred_used = defaultdict(int)
            parts = []
            for uid in order:
                display_name = get_unit_display_name(uid)
                if uid in stars_3 and starred_used[uid] == 0:
                    parts.append(f"{display_name}★")
                    starred_used[uid] += 1
                else:
                    parts.append(display_name)
            champions_line = f"      {'  '.join(parts)}"
            if show_unlockables and c.covered_unlockables:
                champions_line += f"  | Unlockables: {', '.join(c.covered_unlockables)}"
            lines.append(champions_line)
        elif show_unlockables and c.covered_unlockables:
            lines.append(f"      Unlockables: {', '.join(c.covered_unlockables)}")
        if i < len(comps):
            lines.append("")
    return "\n".join(lines)


def run_tftool() -> None:
    cfg = load_config()
    patch = cfg.get("patch", "current")
    comps, applied_filters, resource_status = fetch_compositions_by_avg_place(
        queue=cfg["queue"],
        patch=patch,
        days=cfg["days"],
        server=cfg.get("server"),
        rank=cfg["rank"],
        limit=cfg.get("limit", 15),
        max_avg_place=cfg.get("max_avg_place"),
        exclude_emblem_comps=cfg.get("exclude_emblem_comps", True),
        exclude_repeated_units_comps=cfg.get("exclude_repeated_units_comps", False),
        difficulty_filter=cfg.get("difficulty"),
        objective=cfg.get("objective", "climb"),
        season_unlockables_filter_enabled=cfg.get("season_unlockables_filter_enabled", False),
        season_unlockables=cfg.get("season_unlockables"),
    )
    version_label = f"Patch: {patch}"
    if str(patch).strip().lower() == "current":
        live_patch = get_current_live_patch(days=cfg.get("days", 7))
        if live_patch:
            version_label = f"Patch: {live_patch}"
        else:
            version_label = "Patch: current"
    output = _format_comps(
        comps,
        show_unlockables=cfg.get("season_unlockables_filter_enabled", False),
        columns=cfg.get("columns"),
        resource_status=resource_status,
        version_label=version_label,
    )
    print(output)

