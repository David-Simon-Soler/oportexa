from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

WindowKind = Literal["daily", "weekly", "monthly"]


@dataclass(frozen=True, slots=True)
class DateWindow:
    date_from: date
    date_to: date


def generate_windows(date_from: date, date_to: date, window: WindowKind) -> list[DateWindow]:
    """Generate contiguous, inclusive, non-overlapping windows.

    Weekly windows are seven-day chunks anchored at date_from. Monthly windows
    use calendar boundaries, with partial first and last months preserved.
    """
    if date_from > date_to:
        raise ValueError("date_from must not be after date_to")
    if window not in {"daily", "weekly", "monthly"}:
        raise ValueError("window must be daily, weekly or monthly")
    result: list[DateWindow] = []
    cursor = date_from
    while cursor <= date_to:
        if window == "daily":
            candidate = cursor
        elif window == "weekly":
            candidate = cursor + timedelta(days=6)
        else:
            candidate = date(cursor.year, cursor.month, monthrange(cursor.year, cursor.month)[1])
        end = min(candidate, date_to)
        result.append(DateWindow(cursor, end))
        cursor = end + timedelta(days=1)
    return result
