"""Fixed mappings, Matplotlib normalizations, and shared colorbar placement."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import BoundaryNorm, ListedColormap, LogNorm, Normalize

import reiplotlib as rpl


def test_subsets_and_order_do_not_change_colors_or_bounds():
    scale = rpl.ColorScale(vmin=10, vmax=100)
    values = np.array([10.0, 30.0, 100.0])
    original = values.copy()
    colors = scale(values)
    np.testing.assert_allclose(scale(values[[2, 0]]), colors[[2, 0]])
    np.testing.assert_allclose(scale(30), colors[1])
    np.testing.assert_allclose(scale([30]), colors[1:2])
    np.testing.assert_array_equal(values, original)
    assert (scale.norm.vmin, scale.norm.vmax) == (10, 100)
    assert scale(np.ones((2, 3))).shape == (2, 3, 4)
    assert scale(np.ones((2, 3, 4))).shape == (2, 3, 4, 4)
    assert scale(values, bytes=True).dtype == np.uint8
    assert scale(30, alpha=0.4)[3] == 0.4


def test_log_norm_discrete_bins_and_default_range():
    scale = rpl.ColorScale(norm=LogNorm(1, 100))
    np.testing.assert_allclose(scale(10), scale.cmap(0.5))
    assert rpl.ColorScale().norm.vmin == 0
    assert rpl.ColorScale().norm.vmax == 1
    cmap = ListedColormap(["blue", "orange", "teal"])
    scale = rpl.ColorScale(cmap, norm=BoundaryNorm([0, 1, 2, 3], cmap.N))
    np.testing.assert_allclose(scale([0.5, 1.5, 2.5]), cmap([0, 1, 2]))


def test_bad_under_over_and_clipping_follow_matplotlib():
    cmap = plt.get_cmap("viridis").with_extremes(
        bad="magenta", under="red", over="blue"
    )
    scale = rpl.ColorScale(cmap, vmin=0, vmax=1)
    np.testing.assert_allclose(scale(-1), cmap(-1.0))
    np.testing.assert_allclose(scale(2), cmap(2.0))
    np.testing.assert_allclose(scale(np.nan), cmap(np.ma.masked))
    values = np.ma.array([0.2, 0.5], mask=[False, True])
    np.testing.assert_allclose(scale(values)[1], cmap(np.ma.masked))
    assert values.mask.tolist() == [False, True]
    clipped = rpl.ColorScale(cmap, norm=Normalize(0, 1, clip=True))
    np.testing.assert_allclose(clipped(-1), clipped(0))
    np.testing.assert_allclose(clipped(2), clipped(1))


def test_shared_and_explicit_colorbar_axes_and_export(tmp_path):
    fig, axes = plt.subplots(1, 2, layout="constrained")
    try:
        scale = rpl.ColorScale(norm=LogNorm(1, 100))
        for ax, values in zip(axes, ([1, 10, 100], [100, 1]), strict=True):
            for value in values:
                ax.plot([0, 1], [0, value], color=scale(value))
        cb = scale.colorbar(axes, orientation="horizontal", label="Value")
        assert cb.mappable is scale.mappable
        assert cb.norm is scale.norm
        assert cb.orientation == "horizontal"
        assert cb.ax.get_xlabel() == "Value"
        scale.mappable.set_clim(1, 1000)
        assert cb.norm.vmax == 1000
        rpl.export.savefig(fig, tmp_path / "scale")
        assert (tmp_path / "scale.png").stat().st_size > 0
        assert (tmp_path / "scale.pdf").stat().st_size > 0
    finally:
        plt.close(fig)
    fig, (ax, cax) = plt.subplots(1, 2)
    try:
        scale = rpl.ColorScale(vmin=0, vmax=2)
        assert scale.colorbar(cax=cax).ax is cax
    finally:
        plt.close(fig)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"norm": Normalize()},
        {"norm": LogNorm(vmin=1)},
        {"norm": Normalize(0, 1), "vmin": 0},
        {"vmin": 2, "vmax": 1},
        {"vmin": 1, "vmax": 1},
        {"vmin": np.nan},
        {"vmax": np.inf},
    ],
)
def test_invalid_or_incomplete_ranges_fail(kwargs):
    with pytest.raises(ValueError):
        rpl.ColorScale(**kwargs)


def test_colorbar_requires_axes_from_one_figure():
    scale = rpl.ColorScale()
    with pytest.raises(ValueError, match="ax or cax"):
        scale.colorbar()
    with pytest.raises(TypeError):
        rpl.ColorScale(norm="log")
    fig, ax = plt.subplots()
    other, other_ax = plt.subplots()
    try:
        with pytest.raises(ValueError, match="same figure"):
            scale.colorbar([ax, other_ax])
        with pytest.raises(ValueError, match="same figure"):
            scale.colorbar(ax, cax=other_ax)
        with pytest.raises(TypeError, match="axes"):
            scale.colorbar("axes")
    finally:
        plt.close(fig)
        plt.close(other)


@pytest.mark.parametrize("orientation", ["horizontal", "vertical"])
def test_default_colorbars_are_slim_in_both_orientations(orientation):
    fig, ax = plt.subplots(figsize=(5, 4), layout="constrained")
    try:
        cb = rpl.ColorScale().colorbar(ax, orientation=orientation)
        fig.canvas.draw()
        box = cb.ax.get_window_extent()
        ratio = (
            box.width / box.height
            if orientation == "horizontal"
            else box.height / box.width
        )
        assert ratio == pytest.approx(50, rel=0.01)
        cb.remove()
        cb = rpl.ColorScale().colorbar(
            ax, orientation=orientation, aspect=20, fraction=0.15, pad=0.1
        )
        fig.canvas.draw()
        box = cb.ax.get_window_extent()
        ratio = (
            box.width / box.height
            if orientation == "horizontal"
            else box.height / box.width
        )
        assert ratio == pytest.approx(20, rel=0.01)
    finally:
        plt.close(fig)


def test_explicit_cax_keeps_caller_geometry():
    fig = plt.figure(figsize=(5, 4))
    cax = fig.add_axes([0.2, 0.2, 0.4, 0.1])
    try:
        before = cax.get_position().bounds
        rpl.ColorScale().colorbar(cax=cax, orientation="horizontal")
        fig.canvas.draw()
        np.testing.assert_allclose(cax.get_position().bounds, before)
        assert rpl.options.colorbar(aspect=25, pad=0.1) == {
            "aspect": 25,
            "fraction": 0.035,
            "pad": 0.1,
        }
    finally:
        plt.close(fig)
