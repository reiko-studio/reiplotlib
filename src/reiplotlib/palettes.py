"""Categorical palettes and Matplotlib property cycles."""

from collections.abc import Iterable
from types import MappingProxyType
from typing import TypeAlias

from cycler import cycler

from . import colors as c
from .colors import Color

Palette: TypeAlias = tuple[Color, ...]

_definitions = {
    # Paul Tol's bright scheme, in the author's recommended cycle order.
    # https://sronpersonalpages.nl/~pault/#sec:qualitative
    "tol_bright": (
        Color("tol_bright.blue", "#4477AA"),
        Color("tol_bright.red", "#EE6677"),
        Color("tol_bright.green", "#228833"),
        Color("tol_bright.yellow", "#CCBB44"),
        Color("tol_bright.cyan", "#66CCEE"),
        Color("tol_bright.purple", "#AA3377"),
        Color("tol_bright.gray", "#BBBBBB"),
    ),
    "myth": (
        Color("myth.gura", "#3887B7"),
        Color("myth.kiara", "#D56A32"),
        Color("myth.ina", "#594967"),
        Color("myth.calliope", "#C75D83"),
        Color("myth.amelia", "#A68A2D"),
    ),
    "grove": (
        Color("grove.blue", "#3569A8"),
        Color("grove.ochre", "#BA7336"),
        Color("grove.teal", "#27847F"),
        Color("grove.rose", "#B64F6D"),
        Color("grove.violet", "#7864A4"),
        Color("grove.olive", "#777C3B"),
    ),
    "duo": (c.fubuki.base, c.mio.base, c.accent.gold, c.accent.green),
    "paper": (
        c.neutral.ink,
        c.fubuki.dark,
        c.mio.dark,
        c.accent.gold,
        c.accent.green,
        c.neutral.muted,
    ),
    "soft": (
        c.fubuki.light,
        c.mio.light,
        c.accent.gold,
        c.accent.green,
        c.neutral.muted,
    ),
    "contrast": (
        c.fubuki.dark,
        c.mio.base,
        c.neutral.ink,
        c.accent.gold,
        c.accent.green,
    ),
    "ina": (c.ina.purple_dark, c.ina.gold, c.ina.pink, c.ina.purple, c.ina.gold_dark),
    "ina_contrast": (c.ina.purple, c.ina.gold),
    "ina_dark_contrast": (c.ina.purple_dark, c.ina.gold_dark),
    "suisei": (c.suisei.blue, c.suisei.blue_dark),
}


named = MappingProxyType(_definitions)
grove = named["grove"]
myth = named["myth"]
tol_bright = named["tol_bright"]
duo = named["duo"]
paper = named["paper"]
soft = named["soft"]
contrast = named["contrast"]
ina = named["ina"]
ina_contrast = named["ina_contrast"]
ina_dark_contrast = named["ina_dark_contrast"]
suisei = named["suisei"]


def get(name: str = "grove") -> Palette:
    """Return a named categorical palette."""
    return named[name]


def cycle(palette: str | Iterable[str] = "grove"):
    """Return a property cycle from a palette name or sequence of colors."""
    values = get(palette) if isinstance(palette, str) else tuple(palette)
    return cycler(color=values)


__all__ = [
    "Palette",
    "get",
    "cycle",
    "named",
    "grove",
    "myth",
    "tol_bright",
    "duo",
    "paper",
    "soft",
    "contrast",
    "ina",
    "ina_contrast",
    "ina_dark_contrast",
    "suisei",
]
