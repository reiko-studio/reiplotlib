"""Figure layout helpers for publication-sized plots."""

from __future__ import annotations

from typing import Any, Literal, TypeAlias

import matplotlib.pyplot as plt

Column: TypeAlias = Literal["single", "double"]
Journal: TypeAlias = Literal["prl"]
Unit: TypeAlias = Literal["pt", "in"]

POINTS_PER_INCH = 72.27
PRL_SINGLE_PT = 243.0
PRL_DOUBLE_PT = 486.0
PRL_SINGLE_IN = PRL_SINGLE_PT / POINTS_PER_INCH
PRL_DOUBLE_IN = PRL_DOUBLE_PT / POINTS_PER_INCH

JOURNAL_WIDTHS_PT: dict[Journal, dict[Column, float]] = {
    "prl": {
        "single": PRL_SINGLE_PT,
        "double": PRL_DOUBLE_PT,
    },
}


def pt_to_in(points: float) -> float:
    """Convert TeX points to inches."""

    return points / POINTS_PER_INCH


def size(
    width: Column | float = "single",
    *,
    aspect: float = 0.62,
    unit: Unit = "pt",
    journal: Journal = "prl",
) -> tuple[float, float]:
    """Return a figure size in inches."""

    if isinstance(width, str):
        width_in = pt_to_in(JOURNAL_WIDTHS_PT[journal][width])
    elif unit == "pt":
        width_in = pt_to_in(width)
    else:
        width_in = width

    return width_in, width_in * aspect


def subplots(
    *args: Any,
    width: Column | float = "single",
    aspect: float = 0.45,
    unit: Unit = "pt",
    journal: Journal = "prl",
    **kwargs: Any,
):
    """Create matplotlib subplots with a publication-sized default figsize."""

    kwargs.setdefault(
        "figsize",
        size(width, aspect=aspect, unit=unit, journal=journal),
    )
    return plt.subplots(*args, **kwargs)


__all__ = [
    "JOURNAL_WIDTHS_PT",
    "POINTS_PER_INCH",
    "PRL_DOUBLE_IN",
    "PRL_DOUBLE_PT",
    "PRL_SINGLE_IN",
    "PRL_SINGLE_PT",
    "pt_to_in",
    "size",
    "subplots",
]
