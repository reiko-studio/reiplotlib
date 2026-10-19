import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.patches import Rectangle

import reiplotlib as rpl


def test_offscreen_outlier_and_crossing():
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2, 20], [1, 2, 3, 15])
    ax.set_xlim(0, 1.5)
    rpl.autoscale_y(ax, margin=0)
    assert np.allclose(ax.get_ylim(), (1, 2.5))
    plt.close(fig)


def test_shared_errors_manual_and_watch():
    fig, axes = plt.subplots(1, 2, sharey=True)
    axes[0].errorbar([1, 20], [2, 50], yerr=[0.5, 3], fmt="none")
    axes[1].scatter([1, 20], [4, 60])
    for ax in axes:
        ax.set_xlim(0, 2)
    rpl.autoscale_y(axes[0], margin=0, watch=True)
    assert np.allclose(axes[0].get_ylim(), (1.5, 4))
    axes[1].set_xlim(19, 21)
    assert np.allclose(axes[0].get_ylim(), (1.5, 60))
    axes[0].set_ylim(0, 10)
    axes[1].set_xlim(0, 2)
    rpl.autoscale_y(axes[0])
    assert axes[0].get_ylim() == (0, 10)
    plt.close(fig)


def test_log_clipping_and_vertical_guide():
    fig, ax = plt.subplots()
    ax.set(xscale="log", yscale="log", xlim=(1, 10))
    ax.plot([1, 100], [1, 100])
    ax.axvline(3)
    rpl.autoscale_y(ax, margin=0)
    assert np.allclose(ax.get_ylim(), (1, 10))
    plt.close(fig)


def test_adaptive_errorbars_preserve_original_extents():
    fig, ax = plt.subplots()
    rpl.errorbar(ax, [1, 20], [2, 50], yerr=[0.01, 30], min_error_size=100, fmt="o")
    ax.set_xlim(0, 2)
    fig.canvas.draw()
    rpl.autoscale_y(ax, margin=0)
    assert np.allclose(ax.get_ylim(), (1.99, 2.01))
    plt.close(fig)


@pytest.mark.parametrize(
    "bounds, expected",
    [
        ({"bottom": 0}, (0, 4.4)),
        ({"top": 10}, (1.2, 10)),
        ({"bottom": 0, "top": 10}, (0, 10)),
    ],
)
def test_partial_bounds_pad_only_free_side(bounds, expected):
    fig, ax = plt.subplots()
    try:
        ax.plot([0, 1], [2, 4])
        rpl.autoscale_y(ax, margin=0.1, **bounds)
        np.testing.assert_allclose(ax.get_ylim(), expected)
    finally:
        plt.close(fig)


def test_band_edges_are_clipped_even_without_visible_vertices():
    fig, ax = plt.subplots()
    try:
        x = np.array([0.0, 4.0])
        low, high = np.array([2.0, 6.0]), np.array([4.0, 12.0])
        band = ax.fill_between(x, low, high)
        original = band.get_paths()[0].vertices.copy()
        ax.set_xlim(1, 3)
        rpl.autoscale_y(ax, margin=0)
        np.testing.assert_allclose(ax.get_ylim(), (3, 10))
        np.testing.assert_array_equal(band.get_paths()[0].vertices, original)
        band.set_visible(False)
        before = ax.get_ylim()
        rpl.autoscale_y(ax, bottom=0)
        assert ax.get_ylim() == before
    finally:
        plt.close(fig)


def test_masked_gap_is_not_bridged_and_patches_do_not_count():
    fig, ax = plt.subplots()
    try:
        values = np.ma.array([1, 2, 30, 40, 50], mask=[0, 0, 1, 0, 0])
        ax.fill_between(np.arange(5), values, values + 2)
        ax.add_patch(Rectangle((0, -100), 5, 500))
        ax.set_xlim(1.5, 2.5)
        before = ax.get_ylim()
        rpl.autoscale_y(ax, margin=0)
        assert ax.get_ylim() == before
        ax.set_xlim(0, 1)
        rpl.autoscale_y(ax, margin=0)
        np.testing.assert_allclose(ax.get_ylim(), (1, 4))
    finally:
        plt.close(fig)


def test_shared_shaded_bands_with_fixed_bound_watch_and_disconnect():
    fig, axes = plt.subplots(1, 2, sharey=True)
    try:
        for ax, y in zip(axes, ([2, 20], [4, 40]), strict=True):
            rpl.shade(ax, [1, 10], y, 0.5)
            ax.set_xlim(0, 2)
        callbacks = rpl.autoscale_y(axes[0], bottom=0, margin=0, watch=True)
        # At x=2 the second upper band boundary reaches 8.5.
        np.testing.assert_allclose(axes[0].get_ylim(), (0, 8.5))
        axes[1].set_xlim(9, 11)
        np.testing.assert_allclose(axes[0].get_ylim(), (0, 40.5))
        for ax, callback in callbacks:
            ax.callbacks.disconnect(callback)
        axes[1].set_xlim(0, 2)
        np.testing.assert_allclose(axes[0].get_ylim(), (0, 40.5))
    finally:
        plt.close(fig)


def test_manual_limits_inversion_and_log_band_clipping():
    fig, ax = plt.subplots()
    try:
        ax.fill_between([1, 100], [1, 100], [10, 1000])
        ax.set(xscale="log", yscale="log", xlim=(1, 10))
        ax.set_ylim(500, 0.1)
        rpl.autoscale_y(ax, bottom=0.5, margin=0)
        assert ax.get_ylim() == (500, 0.1)
        rpl.autoscale_y(ax, bottom=0.5, margin=0, override=True)
        np.testing.assert_allclose(ax.get_ylim(), (100, 0.5))
    finally:
        plt.close(fig)


def test_nan_bands_and_nonpositive_log_data_do_not_add_fake_extrema():
    fig, ax = plt.subplots()
    try:
        ax.fill_between([0, 1, 2, 3, 4], [1, 2, np.nan, 20, 30], [3, 4, np.nan, 40, 50])
        ax.set_xlim(0, 1)
        rpl.autoscale_y(ax, margin=0)
        np.testing.assert_allclose(ax.get_ylim(), (1, 4))
    finally:
        plt.close(fig)
    fig, ax = plt.subplots()
    try:
        ax.set_yscale("log")
        ax.plot([0, 1, 2], [-5, 2, 4])
        rpl.autoscale_y(ax, margin=0)
        np.testing.assert_allclose(ax.get_ylim(), (2, 4))
    finally:
        plt.close(fig)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"bottom": np.nan},
        {"top": np.inf},
        {"bottom": 4, "top": 2},
        {"bottom": 2, "top": 2},
        {"bottom": 10},
    ],
)
def test_invalid_or_incompatible_bounds_do_not_change_limits(kwargs):
    fig, ax = plt.subplots()
    try:
        ax.plot([0, 1], [1, 2])
        before = ax.get_ylim()
        with pytest.raises(ValueError):
            rpl.autoscale_y(ax, **kwargs)
        assert ax.get_ylim() == before
    finally:
        plt.close(fig)


def test_nonpositive_fixed_log_bound_rejected():
    fig, ax = plt.subplots()
    try:
        ax.set_yscale("log")
        with pytest.raises(ValueError, match="positive"):
            rpl.autoscale_y(ax, bottom=0)
    finally:
        plt.close(fig)
