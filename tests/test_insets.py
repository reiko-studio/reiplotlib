"""Rendered inset backgrounds follow labels without callbacks or data changes."""

import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.patches import Rectangle

import reiplotlib as rpl


@pytest.fixture
def figure():
    with rpl.rc_context({"text.usetex": False}):
        fig, ax = plt.subplots(figsize=(5, 3), layout="constrained")
        yield fig, ax
        plt.close(fig)


def assert_bounds(fig, inset, backing, pad):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    expected = inset.get_tightbbox(renderer).padded(renderer.points_to_pixels(pad))
    np.testing.assert_allclose(
        backing.get_window_extent(renderer).extents, expected.extents, atol=1e-7
    )
    return expected


def test_geometry_follows_fonts_labels_placement_and_resize(figure):
    fig, ax = figure
    ax.plot([0, 1], [0, 1])
    limits = (ax.get_xlim(), ax.get_ylim())
    inset = ax.inset_axes([0.5, 0.45, 0.4, 0.4])
    inset.plot([0, 1], [0, 1])
    inset.set(xlabel="x", ylabel="y", title="Detail")
    rpl.style_inset(inset)
    facecolor = inset.get_facecolor()
    callbacks = dict(fig.canvas.callbacks.callbacks)
    backing = rpl.inset_backing(inset, pad=4)
    assert isinstance(backing, Rectangle)
    before = assert_bounds(fig, inset, backing, 4)
    inset.set_ylabel("A longer label", fontsize=14)
    inset.set_xlabel("A much wider x label", fontsize=12)
    inset.set_title("Changed title", fontsize=13)
    fig.set_size_inches(7, 4)
    after = assert_bounds(fig, inset, backing, 4)
    assert not np.allclose(before.extents, after.extents)
    inset.set_axes_locator(None)
    inset.set_position([0.3, 0.5, 0.25, 0.3])
    assert_bounds(fig, inset, backing, 4)
    assert inset.get_facecolor() == facecolor
    assert (ax.get_xlim(), ax.get_ylim()) == limits
    assert fig.canvas.callbacks.callbacks == callbacks


def test_backing_draws_below_inset_and_above_parent(figure):
    fig, ax = figure
    ax.set_facecolor("blue")
    inset = ax.inset_axes([0.4, 0.4, 0.4, 0.4])
    inset.set_facecolor("white")
    inset.set(xlabel="X", ylabel="Y")
    backing = rpl.inset_backing(inset, pad=8, facecolor="red", alpha=1)
    bounds = assert_bounds(fig, inset, backing, 8)
    pixels = np.asarray(fig.canvas.buffer_rgba())

    def pixel(x, y):
        return pixels[pixels.shape[0] - 1 - round(y), round(x), :3]

    np.testing.assert_array_equal(pixel(bounds.x0 + 2, bounds.y0 + 2), [255, 0, 0])
    center = inset.bbox.get_points().mean(axis=0)
    np.testing.assert_array_equal(pixel(*center), [255, 255, 255])


def test_replacement_visibility_and_removal(figure):
    fig, ax = figure
    inset = ax.inset_axes([0.5, 0.5, 0.3, 0.3])
    first = rpl.inset_backing(inset)
    second = rpl.inset_backing(inset)
    assert first not in ax.get_children()
    assert second in ax.get_children()
    assert_bounds(fig, inset, second, 3)
    inset.set_visible(False)
    assert second.get_window_extent(fig.canvas.get_renderer()).width == 0
    inset.set_visible(True)
    assert_bounds(fig, inset, second, 3)
    inset.remove()
    fig.canvas.draw()
    assert second.get_window_extent(fig.canvas.get_renderer()).width == 0
    second.remove()
    assert second not in ax.get_children()


@pytest.mark.parametrize("fmt", ["png", "pdf", "svg"])
def test_export_uses_current_renderer_and_does_not_add_artists(
    figure, fmt, monkeypatch
):
    fig, ax = figure
    inset = ax.inset_axes([0.55, 0.55, 0.35, 0.3])
    inset.set(
        xscale="log",
        yscale="log",
        xlim=(1, 100),
        ylim=(100, 1),
        xlabel="Log x",
        ylabel="Inverted log y",
    )
    rpl.style_inset(inset)
    backing = rpl.inset_backing(inset, pad=5)
    children = len(ax.get_children())
    draw = backing.draw
    renderer_units = []

    def check_draw(renderer):
        draw(renderer)
        expected = inset.get_tightbbox(renderer).padded(renderer.points_to_pixels(5))
        np.testing.assert_allclose(
            backing.get_window_extent(renderer).extents, expected.extents, atol=1e-7
        )
        renderer_units.append(renderer.points_to_pixels(1))

    monkeypatch.setattr(backing, "draw", check_draw)
    for dpi in (100, 250):
        stream = io.BytesIO()
        fig.savefig(stream, format=fmt, dpi=dpi, bbox_inches="tight")
        assert stream.tell() > 1000
        assert len(ax.get_children()) == children
        assert_bounds(fig, inset, backing, 5)
    assert renderer_units


def test_figure_level_and_nested_insets(figure):
    fig, ax = figure
    outer = ax.inset_axes([0.4, 0.4, 0.5, 0.5])
    inner = outer.inset_axes([0.5, 0.5, 0.3, 0.3])
    nested = rpl.inset_backing(inner)
    assert nested in outer.get_children()
    assert_bounds(fig, inner, nested, 3)
    standalone = fig.add_axes([0.1, 0.7, 0.2, 0.2], zorder=6)
    backing = rpl.inset_backing(standalone)
    assert backing in fig.artists
    assert_bounds(fig, standalone, backing, 3)


def test_styling_preserves_limits_facecolor_and_spines(figure):
    fig, ax = figure
    inset = ax.inset_axes([0.4, 0.4, 0.4, 0.4])
    inset.set(xlim=(10, 1), ylim=(-2, 3), facecolor="none")
    inset.spines["top"].set_visible(False)
    assert rpl.style_inset(inset, labelsize=9, ticksize=6) is inset
    assert inset.get_xlim() == (10, 1)
    assert inset.get_ylim() == (-2, 3)
    assert inset.get_facecolor()[-1] == 0
    assert not inset.spines["top"].get_visible()
    assert inset.xaxis.label.get_fontsize() == 9
    assert inset.yaxis.get_offset_text().get_fontsize() == 6
    fig.canvas.draw()
    assert all(label.get_fontsize() == 6 for label in inset.get_xticklabels())


@pytest.mark.parametrize("pad", [-1, np.inf, np.nan])
def test_invalid_pad_leaves_no_backing(figure, pad):
    _, ax = figure
    inset = ax.inset_axes([0.5, 0.5, 0.3, 0.3])
    count = len(ax.get_children())
    with pytest.raises(ValueError, match="pad"):
        rpl.inset_backing(inset, pad=pad)
    assert len(ax.get_children()) == count
