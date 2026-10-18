"""Render the README palette gallery.

Run with PYTHONPATH=src python scripts/render_palettes.py.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import reiplotlib as rpl
from reiplotlib import palettes as p


def main():
    names = ("paper", "grove", "myth", "contrast", "duo", "tol_bright")
    max_colors = max(len(p.get(name)) for name in names)
    destination = Path(__file__).resolve().parents[1] / "docs/images"
    destination.mkdir(parents=True, exist_ok=True)
    with rpl.rc_context():
        fig, axes = rpl.layouts.subplots(
            len(names),
            1,
            width="double",
            aspect=0.058 * len(names),
            layout="constrained",
        )
        fig.get_layout_engine().set(h_pad=0, w_pad=0.01, hspace=0)
        for name, swatches in zip(names, axes, strict=True):
            palette = p.get(name)
            swatches.text(
                -0.18,
                0.19,
                name.replace("_", r"\_"),
                ha="right",
                va="center",
                fontsize=9,
            )
            for i, color in enumerate(palette):
                swatches.add_patch(Rectangle((i, 0), 0.97, 0.38, color=color))
                swatches.text(
                    i + 0.485,
                    -0.04,
                    str(color).replace("#", r"\#"),
                    ha="center",
                    va="top",
                    fontsize=6,
                    fontfamily="monospace",
                )
            swatches.set(xlim=(-1.25, max_colors), ylim=(-0.23, 0.42))
            swatches.axis("off")

        rpl.export.savefig(fig, destination / "palettes", formats=("png",))
        plt.close(fig)


def render_neutrals():
    names = ("ink", "muted", "grid", "paper", "white")
    destination = Path(__file__).resolve().parents[1] / "docs/images"
    destination.mkdir(parents=True, exist_ok=True)
    with rpl.rc_context():
        fig, ax = rpl.layouts.subplots(
            width="double", aspect=0.12, layout="constrained"
        )
        for i, name in enumerate(names):
            color = getattr(rpl.colors.neutral, name)
            ax.add_patch(
                Rectangle(
                    (i, 0),
                    0.96,
                    0.42,
                    facecolor=color,
                    edgecolor=rpl.colors.neutral.grid,
                    linewidth=0.5,
                )
            )
            ax.text(i + 0.48, -0.05, name, ha="center", va="top", fontsize=9)
            ax.text(
                i + 0.48,
                -0.23,
                str(color).replace("#", r"\#"),
                ha="center",
                va="top",
                fontsize=7,
                fontfamily="monospace",
            )
        ax.set(xlim=(-0.04, len(names)), ylim=(-0.40, 0.45))
        ax.axis("off")
        rpl.export.savefig(fig, destination / "neutrals", formats=("png",))
        plt.close(fig)


def render_families():
    shades = ("dark", "base", "bright", "light", "pale")
    destination = Path(__file__).resolve().parents[1] / "docs/images"
    destination.mkdir(parents=True, exist_ok=True)
    with rpl.rc_context():
        fig, ax = rpl.layouts.subplots(
            width="double", aspect=0.55, layout="constrained"
        )
        for column, shade in enumerate(shades):
            ax.text(column + 0.48, 0.25, shade, ha="center", fontsize=9)
        for row, (name, family) in enumerate(rpl.colors.families.items()):
            y = -row * 0.7
            ax.text(-0.15, y - 0.28, name, ha="right", va="center", fontsize=9)
            for column, shade in enumerate(shades):
                color = getattr(family, shade)
                ax.add_patch(
                    Rectangle(
                        (column, y - 0.55),
                        0.96,
                        0.55,
                        facecolor=color,
                        edgecolor=rpl.colors.neutral.grid,
                        linewidth=0.3,
                    )
                )
        ax.set(xlim=(-0.8, 5), ylim=(-5.6, 0.65))
        ax.axis("off")
        rpl.export.savefig(fig, destination / "color-families", formats=("png",))
        plt.close(fig)


if __name__ == "__main__":
    main()
    render_neutrals()
    render_families()
