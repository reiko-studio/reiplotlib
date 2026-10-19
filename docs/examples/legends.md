# Shared legends

A figure often has the same curve in several panels, but only needs one legend
entry for it. `figure_legend()` gathers the labels across the axes and combines
matching entries. We can also give references and model curves their own groups:

```python
import numpy as np
import reiplotlib as rpl
from reiplotlib import layouts as layout

with rpl.rc_context({"text.usetex": True}):
    fig, axes = layout.subplots(1, 2, width="double", aspect=0.43,
                               layout="constrained", sharex=True, sharey=True)
    x = np.linspace(0, 6, 200)
    for ax, tau in zip(axes, (1.0, 2.0)):
        y = np.exp(-x / tau)
        ax.plot(x, y, color=rpl.colors.neutral.ink, ls="--", label="Reference")
        ax.plot(x, y + 0.035 * np.sin(2 * x), color=rpl.colors.blue,
                label="Model A")
        ax.set(title=rf"$\tau={tau:g}$", xlabel=r"Time, $t$", xlim=(0, 6))
        rpl.clean_axes(ax, grid=False)
    rpl.errorbar(axes[1], x[12::25], np.exp(-x[12::25] / 2) + 0.06,
                 yerr=0.025, color=rpl.colors.orange, marker="o",
                 markerfacecolor="none", ls="none", label="Model B")
    axes[0].set_ylabel("Response")

    rpl.figure_legend(fig, axes, include=["Model A", "Model B"],
                      order=["Model B", "Model A"], group="models", ncols=2,
                      loc="outside upper center")
    rpl.figure_legend(fig, axes, include=["Reference"], group="references",
                      loc="outside lower center")
    rpl.export.savefig(fig, "figures/shared-legends")
```

![Two panels with one shared model legend above and a separate reference legend below](../images/shared-legends.png){ width="720" }

Model B appears only in the right panel, but still belongs to the shared legend.
`include` selects entries by their labels; `order` brings the listed labels to
the front. Giving each legend a `group` lets us update it later without removing
the other groups. Repeating a call replaces that group rather than adding a
second copy. Constrained layout leaves room for the outside positions shown
here; other layouts may need their margins adjusted.

By default, repeated labels must have matching styles. If two panels use the
same label for different styles, choose distinct labels or explicitly select a
duplicate policy with `duplicates="first"` or `"last"`. Missing labels in
`include` or `order` raise `KeyError`, making typos easier to catch.

For more control, `rpl.collect_legend(axes)` returns a label-to-handle dictionary
without drawing anything. Pass that dictionary, or your own proxy handles, as
`rpl.figure_legend(fig, entries=entries)`. The drawing helper returns the
Matplotlib legend, so its title and other properties can still be adjusted.

### A shared legend inside one panel

If the same curves appear throughout a grid, the first panel can hold the legend
for all of them. Give `axes_legend()` the destination panel and the axes to
collect from:

```python
with rpl.rc_context({"text.usetex": True}):
    fig, axes = layout.subplots(3, 2, width="double", aspect=0.85,
                               layout="constrained", sharex=True, sharey=True)
    x = np.linspace(0, 6, 200)
    for panel, ax in enumerate(axes.flat):
        for tau in (0.25, 0.5, 1.0, 1.5, 2.0):
            y = np.exp(-x / (tau * (1 + 0.15 * panel)))
            ax.plot(x, y, label=rf"$\tau={tau:g}$")
        ax.set(title=f"Condition {panel + 1}", xlim=(0, 6))
        rpl.clean_axes(ax, grid=False)
    for ax in axes[-1]:
        ax.set_xlabel(r"Time, $t$")
    for ax in axes[:, 0]:
        ax.set_ylabel("Response")

    rpl.axes_legend(axes[0, 0], axes, loc="upper right", fontsize=7)
    rpl.export.savefig(fig, "figures/panel-legend")
```

![Six panels with five repeated curves and one shared legend inside the first panel](../images/panel-legend.png){ width="720" }

Only the first panel gets a legend. The same `include` and `order` arguments
work here, so you can gather just the repeated methods there and keep a separate
reference entry in another panel. Omitting the second argument collects from
all panels in the destination's figure. Other panels' existing legends are left
alone; calling the helper again replaces the destination panel's legend.
