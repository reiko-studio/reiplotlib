"""Series identity survives plotting order, subsets, and per-call overrides."""

from dataclasses import FrozenInstanceError

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from matplotlib.colors import to_rgba

import reiplotlib as rpl


def test_reordered_subset_keeps_line_and_errorbar_identity(tmp_path):
    styles = {
        "reference": rpl.SeriesStyle(
            color="#234567",
            label="Reference",
            marker="s",
            linestyle="--",
            markerfacecolor="none",
        ),
        "model": rpl.SeriesStyle(
            color="#AB3456", label="Model", marker="^", linestyle="-."
        ),
    }
    with rpl.rc_context({"text.usetex": False}):
        fig, axes = plt.subplots(1, 2)
        try:
            first = {}
            for key in ("reference", "model"):
                style = styles[key]
                (first[key],) = axes[0].plot([0, 1], [1, 2], **style.line())
            for key in ("model", "reference"):
                style = styles[key]
                errors = rpl.errorbar(
                    axes[1],
                    [0, 1],
                    [1, 2],
                    yerr=[0.01, 0.5],
                    label=style.label,
                    **style.errorbar(),
                )
                line = errors.lines[0]
                assert to_rgba(line.get_color()) == to_rgba(first[key].get_color())
                assert line.get_marker() == first[key].get_marker()
                assert line.get_linestyle() == first[key].get_linestyle()
                assert line.get_markerfacecolor() == first[key].get_markerfacecolor()
            # Drawing a subset later doesn't depend on any prior lookup order.
            axes[1].plot([0, 1], [2, 3], **styles["reference"].line())
            assert axes[1].lines[-1].get_color() == styles["reference"].color
            fig.legend(handles=[s.legend_handle() for s in styles.values()])
            rpl.export.savefig(fig, tmp_path / "series")
            assert (tmp_path / "series.png").stat().st_size > 0
            assert (tmp_path / "series.pdf").stat().st_size > 0
        finally:
            plt.close(fig)


def test_overrides_and_returned_options_do_not_mutate_style():
    style = rpl.SeriesStyle(color="blue", label="Model", markerfacecolor="none")
    original = style.line()
    changed = style.line(color="red", marker="s", markersize=7)
    changed["linestyle"] = ":"
    assert style.line() == original
    assert style.errorbar()["color"] == "blue"
    assert "label" not in style.line()
    assert style.legend_handle().get_label() == "Model"
    assert style.legend_handle(label="Alternate").get_label() == "Alternate"
    assert style.label == "Model"
    with pytest.raises(FrozenInstanceError):
        style.color = "red"
    with pytest.raises(KeyError):
        {"model": style}["unknown"]


def test_style_can_disable_markers_and_override_errorbar_options():
    style = rpl.SeriesStyle(color=rpl.colors.teal, marker=None)
    assert style.line()["marker"] is None
    assert style.legend_handle().get_marker() == "None"
    options = style.errorbar(capsize=6, linestyle="none")
    assert options["capsize"] == 6
    assert options["linestyle"] == "none"
    assert style.errorbar()["linestyle"] == "-"
