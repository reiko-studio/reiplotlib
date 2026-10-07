"""Small matplotlib utilities with reiplotlib color defaults."""

from . import color, colors, export, layouts, options, palettes
from .axes import (
    clean_axes,
    clean_legend,
    drop_axis_labels,
    label_panel,
    percent_axis,
    use_palette,
)
from .palette import (
    Color,
    Palette,
    cycle,
    palette,
)
from .style import STYLE, apply_style, rc_context

__all__ = [
    "Color",
    "Palette",
    "STYLE",
    "apply_style",
    "clean_axes",
    "clean_legend",
    "color",
    "colors",
    "cycle",
    "drop_axis_labels",
    "export",
    "label_panel",
    "layouts",
    "options",
    "palette",
    "palettes",
    "percent_axis",
    "rc_context",
    "use_palette",
]
