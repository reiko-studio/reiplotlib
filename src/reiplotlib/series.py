"""Explicit series identities independent of plotting order."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matplotlib.lines import Line2D

from . import options as o
from .options import ColorLike


@dataclass(frozen=True, kw_only=True)
class SeriesStyle:
    """Appearance for one series, usually stored in a dictionary by identity.

    ``line()`` and ``errorbar()`` return fresh keyword dictionaries. The display
    label is separate: pass ``label=style.label`` when plotting. Per-call
    overrides do not change the stored style. Color strings are recommended
    when the identity should remain fixed; a mutable NamedColor remains mutable.
    """

    color: ColorLike
    label: str | None = None
    marker: str | None = "o"
    linestyle: str = "-"
    markerfacecolor: ColorLike | None = None

    def _appearance(self) -> dict[str, Any]:
        kwargs = {
            "color": self.color,
            "marker": self.marker,
            "linestyle": self.linestyle,
        }
        if self.markerfacecolor is not None:
            kwargs["markerfacecolor"] = self.markerfacecolor
        return kwargs

    def line(self, **overrides: Any) -> dict[str, Any]:
        """Return marker-line options, without the display label."""
        kwargs = self._appearance()
        kwargs.update(overrides)
        return o.markerline(**kwargs)

    def errorbar(self, **overrides: Any) -> dict[str, Any]:
        """Return errorbar options, including this series' connecting line style."""
        kwargs = self._appearance()
        kwargs.update(overrides)
        return o.errorbar(**kwargs)

    def legend_handle(self, **overrides: Any) -> Line2D:
        """Return a standalone line/marker legend handle with the display label.

        This represents the series identity, not uncertainty bars. Actual
        ErrorbarContainers can be used when the legend should show those bars.
        """
        kwargs = self.line(**overrides)
        kwargs.setdefault("label", self.label)
        return Line2D([], [], **kwargs)
