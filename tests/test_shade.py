"""Uncertainty-band geometry and Matplotlib integration."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import to_rgba

import reiplotlib as rpl


@pytest.mark.parametrize(
    "error, lower, upper",
    [
        (0.5, [1.5, 2.5], [2.5, 3.5]),
        ([0.2, 0.4], [1.8, 2.6], [2.2, 3.4]),
        ([[0.2, 0.4], [0.6, 0.8]], [1.8, 2.6], [2.6, 3.8]),
    ],
)
def test_band_geometry_and_color_cycle(error, lower, upper):
    with rpl.rc_context({"text.usetex": False}):
        fig, ax = plt.subplots()
        try:
            x, y = np.array([0, 1]), np.array([2.0, 3.0])
            original = np.array(error, copy=True)
            (line,) = ax.plot(x, y)
            band = rpl.shade(ax, x, y, error)
            vertices = band.get_paths()[0].vertices
            for i in range(2):
                at_x = vertices[vertices[:, 0] == x[i], 1]
                np.testing.assert_allclose(
                    [at_x.min(), at_x.max()], [lower[i], upper[i]]
                )
            np.testing.assert_array_equal(error, original)
            np.testing.assert_array_equal(y, [2, 3])
            np.testing.assert_allclose(
                band.get_facecolor()[0], to_rgba(line.get_color(), 0.2)
            )
            (next_line,) = ax.plot(x, y)
            assert next_line.get_color() == rpl.palettes.grove[1]
            band.remove()
            assert band not in ax.collections
        finally:
            plt.close(fig)


def test_band_supports_gaps_and_fill_options(tmp_path):
    fig, ax = plt.subplots()
    try:
        x = np.arange(5)
        band = rpl.shade(
            ax,
            x,
            [1, 2, np.nan, 3, 4],
            0.2,
            facecolor="red",
            alpha=0.4,
            step="mid",
            label="interval",
        )
        assert len(band.get_paths()) == 2
        assert band.get_label() == "interval"
        np.testing.assert_allclose(band.get_facecolor()[0], to_rgba("red", 0.4))
        rpl.export.savefig(fig, tmp_path / "band")
        assert (tmp_path / "band.pdf").stat().st_size > 0
    finally:
        plt.close(fig)


@pytest.mark.parametrize("error", [-1, [0.2, -0.1], [[[0.1]]], [[0.1], [0.2], [0.3]]])
def test_invalid_widths_fail_before_adding_artist(error):
    fig, ax = plt.subplots()
    try:
        with pytest.raises(ValueError):
            rpl.shade(ax, [0, 1], [1, 2], error)
        assert not ax.collections
    finally:
        plt.close(fig)
