"""Compact inset styling and backgrounds fitted to rendered decorations."""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox, IdentityTransform

__all__ = ["style_inset", "inset_backing"]


def style_inset(
    ax: Axes, *, labelsize=8, ticksize=7, linewidth=0.7, ticklength=2
) -> Axes:
    """Apply compact typography and strokes to an existing inset, returning it.

    Sizes and lengths are in points. Labels and titles use ``labelsize``; tick
    labels and scientific-notation offsets use ``ticksize``. Minor ticks are
    half the major tick length. Existing limits, placement, colors, tick
    locators, spine visibility, grid and axes facecolor are preserved.
    """
    ax.tick_params(which="both", labelsize=ticksize, width=linewidth, pad=2)
    ax.tick_params(which="major", length=ticklength)
    ax.tick_params(which="minor", length=ticklength / 2)
    for axis in (ax.xaxis, ax.yaxis):
        axis.label.set_fontsize(labelsize)
        axis.get_offset_text().set_fontsize(ticksize)
    for title in (ax.title, ax._left_title, ax._right_title):
        title.set_fontsize(labelsize)
    for spine in ax.spines.values():
        spine.set_linewidth(linewidth)
    return ax


def _container(inset):
    def parent(axes):
        for ax in axes:
            if inset in ax.child_axes:
                return ax
            found = parent(ax.child_axes)
            if found is not None:
                return found
        return None

    fig = inset.figure
    if fig is None:
        raise ValueError("inset must belong to a figure")
    host = parent(fig.axes)
    if host is not None:
        return host
    if inset in fig.axes:
        return fig
    raise ValueError("inset must be attached to a figure or parent axes")


class _InsetBacking(Rectangle):
    def __init__(self, inset, host, pad, **kwargs):
        self._inset = inset
        self._host = host
        self._pad = pad
        super().__init__(
            (0, 0), 0, 0, transform=IdentityTransform(), clip_on=False, **kwargs
        )

    def _update_bounds(self, renderer):
        children = (
            self._host.child_axes if isinstance(self._host, Axes) else self._host.axes
        )
        if self._inset not in children or not self._inset.get_visible():
            return False
        bbox = self._inset.get_tightbbox(renderer)
        if bbox is None or not np.isfinite(bbox.extents).all():
            return False
        self.set_bounds(*bbox.padded(renderer.points_to_pixels(self._pad)).bounds)
        return True

    def get_window_extent(self, renderer=None):
        if renderer is None:
            renderer = self.figure._get_renderer()
        if not self._update_bounds(renderer):
            return Bbox.from_bounds(0, 0, 0, 0)
        return super().get_window_extent(renderer)

    def draw(self, renderer):
        if self.get_visible() and self._update_bounds(renderer):
            super().draw(renderer)


def inset_backing(
    inset: Axes, *, pad=3, facecolor="white", alpha=0.85, edgecolor="none", **kwargs
) -> Rectangle:
    """Place a background behind an inset's axes, tick labels, labels and title.

    ``pad`` adds space in points around the rendered tight bounding box. The
    Rectangle updates before every draw and tight-bounds query, including after
    resizing, label edits, and PNG/PDF export. No draw callbacks are installed.
    Its color/alpha are independent of the inset's own facecolor; use
    ``inset.set_facecolor(\"none\")`` for a translucent plot area too.

    Create the inset with ``ax.inset_axes(bounds)`` for native parent-relative
    placement. The backing is attached to the same container as the inset,
    immediately below its current zorder. Keep both above the parent data when
    using figure-level inset axes. Placement and limits remain caller controlled.
    Other keywords style the Rectangle, e.g. ``linewidth`` or ``zorder``;
    transform and clipping are fixed so labels outside the axes remain covered.

    Returns an editable Rectangle: ``backing.remove()`` removes it. Calling this
    helper again on the same inset replaces the previous backing. Hiding or
    removing the inset suppresses its backing; remove the backing as well when
    discarding the inset to release both artists.
    """
    if not np.isfinite(pad) or pad < 0:
        raise ValueError("pad must be finite and nonnegative")
    if "transform" in kwargs or "clip_on" in kwargs:
        raise TypeError("backing transform and clipping are managed automatically")
    host = _container(inset)
    kwargs.setdefault("zorder", inset.get_zorder() - 0.01)
    backing = _InsetBacking(
        inset,
        host,
        pad,
        facecolor=facecolor,
        alpha=alpha,
        edgecolor=edgecolor,
        **kwargs,
    )
    previous = getattr(inset, "_rpl_inset_backing", None)
    if previous is not None and previous.figure is not None:
        previous.remove()
    host.add_artist(backing)
    inset._rpl_inset_backing = backing
    return backing
