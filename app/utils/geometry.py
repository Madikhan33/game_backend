from collections.abc import Sequence
from math import isclose
from typing import TypedDict


class PolygonPoint(TypedDict):
    x: float
    y: float


def _point_on_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> bool:
    cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
    if not isclose(cross, 0.0, abs_tol=1e-9):
        return False
    return min(ax, bx) - 1e-9 <= px <= max(ax, bx) + 1e-9 and min(ay, by) - 1e-9 <= py <= max(ay, by) + 1e-9


def point_in_polygon(x: float, y: float, polygon: Sequence[PolygonPoint]) -> bool:
    if len(polygon) < 3:
        return False

    inside = False
    previous = polygon[-1]

    for current in polygon:
        ax = float(previous["x"])
        ay = float(previous["y"])
        bx = float(current["x"])
        by = float(current["y"])

        if _point_on_segment(x, y, ax, ay, bx, by):
            return True

        if (ay > y) != (by > y):
            x_at_y = (bx - ax) * (y - ay) / (by - ay) + ax
            if x_at_y >= x:
                inside = not inside

        previous = current

    return inside
