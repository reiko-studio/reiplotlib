"""Presets leave automatic color selection to the axes."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from matplotlib.colors import to_rgba

import reiplotlib as rpl
from reiplotlib import options as o


@pytest.mark.parametrize(
    "kind", ["line", "markers", "markerline", "scatter", "errorbar", "fill", "hist"]
)
def test_presets_follow_custom_axes_cycle(kind):
    preset = getattr(o, kind)
    assert "color" not in preset()
    assert "color" not in preset(None)
    assert preset("#123456")["color"] == "#123456"
    fig, ax = plt.subplots()
    try:
        rpl.use_palette(ax, ("#123456", "#ABCDEF"))
        for expected in ("#123456", "#ABCDEF", "#123456"):
            if kind in ("line", "markers", "markerline"):
                (artist,) = ax.plot([0, 1], [0, 1], **preset())
                actual = to_rgba(artist.get_color())
            elif kind == "errorbar":
                artist = rpl.errorbar(ax, [0, 1], [0, 1], yerr=0.1, **preset())
                actual = to_rgba(artist.lines[0].get_color())
            elif kind == "scatter":
                artist = ax.scatter([0, 1], [0, 1], **preset())
                actual = artist.get_facecolor()[0]
            elif kind == "fill":
                artist = ax.fill_between([0, 1], [0, 0], [1, 1], **preset())
                actual = artist.get_facecolor()[0]
            else:
                _, _, patches = ax.hist([0, 0.5, 1], **preset())
                actual = patches[0].get_facecolor()
            assert tuple(actual[:3]) == to_rgba(expected)[:3]
        fig.canvas.draw()
    finally:
        plt.close(fig)
