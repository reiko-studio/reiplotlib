"""Render default Matplotlib beside reiplotlib for the README opening."""

from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

import reiplotlib as rpl


def main():
    destination = Path(__file__).resolve().parents[1] / "docs/images"
    destination.mkdir(parents=True, exist_ok=True)
    x = np.linspace(0, 10, 300)
    with mpl.rc_context(mpl.rcParamsDefault):
        fig = plt.figure(figsize=(7.5, 2.6), layout="constrained")
        grid = fig.add_gridspec(1, 3, width_ratios=(1, 0.08, 1))
        default = fig.add_subplot(grid[0])
        arrow = fig.add_subplot(grid[1])
        arrow.axis("off")
        arrow.text(0.5, 0.5, r"$\rightarrow$", ha="center", va="center", fontsize=20)
        for tau in (1.5, 3.0, 6.0):
            y = np.exp(-x / tau) * np.cos(np.pi * x / 2)
            default.plot(x, y, label=rf"$\tau={tau:g}$")
        default.set(title="Matplotlib", xlabel=r"Time, $t$", ylabel=r"$C(t)$")
        default.legend()

        with rpl.rc_context():
            styled = fig.add_subplot(grid[2])
            for tau in (1.5, 3.0, 6.0):
                y = np.exp(-x / tau) * np.cos(np.pi * x / 2)
                styled.plot(x, y, label=rf"$\tau={tau:g}$")
            styled.set(title="reiplotlib", xlabel=r"Time, $t$", ylabel=r"$C(t)$")
            rpl.clean_axes(styled, grid=False)
            rpl.clean_legend(styled)
            rpl.export.savefig(fig, destination / "style-comparison", formats=("png",))
        plt.close(fig)


if __name__ == "__main__":
    main()
