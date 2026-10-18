"""Named color families and neutral colors for Matplotlib."""

from dataclasses import dataclass
from types import MappingProxyType

from ._color import Color, ColorFamily, NamedColor


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
ina = InaColors()
suisei = SuiseiColors()

red = ColorFamily(
    "red",
    base="#BF454B",
    dark="#7F2934",
    bright="#E4474D",
    light="#ECA1A4",
    pale="#F9E5E6",
)
orange = ColorFamily(
    "orange",
    base="#C77535",
    dark="#87451F",
    bright="#EC7D29",
    light="#EDBB92",
    pale="#FBEDDF",
)
gold = ColorFamily(
    "gold",
    base="#AD8A2D",
    dark="#755B1B",
    bright="#D4A52C",
    light="#E5D08E",
    pale="#F8F1D8",
)
green = ColorFamily(
    "green",
    base="#47845A",
    dark="#285638",
    bright="#3CA65C",
    light="#A5CFAD",
    pale="#E7F2E9",
)
teal = ColorFamily(
    "teal",
    base="#27847F",
    dark="#185A59",
    bright="#19A69B",
    light="#9ACFC8",
    pale="#E2F2EF",
)
blue = ColorFamily(
    "blue",
    base="#3569A8",
    dark="#23466F",
    bright="#3488D6",
    light="#A3C2E4",
    pale="#E6EFF9",
)
purple = ColorFamily(
    "purple",
    base="#7864A4",
    dark="#51416F",
    bright="#9667CE",
    light="#C6B7DF",
    pale="#F0EAF7",
)
pink = ColorFamily(
    "pink",
    base="#B64F7C",
    dark="#793450",
    bright="#DD5497",
    light="#E6AECA",
    pale="#F8E7F0",
)

families = MappingProxyType(
    {
        "red": red,
        "orange": orange,
        "gold": gold,
        "green": green,
        "teal": teal,
        "blue": blue,
        "purple": purple,
        "pink": pink,
    }
)

# One canonical lookup spelling per family or shade.
named = MappingProxyType(
    {
        **families,
        **{
            shade.name: shade
            for family in families.values()
            for shade in (
                family.base,
                family.dark,
                family.bright,
                family.light,
                family.pale,
            )
        },
        **{
            f"neutral.{name}": getattr(neutral, name)
            for name in ("ink", "muted", "grid", "paper", "white")
        },
    }
)

__all__ = [
    "Color",
    "ColorFamily",
    "NamedColor",
    "families",
    "named",
    "neutral",
    "fubuki",
    "mio",
    "accent",
    "ina",
    "suisei",
    "red",
    "orange",
    "gold",
    "green",
    "teal",
    "blue",
    "purple",
    "pink",
]
