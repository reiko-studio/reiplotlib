"""Reusable matplotlib keyword option presets."""

from __future__ import annotations

from typing import Any

from . import colors as c
from .palette import Color

ColorLike = str | Color


def _with_overrides(
    defaults: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    opts = defaults.copy()
    opts.update(overrides)
    return opts


def line(color: ColorLike = c.fubuki.base, **overrides: Any) -> dict[str, Any]:
    """Return common keyword options for line plots."""

    return _with_overrides(
        {
            "color": color,
            "linewidth": 2.0,
            "solid_capstyle": "round",
        },
        overrides,
    )


def markers(color: ColorLike = c.fubuki.base, **overrides: Any) -> dict[str, Any]:
    """Return common keyword options for marker-only line plots."""

    return _with_overrides(
        {
            "color": color,
            "linestyle": "none",
            "marker": "o",
            "markersize": 4.5,
        },
        overrides,
    )


def markerline(color: ColorLike = c.fubuki.base, **overrides: Any) -> dict[str, Any]:
    """Return common keyword options for marker-only line plots."""

    return _with_overrides(
        {
            "color": color,
            "linewidth": 2.0,
            "marker": "o",
            "markersize": 3.0,
        },
        overrides,
    )


def scatter(color: ColorLike = c.fubuki.base, **overrides: Any) -> dict[str, Any]:
    """Return common keyword options for scatter plots."""

    return _with_overrides(
        {
            "color": color,
            "s": 24,
            "edgecolors": "none",
            "alpha": 0.95,
        },
        overrides,
    )


def errorbar(color: ColorLike = c.fubuki.base, **overrides: Any) -> dict[str, Any]:
    """Return common keyword options for errorbar plots."""

    return _with_overrides(
        {
            "color": color,
            "elinewidth": 1.0,
            "capsize": 2.5,
            "capthick": 1.0,
            "linestyle": "none",
            "marker": "o",
            "markersize": 4.0,
        },
        overrides,
    )


def fill(color: ColorLike = c.fubuki.base, **overrides: Any) -> dict[str, Any]:
    """Return common keyword options for filled regions."""

    return _with_overrides(
        {
            "color": color,
            "alpha": 0.25,
            "linewidth": 0,
        },
        overrides,
    )


def hist(color: ColorLike = c.fubuki.base, **overrides: Any) -> dict[str, Any]:
    """Return common keyword options for histograms."""

    return _with_overrides(
        {
            "color": color,
            "alpha": 0.9,
            "edgecolor": c.neutral.ink,
            "linewidth": 0.6,
        },
        overrides,
    )


def savefig(**overrides: Any) -> dict[str, Any]:
    """Return common keyword options for saving figures."""

    return _with_overrides(
        {
            "bbox_inches": "tight",
            "dpi": 300,
        },
        overrides,
    )


__all__ = [
    "ColorLike",
    "errorbar",
    "fill",
    "hist",
    "line",
    "markerline",
    "markers",
    "savefig",
    "scatter",
]
