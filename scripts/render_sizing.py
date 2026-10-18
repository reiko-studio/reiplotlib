"""Render the README sizing schematic using the public layout dimensions.

Run with PYTHONPATH=src python scripts/render_sizing.py.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import reiplotlib as rpl
from reiplotlib import colors as c
from reiplotlib import layouts as layout


def main():
    cases = (
        ("single", layout.size("single", aspect=0.75), 1, "aspect = 0.75"),
        ("double", layout.size("double", aspect=0.45), 2, "aspect = 0.45"),
        ("custom", (3.3, 3.0), 1, "figsize = (3.3, 3.0)"),
    )
    destination = Path(__file__).resolve().parents[1] / "docs/images"
    destination.mkdir(parents=True, exist_ok=True)
    with rpl.rc_context():
        fig, ax = layout.subplots(width="double", aspect=0.32)
        x = 0
        for name, (width, height), panels, caption in cases:
            ax.add_patch(
                Rectangle(
                    (x, 0),
                    width,
                    height,
                    facecolor=c.neutral.paper,
                    edgecolor=c.neutral.ink,
                    linewidth=0.8,
                )
            )
            gap = 0.25
            panel_width = (width - (panels + 1) * gap) / panels
            for panel in range(panels):
                ax.add_patch(
                    Rectangle(
                        (x + gap + panel * (panel_width + gap), 0.35),
                        panel_width,
                        height - 0.7,
                        fill=False,
                        edgecolor=c.neutral.grid,
                        linestyle="--",
                        linewidth=0.7,
                    )
                )
            ax.text(x + width / 2, height / 2, name, ha="center", fontsize=10)
            ax.text(x + width / 2, -0.4, caption, ha="center", fontsize=7)
            ax.annotate(
                "",
                (x, height + 0.4),
                (x + width, height + 0.4),
                arrowprops={
                    "arrowstyle": "<->",
                    "color": c.neutral.muted,
                    "linewidth": 0.6,
                },
            )
            ax.text(
                x + width / 2,
                height + 0.6,
                f"{width:.2f} in",
                ha="center",
                fontsize=8,
            )
            ax.annotate(
                "",
                (x + width + 0.25, 0),
                (x + width + 0.25, height),
                arrowprops={
                    "arrowstyle": "<->",
                    "color": c.neutral.muted,
                    "linewidth": 0.6,
                },
            )
            ax.text(
                x + width + 0.4,
                height / 2,
                f"{height:.2f} in",
                va="center",
                rotation=90,
                fontsize=8,
            )
            x += width + 1.5
        ax.set(xlim=(-0.2, x - 0.5), ylim=(-0.8, 4.1), aspect="equal")
        ax.axis("off")
        rpl.export.savefig(fig, destination / "sizing", formats=("png",))
        plt.close(fig)


if __name__ == "__main__":
    main()
