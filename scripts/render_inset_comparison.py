"""Compare inset styling with identical data, placement and parent styling."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

import reiplotlib as rpl


def main():
    destination = Path(__file__).resolve().parents[1] / "docs/images"
    destination.mkdir(parents=True, exist_ok=True)
    with rpl.rc_context({"text.usetex": True}):
        fig, axes = rpl.layouts.subplots(
            1, 2, width="double", aspect=0.43, layout="constrained", sharey=True
        )
        t = np.linspace(0, 10, 500)
        for ax, title in zip(
            axes, ("Default inset", "Styled inset + backing"), strict=True
        ):
            inset = ax.inset_axes([0.55, 0.54, 0.40, 0.38])
            for tau in (1.5, 2.5):
                response = np.exp(-t / tau) * (1 + 0.12 * np.cos(5 * t))
                ax.plot(t, response)
                inset.plot(t, response)
            ax.set(xlim=(0, 10), ylim=(0, 1.2), xlabel=r"Time, $t$", title=title)
            inset.set(
                xlim=(6, 10),
                ylim=(0, 0.12),
                xlabel=r"$t$",
                ylabel="Response",
                xticks=[6, 10],
                yticks=[0, 0.1],
            )
            rpl.clean_axes(ax)
            rpl.clean_axes(inset, grid=False)
            if ax is axes[1]:
                rpl.style_inset(inset)
                rpl.inset_backing(inset, pad=3, alpha=0.92)
        axes[0].set_ylabel("Response")
        rpl.export.savefig(fig, destination / "inset-comparison", formats=("png",))
        plt.close(fig)


if __name__ == "__main__":
    main()
