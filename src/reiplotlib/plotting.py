"""Drawing helpers which complement the keyword presets in options."""

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.container import ErrorbarContainer
from matplotlib.markers import MarkerStyle


def shade(ax: Axes, x, y, yerr, **kwargs: Any):
    """Fill an uncertainty band around y, returning ax.fill_between's artist.

    ``yerr`` is a nonnegative scalar or length-N sequence for symmetric widths,
    or shape (2, N) for lower/upper widths, as in Matplotlib errorbar. Widths are
    distances from y, not absolute bounds. NaNs and masks produce gaps.

    Defaults to alpha=0.2 and no outline. Without an explicit color, reuse the
    most recently plotted line's color, if present. Other keywords (including
    where, step, interpolate and label) pass through to fill_between. This draws
    only the band; it does not compute statistics or plot a central line.
    """
    values = np.ma.asarray(y)
    errors = np.ma.asarray(yerr)
    if values.ndim > 1:
        raise ValueError("y must be a scalar or one-dimensional sequence")
    if errors.ndim <= 1:
        lower = upper = errors
    elif errors.ndim == 2 and errors.shape[0] == 2:
        lower, upper = errors
    else:
        raise ValueError("yerr must be scalar, shape (N,), or shape (2, N)")
    if np.any(errors < 0):
        raise ValueError("yerr must contain nonnegative widths")
    kwargs.setdefault("alpha", 0.2)
    kwargs.setdefault("linewidth", 0)
    if not any(key in kwargs for key in ("color", "facecolor", "facecolors", "fc")):
        if ax.lines:
            kwargs["color"] = ax.lines[-1].get_color()
    return ax.fill_between(x, values - lower, values + upper, **kwargs)


class _AdaptiveErrorbarContainer(ErrorbarContainer):
    """An ordinary errorbar container with a removable visibility controller."""

    def remove(self) -> None:
        self._visibility_controller.remove()
        super().remove()


class _ErrorbarVisibility(Artist):
    def __init__(self, container: ErrorbarContainer, threshold: float):
        super().__init__()
        self.container = container
        self.threshold = threshold
        line, caps, collections = container.lines
        self.line = line
        directions = []
        if container.has_xerr:
            directions.append("x")
        if container.has_yerr:
            directions.append("y")
        self.bars = {}
        for direction, collection in zip(directions, collections, strict=True):
            self.bars[direction] = (
                collection,
                collection.get_segments(),
                collection.get_edgecolors().copy(),
                np.asarray(collection.get_linewidths()).copy(),
            )
        self.caps = []
        for cap in caps:
            direction = "x" if cap.get_marker() == "|" else "y"
            x, y = cap.get_data()
            self.caps.append(
                (cap, direction, np.asanyarray(x).copy(), np.asanyarray(y).copy())
            )
        artists = [*caps, *collections]
        if line is not None:
            artists.append(line)
        # Run before the existing bars/caps, on the same render (not draw_event).
        self.set_zorder(min(a.get_zorder() for a in artists) - 1)
        self.set_in_layout(False)

    def draw(self, renderer) -> None:
        if not self.get_visible():
            return
        diameter = {"x": 0.0, "y": 0.0}
        marker = None
        if self.line is not None and self.line.get_visible():
            candidate = MarkerStyle(self.line.get_marker())
            if candidate.get_path().vertices.size and self.line.get_markersize() > 0:
                marker = candidate
        if marker is not None:
            bounds = marker.get_path().transformed(marker.get_transform()).get_extents()
            edge = self.line.get_markeredgewidth() or 0.0
            edgecolor = self.line.get_markeredgecolor()
            if isinstance(edgecolor, str) and edgecolor.lower() == "none":
                edge = 0.0
            for direction, extent in (("x", bounds.width), ("y", bounds.height)):
                diameter[direction] = renderer.points_to_pixels(
                    self.line.get_markersize() * extent + edge
                )
        masks = {}
        for direction, (collection, segments, colors, widths) in self.bars.items():
            component = 0 if direction == "x" else 1
            spans = []
            for segment in segments:
                if np.shape(segment) != (2, 2):
                    spans.append(np.nan)
                    continue
                display = collection.get_transform().transform(segment)
                spans.append(abs(display[1, component] - display[0, component]))
            spans = np.asarray(spans)
            mask = np.isfinite(spans) & (spans > self.threshold * diameter[direction])
            masks[direction] = mask
            collection.set_segments(
                [s for s, keep in zip(segments, mask, strict=True) if keep]
            )
            # Keep per-point styles aligned when some, but not all, bars disappear.
            collection.set_edgecolors(
                colors[mask] if len(colors) == len(mask) else colors
            )
            collection.set_linewidths(
                widths[mask] if len(widths) == len(mask) else widths
            )
        for cap, direction, x, y in self.caps:
            mask = masks[direction]
            cap.set_data(x[mask], y[mask])
        self.stale = False


def errorbar(
    ax: Axes,
    x: Any,
    y: Any,
    yerr: Any = None,
    xerr: Any = None,
    *,
    hide_small_errors: bool = True,
    min_error_size: float = 1.0,
    **kwargs: Any,
) -> ErrorbarContainer:
    """Draw error bars, optionally hiding those smaller than their markers.

    Each point and error direction is checked independently at draw time.
    The full lower-to-upper span is compared with the marker's displayed
    width/height (including its edge), multiplied by ``min_error_size``.
    Zooms, axis scales, figure sizes and export DPI are handled on every draw.
    Original errors still affect autoscaling and are never modified.

    Matplotlib errorbar keywords, units, asymmetric errors and ``errorevery``
    are supported on rectilinear axes. Automatic hiding does not support
    one-sided limit arrows or polar axes; use ``hide_small_errors=False``
    for those. Without a marker, all finite nonzero bars remain visible.
    Returns a normal-compatible ErrorbarContainer; ``remove()`` also removes
    the visibility controller. Setting ``hide_small_errors=False`` delegates
    directly to ``ax.errorbar``.
    """
    if not np.isfinite(min_error_size) or min_error_size < 0:
        raise ValueError("min_error_size must be finite and nonnegative")
    if hide_small_errors and (xerr is not None or yerr is not None):
        if ax.name != "rectilinear":
            raise ValueError("Automatic hiding requires rectilinear axes")
        limits = ("lolims", "uplims", "xlolims", "xuplims")
        if any(np.any(kwargs.get(k, False)) for k in limits):
            raise ValueError("Use hide_small_errors=False for one-sided limit arrows")
    original = ax.errorbar(x, y, yerr=yerr, xerr=xerr, **kwargs)
    if not hide_small_errors or (xerr is None and yerr is None):
        return original
    container = _AdaptiveErrorbarContainer(
        original.lines,
        has_xerr=original.has_xerr,
        has_yerr=original.has_yerr,
        label=original.get_label(),
    )
    ax.containers.remove(original)
    ax.add_container(container)
    controller = _ErrorbarVisibility(container, min_error_size)
    container._visibility_controller = controller
    ax.add_artist(controller)
    return container
