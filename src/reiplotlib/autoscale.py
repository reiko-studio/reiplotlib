"""Visible-range y scaling, without altering the plotted data."""

import numpy as np
from matplotlib.collections import LineCollection, PathCollection, PolyCollection
from matplotlib.path import Path


def _clip_y(vertices, bounds, connected=True):
    vertices = np.asarray(vertices, dtype=float)
    if vertices.ndim != 2 or vertices.shape[1] != 2:
        return []
    lo, hi = sorted(bounds)
    finite = np.isfinite(vertices).all(axis=1)
    values = list(vertices[finite & (vertices[:, 0] >= lo) & (vertices[:, 0] <= hi), 1])
    if connected:
        for a, b, valid in zip(
            vertices[:-1], vertices[1:], finite[:-1] & finite[1:], strict=True
        ):
            if not valid or a[0] == b[0]:
                continue
            for x in (lo, hi):
                if min(a[0], b[0]) <= x <= max(a[0], b[0]):
                    values.append(a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))
    return values


def _polygon_rings(path):
    """Yield separate closed rings without treating CLOSEPOLY dummies as data."""
    ring = []
    for vertices, code in path.iter_segments(curves=False, simplify=False):
        if code == Path.MOVETO:
            if ring:
                yield np.asarray(ring)
            ring = [vertices[-2:]]
        elif code == Path.CLOSEPOLY:
            if ring:
                yield np.asarray([*ring, ring[0]])
                ring = []
        elif code == Path.LINETO:
            ring.append(vertices[-2:])
    if ring:
        yield np.asarray(ring)


def autoscale_y(
    ax,
    *,
    visible_only=True,
    margin=0.05,
    bottom=None,
    top=None,
    override=False,
    watch=False,
):
    """Scale shared y axes using data inside each sibling's current x limits.

    Supports data-coordinate lines, scatter, line collections (including error
    bars), and polygon collections such as fill_between/shade bands. Polygon
    edges contribute their clipped endpoints, including crossings without any
    vertex inside the view. Masked gaps and separate rings are not bridged.
    Crossing line segments also contribute their clipped endpoints;
    interpolation is performed in axis-scale coordinates, including log axes.
    Blended reference lines in y data coordinates are included, but vertical
    axes-coordinate guides are not. Images, bars and individual patches are not
    supported. Polygon collections with nonzero offsets are excluded.

    ``bottom`` and ``top`` fix the numerical lower/upper bounds in data units;
    omitted bounds are fitted. Margin pads only free bounds, using the span
    after fixed bounds are applied. Inverted axes retain their direction.
    Log bounds must be positive. Nonpositive log data vertices are excluded.
    A fixed bound beyond the opposite visible extent raises ValueError.

    Empty views retain their limits. Explicit y limits are preserved unless
    ``override=True``, even when bottom/top is supplied. ``watch=True`` also
    updates after x-limit changes, retaining the requested fixed bounds.
    Return callback IDs as (axes, ID) pairs; disconnect with ax.callbacks.disconnect.
    """
    if not np.isfinite(margin) or margin < 0:
        raise ValueError("margin must be finite and nonnegative")
    for name, bound in (("bottom", bottom), ("top", top)):
        if bound is not None:
            if not np.isfinite(bound):
                raise ValueError(f"{name} must be finite")
            if ax.get_yscale() == "log" and bound <= 0:
                raise ValueError(f"{name} must be positive on a log axis")
    if bottom is not None and top is not None and bottom >= top:
        raise ValueError("bottom must be less than top")
    siblings = list(ax.get_shared_y_axes().get_siblings(ax))
    eligible = override or all(a.get_autoscaley_on() for a in siblings)

    def update(_=None):
        if not eligible or (
            not override and not all(a.get_autoscaley_on() for a in siblings)
        ):
            return
        values = []
        for pane in siblings:
            scale = pane.transScale
            bounds = scale.transform(
                [[pane.get_xlim()[0], 1], [pane.get_xlim()[1], 1]]
            )[:, 0]
            if not visible_only:
                bounds = (-np.inf, np.inf)

            def collect(
                vertices, connected=True, *, pane=pane, scale=scale, bounds=bounds
            ):
                vertices = np.asarray(vertices, dtype=float).copy()
                # LogScale can clip invalid values to finite sentinel coordinates.
                if pane.get_xscale() == "log":
                    vertices[vertices[:, 0] <= 0] = np.nan
                if pane.get_yscale() == "log":
                    vertices[vertices[:, 1] <= 0] = np.nan
                with np.errstate(invalid="ignore", divide="ignore"):
                    transformed = scale.transform(vertices)
                values.extend(_clip_y(transformed, bounds, connected))

            for line in pane.lines:
                if not line.get_visible():
                    continue
                xdata, ydata = line.get_transform().contains_branch_seperately(
                    pane.transData
                )
                if not ydata:
                    continue
                xy = line.get_xydata()
                if not xdata:
                    ys = xy[:, 1]
                    valid = np.isfinite(ys)
                    if pane.get_yscale() == "log":
                        valid &= ys > 0
                    values.extend(scale.transform(xy[valid])[:, 1])
                else:
                    collect(
                        line.get_path().vertices,
                        line.get_linestyle() not in ("None", "none", "", " "),
                    )
            originals = {}
            for container in pane.containers:
                controller = getattr(container, "_visibility_controller", None)
                if controller is not None:
                    originals.update(
                        {
                            collection: segments
                            for collection, segments, *_ in controller.bars.values()
                        }
                    )
            for collection in pane.collections:
                if not collection.get_visible():
                    continue
                if (
                    isinstance(collection, LineCollection)
                    and collection.get_transform() == pane.transData
                ):
                    for segment in originals.get(collection, collection.get_segments()):
                        collect(segment)
                elif (
                    isinstance(collection, PathCollection)
                    and collection.get_offset_transform() == pane.transData
                ):
                    collect(np.ma.filled(collection.get_offsets(), np.nan), False)
                elif (
                    isinstance(collection, PolyCollection)
                    and collection.get_transform() == pane.transData
                    and not np.any(collection.get_offsets())
                ):
                    for path in collection.get_paths():
                        for ring in _polygon_rings(path):
                            collect(ring)
        values = np.asarray(values)
        values = values[np.isfinite(values)]
        if not values.size:
            return
        low, high = values.min(), values.max()
        if bottom is not None:
            low = ax.transScale.transform([[1, bottom]])[0, 1]
        if top is not None:
            high = ax.transScale.transform([[1, top]])[0, 1]
        if low > high:
            raise ValueError("Fixed bound lies beyond the opposite visible extent")
        if low == high:
            expansion = max(abs(low), 1.0) * 0.05
            if bottom is None:
                low -= expansion
            if top is None:
                high += expansion
        padding = (high - low) * margin
        limits = ax.transScale.inverted().transform(
            [
                [1, low - padding if bottom is None else low],
                [1, high + padding if top is None else high],
            ]
        )[:, 1]
        if bottom is not None:
            limits[0] = bottom
        if top is not None:
            limits[1] = top
        if ax.yaxis_inverted():
            limits = limits[::-1]
        # Keep the auto/manual flag so later calls still respect manual limits.
        ax.set_ylim(*limits, auto=None)

    update()
    return (
        [(pane, pane.callbacks.connect("xlim_changed", update)) for pane in siblings]
        if watch
        else []
    )
