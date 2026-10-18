"""
Route planning helper using a deterministic nearest-neighbour ordering and
straight-line Haversine distances between configured coordinates.
"""
from __future__ import annotations

import math
from typing import Any

from logistics.config import GEO_COORDINATES


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def optimize_route(stops: list[str], start: str | None = None, end: str | None = None) -> dict[str, Any]:
    """
    Order intermediate stops by nearest-neighbour straight-line distance.
    """
    if not stops:
        return {"status": "empty", "ordered_stops": [], "engine": "none"}

    nodes = [s for s in stops if s in GEO_COORDINATES]
    missing = [s for s in stops if s not in GEO_COORDINATES]
    if not nodes:
        return {"status": "no_coordinates", "ordered_stops": stops, "missing_nodes": missing, "engine": "none"}

    start_node = start if start in GEO_COORDINATES else nodes[0]
    end_node = end if end in GEO_COORDINATES else None

    engine = "greedy_nearest_neighbour"
    ordered = [start_node]
    remaining = [n for n in nodes if n != start_node and n != end_node]

    # Greedy nearest-neighbour on haversine distances
    current = start_node
    while remaining:
        nxt = min(
            remaining,
            key=lambda n: _haversine_km(
                GEO_COORDINATES[current]["lat"],
                GEO_COORDINATES[current]["lon"],
                GEO_COORDINATES[n]["lat"],
                GEO_COORDINATES[n]["lon"],
            ),
        )
        ordered.append(nxt)
        remaining.remove(nxt)
        current = nxt
    if end_node and end_node not in ordered:
        ordered.append(end_node)

    total_km = 0.0
    for a, b in zip(ordered, ordered[1:]):
        total_km += _haversine_km(
            GEO_COORDINATES[a]["lat"], GEO_COORDINATES[a]["lon"],
            GEO_COORDINATES[b]["lat"], GEO_COORDINATES[b]["lon"],
        )

    return {
        "status": "ok",
        "ordered_stops": ordered,
        "approx_distance_km": round(total_km, 1),
        "missing_nodes": missing,
        "engine": engine,
        "disclaimer": "Distances are straight-line Haversine estimates, not road distances. The stop order uses a nearest-neighbour heuristic.",
    }
