import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

import reiplotlib as rpl


@pytest.fixture
def axes():
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.set(xlim=(-1, 3), ylim=(0, 1))
    yield fig, ax
    plt.close(fig)


def test_partial_errors_and_caps(axes):
    fig, ax = axes
    result = rpl.errorbar(
        ax,
        [0, 1, 2],
        [0.5] * 3,
        yerr=[0.0001, 0.2, 0.0002],
        fmt="o-",
        markersize=8,
        capsize=3,
    )
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1
    assert all(len(cap.get_xdata()) == 1 for cap in result.lines[1])
    assert len(result.lines[0].get_xdata()) == 3
    assert result in ax.containers


def test_hidden_errors_reappear_after_zoom(axes):
    fig, ax = axes
    result = rpl.errorbar(
        ax, [0, 1], [0.5, 0.5], yerr=[0.0001, 0.2], fmt="o", markersize=8, capsize=3
    )
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1
    ax.set_ylim(0.4995, 0.5005)
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 2
    ax.set_ylim(0, 1)
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1


def test_resize_changes_visibility(axes):
    fig, ax = axes
    result = rpl.errorbar(ax, [0], [0.5], yerr=[0.02], fmt="o", markersize=12)
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 0
    fig.set_size_inches(4, 12)
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1


def test_dpi_does_not_change_threshold(axes):
    fig, ax = axes
    result = rpl.errorbar(ax, [0, 1], [0.5, 0.5], yerr=[0.001, 0.1], fmt="o")
    fig.canvas.draw()
    count = len(result.lines[2][0].get_segments())
    fig.set_dpi(300)
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == count


def test_first_save_updates_before_render(axes):
    fig, ax = axes
    result = rpl.errorbar(
        ax, [0, 1], [0.5, 0.5], yerr=[0.0001, 0.2], fmt="o", capsize=3
    )
    fig.savefig(io.BytesIO(), format="png", dpi=300)
    assert len(result.lines[2][0].get_segments()) == 1
    fig.savefig(io.BytesIO(), format="pdf")
    assert len(result.lines[2][0].get_segments()) == 1


def test_log_and_inverted_axis(axes):
    fig, ax = axes
    ax.set_yscale("log")
    ax.set_ylim(0.5, 200)
    result = rpl.errorbar(
        ax, [0, 1], [1, 100], yerr=[0.2, 0.2], fmt="o", markersize=5, capsize=2
    )
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1
    ax.invert_yaxis()
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1


def test_asymmetric_errors(axes):
    fig, ax = axes
    result = rpl.errorbar(
        ax, [0, 1], [0.5, 0.5], yerr=[[0.0001, 0.01], [0.0002, 0.2]], fmt="o"
    )
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1
    np.testing.assert_allclose(result.lines[2][0].get_segments()[0][:, 1], [0.49, 0.7])


def test_horizontal_and_vertical_independent(axes):
    fig, ax = axes
    result = rpl.errorbar(
        ax,
        [0, 1],
        [0.5, 0.5],
        xerr=[0.4, 0.0001],
        yerr=[0.0001, 0.2],
        fmt="o",
        capsize=3,
    )
    fig.canvas.draw()
    assert [len(c.get_segments()) for c in result.lines[2]] == [1, 1]
    for cap in result.lines[1]:
        assert len(cap.get_xdata()) == 1


def test_errorevery_and_nan(axes):
    fig, ax = axes
    result = rpl.errorbar(
        ax,
        [0, 1, 2],
        [0.5, np.nan, 0.5],
        yerr=[0.0001, 0.2, 0.2],
        fmt="o",
        errorevery=2,
        capsize=3,
    )
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1
    assert all(len(cap.get_xdata()) == 1 for cap in result.lines[1])


def test_no_marker_does_not_hide_nonzero_errors(axes):
    fig, ax = axes
    result = rpl.errorbar(ax, [0], [0.5], yerr=[0.0001], fmt="-")
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1


def test_opt_out_preserves_all_errors_and_limits(axes):
    fig, ax = axes
    result = rpl.errorbar(
        ax,
        [0, 1],
        [0.5, 0.5],
        yerr=[0.0001, 0.2],
        hide_small_errors=False,
        fmt="o",
        uplims=[False, True],
    )
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 2


def test_autoscale_retains_original_errors():
    fig, ax = plt.subplots()
    try:
        rpl.errorbar(ax, [0], [0], yerr=[2], fmt="o", markersize=500)
        fig.canvas.draw()
        np.testing.assert_allclose(ax.dataLim.intervaly, [-2, 2])
    finally:
        plt.close(fig)


def test_remove_cleans_up_controller(axes):
    fig, ax = axes
    result = rpl.errorbar(ax, [0], [0.5], yerr=[0.01], fmt="o")
    assert len(ax.artists) == 1
    result.remove()
    assert not ax.artists and not ax.containers and not ax.collections
    fig.canvas.draw()


def test_invalid_threshold_and_limit_arrows(axes):
    _, ax = axes
    with pytest.raises(ValueError, match="nonnegative"):
        rpl.errorbar(ax, [0], [0.5], yerr=[0.1], min_error_size=-1)
    with pytest.raises(ValueError, match="limit arrows"):
        rpl.errorbar(ax, [0], [0.5], yerr=[0.1], uplims=True)
    assert not ax.collections


def test_per_point_colors_remain_aligned(axes):
    fig, ax = axes
    result = rpl.errorbar(
        ax,
        [0, 1, 2],
        [0.5] * 3,
        yerr=[0.0001, 0.2, 0.0002],
        fmt="o",
        ecolor=["red", "green", "blue"],
    )
    fig.canvas.draw()
    colors = result.lines[2][0].get_edgecolors()
    np.testing.assert_allclose(colors, [matplotlib.colors.to_rgba("green")])
    ax.set_ylim(0.4995, 0.5005)
    fig.canvas.draw()
    assert len(result.lines[2][0].get_edgecolors()) == 3


def test_custom_marker_and_edge_color(axes):
    fig, ax = axes
    marker = np.array([[-0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]])
    result = rpl.errorbar(
        ax,
        [0, 1],
        [0.5, 0.5],
        yerr=[0.0001, 0.2],
        marker=marker,
        markeredgecolor=np.array([1.0, 0.0, 0.0, 1.0]),
    )
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1


def test_legend_and_no_data_line(axes):
    fig, ax = axes
    result = rpl.errorbar(ax, [0], [0.5], yerr=[0.0001], fmt="none", label="data")
    ax.legend()
    fig.canvas.draw()
    assert len(result.lines[2][0].get_segments()) == 1
