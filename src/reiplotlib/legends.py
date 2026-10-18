"""Collect shared legend entries and arrange them in independent groups."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Literal

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.container import ErrorbarContainer
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

DuplicatePolicy = Literal["check", "first", "last", "error"]


def _axes(axes):
    if isinstance(axes, Axes):
        yield axes
    elif isinstance(axes, Iterable) and not isinstance(axes, (str, bytes)):
        for item in axes:
            yield from _axes(item)
    else:
        raise TypeError("Expected an Axes or an iterable of axes")


def _freeze(value):
    if isinstance(value, np.ndarray):
        return (value.shape, _freeze(value.tolist()))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    return value


def _signature(handle):
    # Compare appearance, never the coordinates represented by the handle.
    if isinstance(handle, Line2D):
        properties = (
            "color",
            "linestyle",
            "linewidth",
            "marker",
            "markersize",
            "markerfacecolor",
            "markeredgecolor",
            "markeredgewidth",
            "fillstyle",
            "alpha",
            "drawstyle",
        )
        return (
            "line",
            tuple(_freeze(getattr(handle, f"get_{p}")()) for p in properties),
            # get_linestyle collapses every custom dash sequence to '--'.
            _freeze(handle._unscaled_dash_pattern),
        )
    if isinstance(handle, ErrorbarContainer):
        line, caps, collections = handle.lines
        return (
            "errorbar",
            handle.has_xerr,
            handle.has_yerr,
            _signature(line) if line is not None else None,
            tuple(_signature(cap) for cap in caps),
            tuple(
                (
                    _freeze(c.get_colors()),
                    _freeze(c.get_linewidths()),
                    _freeze(c.get_linestyles()),
                    c.get_alpha(),
                )
                for c in collections
            ),
        )
    if isinstance(handle, PathCollection):
        return (
            "scatter",
            _freeze(handle.get_facecolors()),
            _freeze(handle.get_edgecolors()),
            _freeze(handle.get_sizes()),
            _freeze(handle.get_linewidths()),
            handle.get_alpha(),
            tuple(
                (_freeze(path.vertices), _freeze(path.codes))
                for path in handle.get_paths()
            ),
        )
    if isinstance(handle, Patch):
        return (
            type(handle),
            handle.get_facecolor(),
            handle.get_edgecolor(),
            handle.get_linewidth(),
            _freeze(handle.get_linestyle()),
            handle.get_hatch(),
            handle.get_alpha(),
        )
    return None


def _select(entries, order, include):
    def names(values, argument):
        if isinstance(values, str):
            raise TypeError(f"{argument} must be a sequence of labels, not a string")
        result = list(values)
        if len(set(result)) != len(result):
            raise ValueError(f"{argument} contains repeated labels")
        for label in result:
            if label not in entries:
                raise KeyError(f"Unknown legend label: {label!r}")
        return result

    selected = list(entries) if include is None else names(include, "include")
    if order is not None:
        priority = names(order, "order")
        if any(label not in selected for label in priority):
            raise ValueError("order contains labels excluded by include")
        selected = priority + [label for label in selected if label not in priority]
    return {label: entries[label] for label in selected}


def collect_legend(
    axes,
    *,
    order: Iterable[str] | None = None,
    include: Iterable[str] | None = None,
    duplicates: DuplicatePolicy = "check",
) -> dict[str, Any]:
    """Collect labeled handles across axes into an ordered label-to-handle dict.

    Accepts a single axes, a subplot array, or nested iterables. Empty/private
    labels follow Matplotlib's normal exclusion rules. Default order is first
    encounter; include selects labels, and order puts listed labels first.
    Missing requested labels raise KeyError rather than being silently dropped.

    With duplicates="check", matching line, errorbar, scatter, and patch styles
    collapse to the first handle; different styles raise ValueError. Data values
    are not compared. Unknown handle types require the same object or an explicit
    duplicate policy. "first"/"last" choose a handle without comparing styles;
    "error" rejects any repeated label. Exact style properties are compared,
    so equivalent aliases can require an explicit policy.
    """
    if duplicates not in ("check", "first", "last", "error"):
        raise ValueError("duplicates must be 'check', 'first', 'last', or 'error'")
    entries = {}
    for ax in _axes(axes):
        handles, labels = ax.get_legend_handles_labels()
        for handle, label in zip(handles, labels, strict=True):
            if label in entries:
                previous = entries[label]
                if duplicates == "error":
                    raise ValueError(f"Repeated legend label: {label!r}")
                if duplicates == "first":
                    continue
                if duplicates == "check" and previous is not handle:
                    signature = _signature(previous)
                    if signature is None or signature != _signature(handle):
                        raise ValueError(
                            f"Conflicting legend styles for {label!r}; use distinct "
                            "labels, duplicates='first'/'last', or explicit entries"
                        )
                if duplicates == "check":
                    continue
            entries[label] = handle
    return _select(entries, order, include)


def figure_legend(
    fig: Figure,
    axes=None,
    *,
    entries: Mapping[str, Any] | None = None,
    order: Iterable[str] | None = None,
    include: Iterable[str] | None = None,
    duplicates: DuplicatePolicy = "check",
    group: str = "shared",
    **kwargs: Any,
) -> Legend | None:
    """Draw a shared figure legend, replacing only the same named group.

    Collects from fig.axes by default; pass axes to limit collection, or entries
    as a label-to-handle mapping (including custom proxy handles). Returns a
    Matplotlib Legend, or None when selection is empty. Repeated calls replace
    the same group; different group names coexist, as do ordinary fig legends.

    Defaults to an unframed legend outside the upper center. For automatic space
    reservation use constrained layout; placement and remaining keywords pass
    through to fig.legend. This helper does not avoid overlaps between groups.
    """
    if not isinstance(group, str) or not group:
        raise ValueError("group must be a nonempty string")
    if entries is not None and axes is not None:
        raise ValueError("Supply axes or explicit entries, not both")
    if "handles" in kwargs or "labels" in kwargs:
        raise TypeError("Use entries={label: handle} for explicit legend handles")
    if entries is None:
        entries = collect_legend(
            fig.axes if axes is None else axes,
            order=order,
            include=include,
            duplicates=duplicates,
        )
    else:
        entries = _select(entries, order, include)
    gid = f"reiplotlib.legend:{group}"
    previous = [legend for legend in fig.legends if legend.get_gid() == gid]
    result = None
    if entries:
        options = {
            "frameon": False,
            "loc": "outside upper center",
            "handlelength": 1.4,
            "labelspacing": 0.3,
            "columnspacing": 1.0,
        }
        options.update(kwargs)
        result = fig.legend(list(entries.values()), list(entries), **options)
        result.set_gid(gid)
    for legend in previous:
        legend.remove()
    return result


def axes_legend(
    ax: Axes,
    axes=None,
    *,
    entries: Mapping[str, Any] | None = None,
    order: Iterable[str] | None = None,
    include: Iterable[str] | None = None,
    duplicates: DuplicatePolicy = "check",
    **kwargs: Any,
) -> Legend | None:
    """Put a shared legend inside one axes, collecting from several panels.

    ``ax`` is the destination; ``axes`` supplies entries and defaults to all axes
    in its figure. Selection and duplicate policies match figure_legend. Explicit
    proxy entries are also accepted. Returns the Matplotlib Legend or None for an
    empty selection. Replaces the destination's ordinary axes legend and leaves
    other panels and figure legends untouched. Existing legends elsewhere are
    not automatically removed.
    """
    if entries is not None and axes is not None:
        raise ValueError("Supply axes or explicit entries, not both")
    if "handles" in kwargs or "labels" in kwargs:
        raise TypeError("Use entries={label: handle} for explicit legend handles")
    if entries is None:
        entries = collect_legend(
            ax.figure.axes if axes is None else axes,
            order=order,
            include=include,
            duplicates=duplicates,
        )
    else:
        entries = _select(entries, order, include)
    if not entries:
        previous = ax.get_legend()
        if previous is not None:
            previous.remove()
        return None
    options = {
        "frameon": False,
        "loc": "upper right",
        "handlelength": 1.4,
        "labelspacing": 0.3,
        "columnspacing": 1.0,
    }
    options.update(kwargs)
    return ax.legend(list(entries.values()), list(entries), **options)
