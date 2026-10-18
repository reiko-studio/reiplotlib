"""Small matplotlib utilities with reiplotlib color defaults."""

from . import colors, export, layouts, options, palettes
from .autoscale import autoscale_y
from .axes import (
    clean_axes,
    clean_legend,
    drop_axis_labels,
    label_panel,
    percent_axis,
    use_palette,
)
from .colors import Color, ColorFamily
from .palettes import Palette, cycle
from .palettes import get as palette
from .plotting import errorbar
from .style import STYLE, apply_style, rc_context

__all__ = [
    "Color",
    "ColorFamily",
    "Palette",
    "STYLE",
    "apply_style",
    "autoscale_y",
    "clean_axes",
    "clean_legend",
    "colors",
    "cycle",
    "drop_axis_labels",
    "export",
    "errorbar",
    "label_panel",
    "layouts",
    "options",
    "palette",
    "palettes",
    "percent_axis",
    "rc_context",
    "use_palette",
]
