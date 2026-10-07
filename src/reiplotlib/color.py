"""Compatibility alias for :mod:`reiplotlib.colors`."""

from .colors import *  # noqa: F403
from .colors import __all__ as _colors_all
from .palettes import cycle, get

palette = get

__all__ = [*_colors_all, "cycle", "get", "palette"]
