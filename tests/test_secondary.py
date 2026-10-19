"""Secondary coordinates retain ticks, labels and parent limits on redraw."""

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes._secondary_axes import SecondaryAxis

import reiplotlib as rpl


@pytest.mark.parametrize("orientation", ["x", "y"])
def test_ticks_follow_zoom_inversion_and_scale(orientation):
    with rpl.rc_context({"text.usetex": False}):
        fig, ax = plt.subplots()
        set_limits = getattr(ax, f"set_{orientation}lim")
        get_limits = getattr(ax, f"get_{orientation}lim")
        set_limits(1, 4)
        helper = getattr(rpl, f"secondary_{orientation}axis")

        def reciprocal(v):
            with np.errstate(divide="ignore", invalid="ignore"):
                return 10 / v

        secondary = helper(
            ax,
            (reciprocal, reciprocal),
            ticks=[1, 2, 5, 10, 20],
            labels=["a", "b", "c", "d", "e"],
            label="converted",
            labelsize=9,
            ticksize=8,
        )
        assert isinstance(secondary, SecondaryAxis)
        fig.canvas.draw()
        axis = getattr(secondary, f"{orientation}axis")
        np.testing.assert_allclose(axis.get_majorticklocs(), [5, 10])
        assert [t.get_text() for t in axis.get_ticklabels()] == ["c", "d"]
        assert get_limits() == (1, 4)
        set_limits(10, 2)
        getattr(ax, f"set_{orientation}scale")("log")
        fig.canvas.draw()
        np.testing.assert_allclose(axis.get_majorticklocs(), [1, 2, 5])
        assert [t.get_text() for t in axis.get_ticklabels()] == ["a", "b", "c"]
        assert get_limits() == (10, 2)
        fig.set_size_inches(5, 3)
        fig.savefig(io.BytesIO(), format="png")
        fig.savefig(io.BytesIO(), format="pdf")
        secondary.remove()
        assert secondary not in ax.child_axes
        fig.canvas.draw()
        plt.close(fig)


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(labels=["x"]),
        dict(ticks=[np.nan]),
        dict(ticks=[1, 1]),
        dict(ticks=[1], labels=[]),
    ],
)
def test_invalid_ticks_leave_no_child_axis(kwargs):
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        rpl.secondary_yaxis(ax, (lambda v: v, lambda v: v), **kwargs)
    assert not ax.child_axes
    plt.close(fig)


def test_automatic_ticks_and_native_customization():
    with rpl.rc_context({"text.usetex": False}):
        fig, ax = plt.subplots()
        ax.set_ylim(0, 100)
        secondary = rpl.secondary_yaxis(ax, (lambda v: v / 100, lambda v: v * 100))
        secondary.set_ylabel("fraction")
        secondary.set_ticks([0, 0.5, 1], labels=["zero", "half", "one"])
        fig.canvas.draw()
        np.testing.assert_allclose(secondary.get_ylim(), [0, 1])
        assert secondary.get_ylabel() == "fraction"
        plt.close(fig)
