"""String-compatible named colors and curated shade families."""

from __future__ import annotations

import colorsys
import re
from collections.abc import Sequence

from matplotlib.colors import to_hex, to_rgb


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


class NamedColor(Sequence[float]):
    """A mutable, Matplotlib-compatible color with automatically generated shades.

    Accepts opaque ``#RGB`` or ``#RRGGBB`` strings. Assigning ``base`` regenerates
    every shade; assigning another shade overrides only that shade. Dark, light,
    and pale mix the base with black/white in sRGB. Bright increases HLS saturation
    and lightness. These simple rules do not guarantee perceptual spacing.

    The object presents its current base as an RGB sequence to Matplotlib. It is
    unhashable so mutable values cannot leave stale entries in its color cache.
    Use a shade attribute when a hex string is required.
    """

    __hash__ = None
    _shades = frozenset(("base", "dark", "bright", "light", "pale"))

    base: Color
    dark: Color
    bright: Color
    light: Color
    pale: Color

    def __init__(self, hex: str):
        self.base = hex

    @staticmethod
    def _normalize(value: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(
            r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value
        ):
            raise ValueError("Expected an opaque hex color: #RGB or #RRGGBB")
        return to_hex(value).upper()

    def __setattr__(self, name, value):
        if name not in self._shades:
            raise AttributeError(f"Unknown color attribute: {name}")
        value = self._normalize(value)
        object.__setattr__(self, name, Color(f"custom.{name}", value))
        if name == "base":
            rgb = to_rgb(value)
            hue, lightness, saturation = colorsys.rgb_to_hls(*rgb)
            generated = {
                "dark": tuple(channel * 0.65 for channel in rgb),
                "light": tuple(channel + (1 - channel) * 0.55 for channel in rgb),
                "pale": tuple(channel + (1 - channel) * 0.85 for channel in rgb),
                "bright": colorsys.hls_to_rgb(
                    hue,
                    lightness + (1 - lightness) * 0.10,
                    saturation + (1 - saturation) * 0.25,
                ),
            }
            for shade, channels in generated.items():
                object.__setattr__(
                    self, shade, Color(f"custom.{shade}", to_hex(channels).upper())
                )

    @property
    def hex(self) -> str:
        """Return the current base hex string."""
        return str(self.base)

    def __len__(self):
        return 3

    def __getitem__(self, index):
        return to_rgb(self.base)[index]

    def __str__(self):
        return str(self.base)

    def __repr__(self):
        return f"NamedColor({str(self.base)!r})"
