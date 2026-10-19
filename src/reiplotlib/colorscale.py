"""Reusable numeric color mappings and their matching colorbars."""

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar
from matplotlib.colors import Colormap, Normalize

from . import options

__all__ = ["ColorScale"]


class ColorScale:
    """Map numeric values to RGBA colors with a fixed, shared normalization.

    ``cmap`` accepts a Matplotlib colormap name or Colormap object. The default
    linear range is 0 to 1; supply vmin/vmax for a different range, or a fully
    bounded Normalize instance (including LogNorm and BoundaryNorm). Explicit
    norm and vmin/vmax cannot be combined. An unbounded norm is rejected so a
    first subset cannot silently determine colors for later panels.

    Masks, NaNs, clipping, and under/over-range values follow the supplied
    colormap and norm. With the default unclipped Normalize, a colormap's
    configured under/over colors apply; otherwise its endpoint colors apply.
    Masked/NaN values use the colormap's bad color (usually transparent).

    The norm and colormap are shared, not copied. Editing them is an explicit
    change to the scale; ``mappable`` exposes the underlying ScalarMappable for
    use with ordinary Matplotlib plotting and colorbar APIs.
    """

    def __init__(
        self,
        cmap: str | Colormap = "viridis",
        *,
        vmin: float | None = None,
        vmax: float | None = None,
        norm: Normalize | None = None,
    ):
        if norm is not None:
            if vmin is not None or vmax is not None:
                raise ValueError("Supply norm or vmin/vmax, not both")
            if not isinstance(norm, Normalize):
                raise TypeError("norm must be a Matplotlib Normalize instance")
        else:
            norm = Normalize(
                vmin=0.0 if vmin is None else vmin,
                vmax=1.0 if vmax is None else vmax,
            )
        if norm.vmin is None or norm.vmax is None:
            raise ValueError("norm must have explicit vmin and vmax")
        if not np.isfinite([norm.vmin, norm.vmax]).all() or norm.vmin >= norm.vmax:
            raise ValueError("Color scale bounds must be finite with vmin < vmax")
        self.mappable = ScalarMappable(norm=norm, cmap=cmap)

    @property
    def norm(self) -> Normalize:
        """The shared Matplotlib normalization object."""
        return self.mappable.norm

    @property
    def cmap(self) -> Colormap:
        """The colormap used by the mapping and colorbars."""
        return self.mappable.cmap

    def __call__(self, values, *, alpha=None, bytes=False):
        """Return RGBA for a scalar or array, retaining masked/bad colors.

        A scalar yields a tuple and an array yields RGBA values with an extra
        final channel dimension. ``alpha``
        overrides opacity; ``bytes=True`` returns channels in the range 0–255.
        """
        return self.cmap(self.norm(values), alpha=alpha, bytes=bytes)

    def colorbar(self, ax=None, *, cax: Axes | None = None, **kwargs: Any) -> Colorbar:
        """Draw a matching colorbar, returning a Matplotlib Colorbar.

        Supply ``ax`` as one axes or a subplot array to reserve space beside
        those panels, or ``cax`` to use an existing colorbar axes. All axes must
        belong to one figure. Orientation, label, ticks, boundaries and other
        options pass through to Figure.colorbar; positioning remains editable.
        Automatic bars use the slim geometry from options.colorbar (aspect=50,
        fraction=0.035, pad=0.035) for either orientation. Explicit geometry
        overrides these defaults; an existing cax receives no geometry defaults.
        """
        axes = [] if ax is None else np.asarray(ax, dtype=object).ravel().tolist()
        if cax is not None:
            axes.append(cax)
        if not axes:
            raise ValueError("Provide ax or cax to place the colorbar")
        if any(not isinstance(pane, Axes) for pane in axes):
            raise TypeError("ax and cax must contain Matplotlib axes")
        fig = axes[0].figure
        if any(pane.figure is not fig for pane in axes):
            raise ValueError("All colorbar axes must belong to the same figure")
        if cax is None:
            kwargs = options.colorbar(**kwargs)
        return fig.colorbar(self.mappable, ax=ax, cax=cax, **kwargs)
