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
