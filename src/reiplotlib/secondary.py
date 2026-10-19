"""Secondary coordinates with explicit ticks that follow the visible range."""

import numpy as np
from matplotlib.axes._secondary_axes import SecondaryAxis
from matplotlib.ticker import FixedLocator, FuncFormatter


class _VisibleTicks(FixedLocator):
    def __call__(self):
        low, high = sorted(self.axis.get_view_interval())
        return self.locs[(self.locs >= low) & (self.locs <= high)]


class _SecondaryAxis(SecondaryAxis):
    def _set_scale(self):
        # matplotlib replaces locators when the parent changes scale.
        locator = self._axis.get_major_locator()
        formatter = self._axis.get_major_formatter()
        super()._set_scale()
        if isinstance(locator, _VisibleTicks):
            self._axis.set_major_locator(locator)
            self._axis.set_major_formatter(formatter)


def _secondary_axis(
    ax,
    orientation,
    functions,
    location,
    ticks,
    labels,
    label,
    labelsize,
    ticksize,
    kwargs,
):
    if labels is not None and ticks is None:
        raise ValueError("labels require explicit ticks")
    values = None
    if ticks is not None:
        values = np.asarray(list(ticks), dtype=float)
        if values.ndim != 1 or not np.all(np.isfinite(values)):
            raise ValueError(
                "ticks must be a one-dimensional sequence of finite values"
            )
        if len(np.unique(values)) != len(values):
            raise ValueError("ticks must be unique")
        if labels is not None:
            labels = list(labels)
            if len(labels) != len(values):
                raise ValueError("ticks and labels must have the same length")
    secondary = _SecondaryAxis(ax, orientation, location, functions, **kwargs)
    ax.add_child_axes(secondary)
    if values is not None:
        secondary._axis.set_major_locator(_VisibleTicks(values))
        if labels is not None:
            mapping = dict(zip(values, labels, strict=True))
            secondary._axis.set_major_formatter(
                FuncFormatter(lambda value, pos: mapping.get(value, ""))
            )
    if label is not None:
        setter = secondary.set_xlabel if orientation == "x" else secondary.set_ylabel
        setter(label, **({"fontsize": labelsize} if labelsize is not None else {}))
    if ticksize is not None:
        secondary.tick_params(axis=orientation, labelsize=ticksize)
    return secondary


def secondary_xaxis(
    ax,
    functions,
    *,
    location="top",
    ticks=None,
    labels=None,
    label=None,
    labelsize=None,
    ticksize=None,
    **kwargs,
):
    """Add a secondary x coordinate, returning a Matplotlib SecondaryAxis.

    ``functions=(forward, inverse)`` maps parent to secondary coordinates and
    back. Both callables must accept NumPy arrays and be monotonic over the
    plotted domain. Domain handling belongs to the supplied functions.

    Optional ``ticks`` are in secondary units and are filtered to the visible
    range on every draw, including after zooming or changing the parent scale.
    ``labels`` supplies matching strings; omitted ticks use Matplotlib's locator.
    ``labelsize`` and ``ticksize`` override the style's font sizes. Other keyword
    arguments go to Matplotlib's SecondaryAxis (for example ``transform``).
    The returned object supports normal formatting, tick control, and removal.
    """
    return _secondary_axis(
        ax, "x", functions, location, ticks, labels, label, labelsize, ticksize, kwargs
    )


def secondary_yaxis(
    ax,
    functions,
    *,
    location="right",
    ticks=None,
    labels=None,
    label=None,
    labelsize=None,
    ticksize=None,
    **kwargs,
):
    """Add a secondary y coordinate, returning a Matplotlib SecondaryAxis.

    Uses the same transforms, visible tick filtering, labels, typography and
    keyword arguments as :func:`secondary_xaxis`. The default location is right;
    use ``location="left"`` or a numeric position for another placement.
    This converts the parent coordinate; use ``ax.twinx()`` for independent data.
    """
    return _secondary_axis(
        ax, "y", functions, location, ticks, labels, label, labelsize, ticksize, kwargs
    )
