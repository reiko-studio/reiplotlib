"""Axes helpers for common matplotlib cleanup."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from cycler import cycler
from matplotlib.axes import Axes
from matplotlib.ticker import PercentFormatter

Side = Literal["left", "right", "top", "bottom"]
Axis = Literal["x", "y", "both"]


def clean_axes(
    ax: Axes,
    *,
    keep: Iterable[Side] = ("left", "bottom"),
    grid: bool = True,
    legend: bool = True,
) -> Axes:
    """Hide unused spines, soften ticks, and optionally clean the legend."""

    visible = set(keep)
    for side, spine in ax.spines.items():
        spine.set_visible(side in visible)
    ax.tick_params(length=0)
    ax.grid(grid)

    if legend:
        current = ax.get_legend()
        if current is not None:
            current.set_frame_on(False)
    return ax


def clean_legend(
    ax: Axes,
    *,
    frame: bool = False,
    handlelength: float = 1.4,
    labelspacing: float = 0.3,
    columnspacing: float = 1.0,
    ncols: int | None = None,
    **kwargs: Any,
) -> Axes:
    """Create or update a compact legend for an axes."""

    handles, labels = ax.get_legend_handles_labels()
    if not handles:
        return ax

    opts: dict[str, Any] = {
        "frameon": frame,
        "handlelength": handlelength,
        "labelspacing": labelspacing,
        "columnspacing": columnspacing,
    }
    if ncols is not None:
        opts["ncols"] = ncols
    opts.update(kwargs)

    legend = ax.legend(handles, labels, **opts)
    legend.set_frame_on(frame)
    return ax


def percent_axis(
    ax: Axes,
    *,
    axis: Literal["x", "y"] = "y",
    decimals: int = 0,
    xmax: float = 1.0,
) -> Axes:
    """Format an axis as percentages."""

    formatter = PercentFormatter(xmax=xmax, decimals=decimals)
    if axis == "x":
        ax.xaxis.set_major_formatter(formatter)
    else:
        ax.yaxis.set_major_formatter(formatter)
    return ax


def use_palette(ax: Axes, palette: Iterable[str]) -> Axes:
    """Apply a color palette as an axes property cycle."""

    ax.set_prop_cycle(cycler(color=tuple(palette)))
    return ax


def drop_axis_labels(
    ax: Axes,
    axis: Axis = "both",
    *,
    tick_labels: bool = True,
    ticks: bool = True,
) -> Axes:
    """Remove x and/or y axis labels, tick labels, and tick marks."""

    if axis in {"x", "both"}:
        ax.set_xlabel("")
        ax.tick_params(
            axis="x",
            which="both",
            bottom=not ticks,
            top=not ticks,
            labelbottom=not tick_labels,
            labeltop=not tick_labels,
        )
    if axis in {"y", "both"}:
        ax.set_ylabel("")
        ax.tick_params(
            axis="y",
            which="both",
            left=not ticks,
            right=not ticks,
            labelleft=not tick_labels,
            labelright=not tick_labels,
        )
    return ax


def label_panel(
    ax: Axes,
    label: str,
    *,
    x: float = -0.08,
    y: float = 1.04,
    weight: str = "bold",
    size: int = 12,
) -> Axes:
    """Add a small panel label like ``A`` or ``B`` above an axes."""

    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        fontweight=weight,
        fontsize=size,
        va="bottom",
        ha="left",
    )
    return ax
