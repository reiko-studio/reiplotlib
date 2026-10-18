"""Shared legend collection, duplicate policies, and independent groups."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.lines import Line2D

import reiplotlib as rpl


def test_collect_nested_axes_order_subset_and_missing_labels():
    fig, axes = plt.subplots(2, 2)
    try:
        (a,) = axes[0, 0].plot([0, 1], [1, 2], color="blue", label="A")
        axes[0, 1].plot([0, 1], [3, 4], color="blue", label="A")
        (b,) = axes[1, 0].plot([0, 1], [1, 2], label="B")
        axes[1, 1].plot([0, 1], [1, 2], label="_private")
        assert rpl.collect_legend(axes) == {"A": a, "B": b}
        assert list(rpl.collect_legend(axes, order=["B"])) == ["B", "A"]
        assert rpl.collect_legend(axes, include=["B"]) == {"B": b}
        assert rpl.collect_legend(axes[0, 0]) == {"A": a}
        with pytest.raises(KeyError, match="Unknown"):
            rpl.collect_legend(axes, order=["missing"])
        with pytest.raises(ValueError, match="excluded"):
            rpl.collect_legend(axes, include=["A"], order=["B"])
        with pytest.raises(ValueError, match="repeated"):
            rpl.collect_legend(axes, include=["A", "A"])
    finally:
        plt.close(fig)


@pytest.mark.parametrize("kind", ["line", "errorbar", "scatter", "patch"])
def test_duplicates_compare_styles_but_not_data(kind):
    fig, axes = plt.subplots(1, 2)
    handles = []
    try:
        for i, ax in enumerate(axes):
            if kind == "line":
                (handle,) = ax.plot([0, 1], [i, i + 1], color="blue", label="A")
            elif kind == "errorbar":
                handle = rpl.errorbar(
                    ax,
                    [0, 1],
                    [i, i + 1],
                    yerr=[0.01, 0.5],
                    color="blue",
                    marker="o",
                    capsize=3,
                    label="A",
                )
            elif kind == "scatter":
                handle = ax.scatter([0, 1], [i, i + 1], color="blue", label="A")
            else:
                handle = ax.bar([0], [i + 1], color="blue", label="A")[0]
            handles.append(handle)
        # Matplotlib labels a bar container rather than its patch; use patches
        # directly to exercise their public legend representation.
        if kind == "patch":
            for ax, handle in zip(axes, handles, strict=True):
                ax.containers[0].set_label("_bars")
                handle.set_label("A")
        assert rpl.collect_legend(axes)["A"] is handles[0]
        if kind == "errorbar":
            handles[1].lines[0].set_marker("s")
        elif kind == "scatter" or kind == "patch":
            handles[1].set_facecolor("red")
        else:
            handles[1].set_color("red")
        with pytest.raises(ValueError, match="Conflicting"):
            rpl.collect_legend(axes)
        assert rpl.collect_legend(axes, duplicates="first")["A"] is handles[0]
        assert rpl.collect_legend(axes, duplicates="last")["A"] is handles[1]
        with pytest.raises(ValueError, match="Repeated"):
            rpl.collect_legend(axes, duplicates="error")
    finally:
        plt.close(fig)


def test_groups_replace_without_touching_other_legends_and_export(tmp_path):
    with rpl.rc_context({"text.usetex": False}):
        fig, axes = plt.subplots(1, 2, layout="constrained")
        try:
            axes[0].plot([0, 1], [1, 2], label="Reference", color="black")
            error = rpl.errorbar(
                axes[1], [0, 1], [2, 3], yerr=0.2, color="blue", label="Model"
            )
            manual = fig.legend(handles=[Line2D([], [], label="Manual")])
            first = rpl.figure_legend(fig, axes, include=["Reference"], group="refs")
            models = rpl.figure_legend(
                fig, include=["Model"], group="models", loc="outside lower center"
            )
            second = rpl.figure_legend(fig, include=["Reference"], group="refs")
            assert first not in fig.legends
            assert set(fig.legends) == {manual, models, second}
            assert [t.get_text() for t in models.get_texts()] == ["Model"]
            assert rpl.collect_legend(axes)["Model"] is error
            rpl.export.savefig(fig, tmp_path / "legends")
            assert (tmp_path / "legends.png").stat().st_size > 0
            assert (tmp_path / "legends.pdf").stat().st_size > 0
            assert rpl.figure_legend(fig, include=[], group="refs") is None
            assert set(fig.legends) == {manual, models}
        finally:
            plt.close(fig)


def test_explicit_proxy_entries_and_failed_update_preserves_legend():
    fig, ax = plt.subplots()
    try:
        proxy = rpl.SeriesStyle(color="blue", label="Model").legend_handle()
        legend = rpl.figure_legend(fig, entries={"Display label": proxy})
        assert [text.get_text() for text in legend.get_texts()] == ["Display label"]
        with pytest.raises(KeyError):
            rpl.figure_legend(fig, entries={"Display label": proxy}, order=["bad"])
        assert fig.legends == [legend]
        with pytest.raises(ValueError, match="not both"):
            rpl.figure_legend(fig, ax, entries={"Display label": proxy})
        assert rpl.collect_legend(np.array([[ax]])) == {}
        with pytest.raises(ValueError, match="duplicates"):
            rpl.collect_legend(ax, duplicates="unknown")
        with pytest.raises(TypeError):
            rpl.collect_legend("axes")
    finally:
        plt.close(fig)


def test_distinct_custom_dash_sequences_are_not_silently_merged():
    fig, axes = plt.subplots(1, 2)
    try:
        for ax, pattern in zip(axes, ((2, 2), (6, 2)), strict=True):
            ax.plot([0, 1], [0, 1], color="blue", linestyle=(0, pattern), label="A")
        with pytest.raises(ValueError, match="Conflicting"):
            rpl.collect_legend(axes)
    finally:
        plt.close(fig)


def test_shared_axes_legend_collects_grid_and_replaces_only_destination(tmp_path):
    with rpl.rc_context({"text.usetex": False}):
        fig, axes = plt.subplots(3, 2, layout="constrained")
        try:
            for ax in axes.flat:
                ax.plot([0, 1], [0, 1], color="blue", label="Method")
            axes[2, 1].plot([0, 1], [1, 0], color="black", label="Reference")
            other = axes[2, 1].legend()
            figure = rpl.figure_legend(fig)
            target = axes[0, 0]
            first = rpl.axes_legend(target, axes, order=["Reference"])
            assert target.get_legend() is first
            assert [t.get_text() for t in first.get_texts()] == ["Reference", "Method"]
            second = rpl.axes_legend(target, include=["Method"], loc="lower left")
            assert target.get_legend() is second
            assert first not in target.get_children()
            assert axes[2, 1].get_legend() is other
            assert fig.legends == [figure]
            rpl.export.savefig(fig, tmp_path / "panel-legend")
            assert (tmp_path / "panel-legend.pdf").stat().st_size > 0
            assert rpl.axes_legend(target, include=[]) is None
            assert target.get_legend() is None
            assert axes[2, 1].get_legend() is other
        finally:
            plt.close(fig)


def test_axes_legend_supports_proxy_entries_and_preserves_legend_on_failure():
    fig, ax = plt.subplots()
    try:
        proxy = Line2D([], [], color="blue")
        previous = rpl.axes_legend(ax, entries={"Method": proxy})
        with pytest.raises(KeyError):
            rpl.axes_legend(ax, include=["missing"])
        assert ax.get_legend() is previous
        with pytest.raises(ValueError, match="not both"):
            rpl.axes_legend(ax, [ax], entries={"Method": proxy})
        with pytest.raises(TypeError, match="entries"):
            rpl.axes_legend(ax, handles=[proxy])
    finally:
        plt.close(fig)
