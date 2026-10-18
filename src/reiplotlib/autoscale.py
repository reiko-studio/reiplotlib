"""Visible-range y scaling, without altering the plotted data."""

import numpy as np
from matplotlib.collections import LineCollection, PathCollection


def _clip_y(vertices, bounds, connected=True):
    vertices = np.asarray(vertices, dtype=float)
    if vertices.ndim != 2 or vertices.shape[1] != 2:
        return []
    lo, hi = sorted(bounds)
    finite = np.isfinite(vertices).all(axis=1)
    values = list(vertices[finite & (vertices[:, 0] >= lo) & (vertices[:, 0] <= hi), 1])
    if connected:
        for a, b, valid in zip(vertices[:-1], vertices[1:], finite[:-1] & finite[1:]):
            if not valid or a[0] == b[0]:
                continue
            for x in (lo, hi):
                if min(a[0], b[0]) <= x <= max(a[0], b[0]):
                    values.append(a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))
    return values


def autoscale_y(ax, *, visible_only=True, margin=0.05, override=False, watch=False):
    """Scale shared y axes using data inside each sibling's current x limits.

    Supports data-coordinate lines, scatter and line collections (including
    error bars). Crossing line segments contribute their clipped endpoints;
    interpolation is performed in axis-scale coordinates, including log axes.
    Blended reference lines in y data coordinates are included, but vertical
    axes-coordinate guides are not. Images, bars and filled patches are not
    supported. Empty views retain their limits. Explicit y limits are preserved
    unless ``override=True``. ``watch=True`` also updates after x-limit changes.
    Return callback IDs as (axes, ID) pairs; disconnect with ax.callbacks.disconnect.
    """
    if not np.isfinite(margin) or margin < 0:
        raise ValueError('margin must be finite and nonnegative')
    siblings = list(ax.get_shared_y_axes().get_siblings(ax))
    eligible = override or all(a.get_autoscaley_on() for a in siblings)

    def update(_=None):
        if not eligible or (not override and not all(a.get_autoscaley_on() for a in siblings)):
            return
        values = []
        for pane in siblings:
            scale = pane.transScale
            bounds = scale.transform([[pane.get_xlim()[0], 1], [pane.get_xlim()[1], 1]])[:, 0]
            if not visible_only:
                bounds = (-np.inf, np.inf)

            def collect(vertices, connected=True):
                with np.errstate(invalid='ignore', divide='ignore'):
                    transformed = scale.transform(vertices)
                values.extend(_clip_y(transformed, bounds, connected))

            for line in pane.lines:
                if not line.get_visible():
                    continue
                xdata, ydata = line.get_transform().contains_branch_seperately(pane.transData)
                if not ydata:
                    continue
                xy = line.get_xydata()
                if not xdata:
                    values.extend(scale.transform(xy)[:, 1][np.isfinite(xy[:, 1])])
                else:
                    collect(line.get_path().vertices, line.get_linestyle() not in ('None', 'none', '', ' '))
            originals = {}
            for container in pane.containers:
                controller = getattr(container, '_visibility_controller', None)
                if controller is not None:
                    originals.update({collection: segments for collection, segments, *_ in controller.bars.values()})
            for collection in pane.collections:
                if not collection.get_visible():
                    continue
                if isinstance(collection, LineCollection) and collection.get_transform() == pane.transData:
                    for segment in originals.get(collection, collection.get_segments()):
                        collect(segment)
                elif isinstance(collection, PathCollection) and collection.get_offset_transform() == pane.transData:
                    collect(np.ma.filled(collection.get_offsets(), np.nan), False)
        values = np.asarray(values)
        values = values[np.isfinite(values)]
        if not values.size:
            return
        low, high = values.min(), values.max()
        if low == high:
            expansion = max(abs(low), 1.0) * 0.05
            low, high = low - expansion, high + expansion
        padding = (high - low) * margin
        limits = ax.transScale.inverted().transform([[1, low - padding], [1, high + padding]])[:, 1]
        if ax.yaxis_inverted():
            limits = limits[::-1]
        # Keep Matplotlib's auto/manual flag; subsequent calls still respect manual limits.
        ax.set_ylim(*limits, auto=None)

    update()
    return [(pane, pane.callbacks.connect('xlim_changed', update)) for pane in siblings] if watch else []
