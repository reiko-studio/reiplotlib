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
            len(names), 1, width="double", aspect=0.10 * len(names),
            layout="constrained",
        )
        fig.get_layout_engine().set(h_pad=0.01, w_pad=0.02, hspace=0.01)
        for name, swatches in zip(names, axes, strict=True):
            palette = p.get(name)
            swatches.set_title(
                name.replace("_", r"\_"), loc="left", fontsize=10, pad=1
            )
            for i, color in enumerate(palette):
                swatches.add_patch(Rectangle((i, 0), 0.94, 0.5, color=color))
                swatches.text(
                    i + 0.47, -0.06, str(color).replace("#", r"\#"),
                    ha="center", va="top", fontsize=6, fontfamily="monospace",
                )
            swatches.set(xlim=(-0.05, max_colors), ylim=(-0.20, 0.55))
            swatches.axis("off")

        rpl.export.savefig(fig, destination / "palettes", formats=("png",))
        plt.close(fig)


if __name__ == "__main__":
    main()
