"""String-compatible named colors and curated shade families."""

from __future__ import annotations


class Color(str):
    """A hex color string with a descriptive name."""

    name: str
    hex: str

    def __new__(cls, name: str, hex: str) -> Color:
        obj = super().__new__(cls, hex)
        obj.name = name
        obj.hex = hex
        return obj


class ColorFamily(Color):
    """A base color usable directly in Matplotlib, with five curated shades.

    Shades are attributes, not methods. ``family`` and ``family.base`` represent
    the same hex value. Light and pale shades are intended for fills rather
    than thin lines on white. Families are not perceptually uniform colormaps.
    """

    base: Color
    dark: Color
    bright: Color
    light: Color
    pale: Color

    def __new__(
        cls, name: str, *, base: str, dark: str, bright: str, light: str, pale: str
    ) -> ColorFamily:
        obj = super().__new__(cls, name, base)
        obj.base = Color(f"{name}.base", base)
        obj.dark = Color(f"{name}.dark", dark)
        obj.bright = Color(f"{name}.bright", bright)
        obj.light = Color(f"{name}.light", light)
        obj.pale = Color(f"{name}.pale", pale)
        return obj
