"""Check shade families against Matplotlib's actual color consumers."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import to_rgba

import reiplotlib as rpl
from reiplotlib import colors as c
from reiplotlib import palettes as p


@pytest.mark.parametrize("family", c.families.values(), ids=c.families.keys())
def test_family_renders_as_base_with_distinct_shades(family):
    assert isinstance(family, str)
    assert to_rgba(family) == to_rgba(family.base)
    shades = [family.dark, family.base, family.bright, family.light, family.pale]
    assert len(set(shades)) == 5
    for shade in shades:
        assert c.named[shade.name] is shade

    fig, ax = plt.subplots()
    try:
        (line,) = ax.plot([0, 1], [0, 1], color=family)
        ax.scatter([0.5], [0.5], color=family.bright)
        band = ax.fill_between([0, 1], [0, 0], [1, 1], color=family.pale)
        ax.text(0, 1, "label", color=family.dark)
        fig.canvas.draw()
        assert to_rgba(line.get_color()) == to_rgba(family.base)
        np.testing.assert_allclose(band.get_facecolor()[0], to_rgba(family.pale))
    finally:
        plt.close(fig)


def test_palette_accessors_share_one_registry_and_default():
    for name, palette in p.named.items():
        assert p.get(name) is palette
        assert rpl.palette(name) is palette
        assert getattr(p, name) is palette
        assert list(p.cycle(name)) == [{"color": color} for color in palette]
    assert p.get() is p.grove
    assert list(rpl.cycle()) == list(p.cycle("grove"))
    with pytest.raises(TypeError):
        p.named["new"] = ()


def test_removed_basic_names_are_not_exposed():
    assert not hasattr(c, "basic")
    assert not hasattr(p, "basic")
    with pytest.raises(KeyError):
        p.get("basic")


@pytest.mark.parametrize("hex", ["#467A9B", "#abc", "#000000", "#FFFFFF"])
def test_generated_color_is_valid_and_mutable_without_cached_base(hex):
    color = rpl.NamedColor(hex)
    np.testing.assert_allclose(to_rgba(color), to_rgba(hex))
    for shade in ("dark", "base", "bright", "light", "pale"):
        assert len(getattr(color, shade)) == 7
        assert to_rgba(getattr(color, shade))[3] == 1
    color.dark = "#123"
    assert color.dark == "#112233"
    assert to_rgba(color) == to_rgba(hex)
    color.base = "#B64F7C"
    assert color.dark != "#112233"
    assert color.hex == "#B64F7C"
    assert to_rgba(color) == to_rgba("#B64F7C")


@pytest.mark.parametrize("bad", ["red", "123456", "#12", "#GGGGGG", "#12345678", None])
def test_generated_color_rejects_invalid_hex_without_partial_mutation(bad):
    with pytest.raises(ValueError):
        rpl.NamedColor(bad)
    color = rpl.NamedColor("#467A9B")
    before = (color.base, color.dark, color.light)
    with pytest.raises(ValueError):
        color.base = bad
    with pytest.raises(ValueError):
        color.dark = bad
    assert (color.base, color.dark, color.light) == before


def test_generated_color_renders_and_artist_can_be_updated(tmp_path):
    color = c.NamedColor("#467A9B")
    fig, ax = plt.subplots()
    try:
        (line,) = ax.plot([0, 1], [0, 1], color=color)
        ax.scatter([0.5], [0.5], color=color.bright)
        ax.fill_between([0, 1], [0, 0], [1, 1], color=color.pale)
        fig.canvas.draw()
        color.base = "#B64F7C"
        line.set_color(color.base)
        fig.canvas.draw()
        assert to_rgba(line.get_color()) == to_rgba(color.base)
        rpl.export.savefig(fig, tmp_path / "custom")
        assert (tmp_path / "custom.png").stat().st_size > 0
        assert (tmp_path / "custom.pdf").stat().st_size > 0
    finally:
        plt.close(fig)
