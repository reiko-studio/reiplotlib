"""Color tokens and palette helpers for reiplotlib plots."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TypeAlias

from cycler import cycler


class Color(str):
    """Hex color token."""

    name: str
    hex: str

    def __new__(cls, name: str, hex: str) -> Color:
        obj = str.__new__(cls, hex)
        obj.name = name
        obj.hex = hex
        return obj


@dataclass(frozen=True)
class FubukiColors:
    """Fubuki color tokens."""

    base: Color = Color("fubuki.base", "#58BFCB")
    dark: Color = Color("fubuki.dark", "#1E7784")
    light: Color = Color("fubuki.light", "#BDECF1")


@dataclass(frozen=True)
class MioColors:
    """Mio color tokens."""

    base: Color = Color("mio.base", "#D35C7F")
    dark: Color = Color("mio.dark", "#87344F")
    light: Color = Color("mio.light", "#F4B6C7")


@dataclass(frozen=True)
class NeutralColors:
    """Neutral color tokens."""

    ink: Color = Color("neutral.ink", "#22242A")
    muted: Color = Color("neutral.muted", "#727783")
    paper: Color = Color("neutral.paper", "#FAFAF7")
    white: Color = Color("neutral.white", "#FFFFFF")
    grid: Color = Color("neutral.grid", "#D9DDE3")


@dataclass(frozen=True)
class AccentColors:
    """Supporting accent color tokens."""

    gold: Color = Color("accent.gold", "#D7A84F")
    green: Color = Color("accent.green", "#5BA56B")


@dataclass(frozen=True)
class BasicColors:
    """Basic high-contrast color tokens."""

    bright_red: Color = Color("basic.bright_red", "#ff0000")
    dark_red: Color = Color("basic.dark_red", "#9f0000")
    dark_blue: Color = Color("basic.dark_blue", "#000a64")
    light_blue: Color = Color("basic.light_blue", "#9e9efe")


@dataclass(frozen=True)
class InaColors:
    """Ina color tokens."""

    gold: Color = Color("ina.gold", "#eaa36d")
    gold_dark: Color = Color("ina.gold_dark", "#ca7845")
    pink: Color = Color("ina.pink", "#d1527a")
    purple: Color = Color("ina.purple", "#594967")
    purple_dark: Color = Color("ina.purple_dark", "#323142")


@dataclass(frozen=True)
class SuiseiColors:
    """Suisei color tokens."""

    blue: Color = Color("suisei.blue", "#76a7e8")
    blue_dark: Color = Color("suisei.blue_dark", "#35338d")


fubuki = FubukiColors()
mio = MioColors()
neutral = NeutralColors()
accent = AccentColors()
basic = BasicColors()
ina = InaColors()
suisei = SuiseiColors()

colors: Mapping[str, Color] = {
    "fubuki": fubuki.base,
    "fubuki_base": fubuki.base,
    "fubuki_dark": fubuki.dark,
    "fubuki_light": fubuki.light,
    "mio": mio.base,
    "mio_base": mio.base,
    "mio_dark": mio.dark,
    "mio_light": mio.light,
    "ink": neutral.ink,
    "muted": neutral.muted,
    "paper": neutral.paper,
    "grid": neutral.grid,
    "gold": accent.gold,
    "green": accent.green,
    "bright_red": basic.bright_red,
    "dark_red": basic.dark_red,
    "dark_blue": basic.dark_blue,
    "light_blue": basic.light_blue,
    "ina_gold": ina.gold,
    "ina_gold1": ina.gold,
    "ina_gold_dark": ina.gold_dark,
    "ina_gold2": ina.gold_dark,
    "ina_pink": ina.pink,
    "ina_pink1": ina.pink,
    "ina_purple": ina.purple,
    "ina_purple1": ina.purple,
    "ina_purple_dark": ina.purple_dark,
    "ina_purple2": ina.purple_dark,
    "suisei_blue": suisei.blue,
    "suisei_blue1": suisei.blue,
    "suisei_blue_dark": suisei.blue_dark,
    "suisei_blue2": suisei.blue_dark,
}

Palette: TypeAlias = tuple[Color, ...]
PaletteName: TypeAlias = str

palettes: Mapping[str, Palette] = {
    "duo": (fubuki.base, mio.base, accent.gold, accent.green),
    "paper": (
        neutral.ink,
        fubuki.dark,
        mio.dark,
        accent.gold,
        accent.green,
        neutral.muted,
    ),
    "soft": (fubuki.light, mio.light, accent.gold, accent.green, neutral.muted),
    "contrast": (fubuki.dark, mio.base, neutral.ink, accent.gold, accent.green),
    "basic": (
        basic.bright_red,
        basic.dark_blue,
        basic.dark_red,
        basic.light_blue,
    ),
    "ina": (ina.purple_dark, ina.gold, ina.pink, ina.purple, ina.gold_dark),
    "ina_contrast": (ina.purple, ina.gold),
    "ina_dark_contrast": (ina.purple_dark, ina.gold_dark),
    "suisei": (suisei.blue, suisei.blue_dark),
}


def palette(name: PaletteName = "duo") -> tuple[str, ...]:
    """Return hex colors for a named palette."""

    return tuple(palettes[name])


def cycle(name: PaletteName = "duo"):
    """Return a matplotlib property cycle for a named palette."""

    return cycler(color=palette(name))
