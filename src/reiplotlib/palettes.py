"""Named color palettes for reiplotlib."""

from __future__ import annotations

from collections.abc import Iterable

from cycler import cycler

from . import colors as c
from .palette import Color

duo = (c.fubuki.base, c.mio.base, c.accent.gold, c.accent.green)
paper = (
    c.neutral.ink,
    c.fubuki.dark,
    c.mio.dark,
    c.accent.gold,
    c.accent.green,
    c.neutral.muted,
)
soft = (
    c.fubuki.light,
    c.mio.light,
    c.accent.gold,
    c.accent.green,
    c.neutral.muted,
)
contrast = (
    c.fubuki.dark,
    c.mio.base,
    c.neutral.ink,
    c.accent.gold,
    c.accent.green,
)
basic = (
    c.basic.bright_red,
    c.basic.dark_blue,
    c.basic.dark_red,
    c.basic.light_blue,
)
ina = (
    c.ina.purple_dark,
    c.ina.gold,
    c.ina.pink,
    c.ina.purple,
    c.ina.gold_dark,
)
ina_contrast = (c.ina.purple, c.ina.gold)
ina_dark_contrast = (c.ina.purple_dark, c.ina.gold_dark)
suisei = (c.suisei.blue, c.suisei.blue_dark)

named = {
    "duo": duo,
    "paper": paper,
    "soft": soft,
    "contrast": contrast,
    "basic": basic,
    "ina": ina,
    "ina_contrast": ina_contrast,
    "ina_dark_contrast": ina_dark_contrast,
    "suisei": suisei,
}


def get(name: str = "duo") -> tuple[Color, ...]:
    """Return a named palette."""

    return named[name]


def cycle(palette: str | Iterable[str] = "duo"):
    """Return a matplotlib property cycle for a named palette or color sequence."""

    values = get(palette) if isinstance(palette, str) else tuple(palette)
    return cycler(color=values)


__all__ = [
    "basic",
    "contrast",
    "cycle",
    "duo",
    "get",
    "ina",
    "ina_contrast",
    "ina_dark_contrast",
    "named",
    "paper",
    "soft",
    "suisei",
]
