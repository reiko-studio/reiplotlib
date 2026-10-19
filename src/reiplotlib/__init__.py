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
from .colors import Color, ColorFamily, NamedColor
from .colorscale import ColorScale
from .legends import axes_legend, collect_legend, figure_legend
from .palettes import Palette, cycle
from .palettes import get as palette
from .plotting import errorbar, shade
from .secondary import secondary_xaxis, secondary_yaxis
from .series import SeriesStyle
from .style import STYLE, apply_style, rc_context

__all__ = [
    "Color",
    "ColorFamily",
    "ColorScale",
    "NamedColor",
    "Palette",
    "STYLE",
    "SeriesStyle",
    "apply_style",
    "autoscale_y",
    "axes_legend",
    "clean_axes",
    "clean_legend",
    "colors",
    "collect_legend",
    "cycle",
    "drop_axis_labels",
    "export",
    "figure_legend",
    "errorbar",
    "label_panel",
    "layouts",
    "options",
    "palette",
    "palettes",
    "percent_axis",
    "rc_context",
    "shade",
    "secondary_xaxis",
    "secondary_yaxis",
    "use_palette",
]
