# reiplotlib

Reiplotlib is a set of matplotlib utilities, styles, and slightly opinionated presets for
consistent publication-ready figures.

```python
import reiplotlib as rpl

with rpl.rc_context({"text.usetex": False}):
    fig, ax = rpl.layouts.subplots()
    ax.plot([0, 1, 2], [0.2, 0.5, 0.9], **rpl.options.line())
    ax.set(xlabel="Time", ylabel="Response")
    rpl.clean_axes(ax)
    rpl.export.saveclose(fig, "response")  # PNG + PDF
```

Part of **Reiko Studio**.

<!-- future Reiplot artwork will be here -->

## Installation

Requires Python ≥3.10 and Matplotlib ≥3.7.

```bash
pip install git+https://github.com/reiko-studio/reiplotlib.git
```

Ideally, a LaTeX compiler available.

## A first figure

Start with a single-column figure and two data series:

```python
import reiplotlib as rpl
from reiplotlib import colors as c, layouts as layout, options as o

x = [0, 1, 2, 3]
y = [0.15, 0.35, 0.60, 0.85]
y_reference = [0.10, 0.30, 0.55, 0.80]

with rpl.rc_context({"text.usetex": False}):
    fig, ax = layout.subplots(width="single", aspect=0.75)
    ax.plot(x, y, label="Measurement", **o.markerline(c.ina.purple))
    ax.plot(x, y_reference, label="Reference", **o.line(c.ina.gold))
    ax.set(xlabel="Time", ylabel="Response")
    rpl.clean_axes(ax, grid=False)
    rpl.clean_legend(ax)
    rpl.export.savefig(fig, "figures/response")
```

This saves `response.png` and `response.pdf`. The context applies the style
while making and saving the figure, then restores your previous Matplotlib
settings.

The default style enables LaTeX. The example turns it off so you can try it
without a TeX installation. If you have LaTeX available, use
`with rpl.rc_context():` for serif text rendered through TeX. The style loads
`amsfonts` and configures `pdflatex` for PGF output.

For a script where every figure should share the same style, apply it once:

```python
rpl.apply_style({"text.usetex": False, "font.size": 11})
```

### Choose colors

The example passes colors explicitly. You can also give an axes a palette and
let Matplotlib choose the next color for each series:

```python
from reiplotlib import palettes as p

rpl.use_palette(ax, p.ina_contrast)
ax.plot(x, y, label="Measurement")
ax.plot(x, y_reference, label="Reference")
```

Color tokens are strings, so they work anywhere Matplotlib expects a color:

```python
c.fubuki.base     # "#58BFCB"
c.mio.base        # "#D35C7F"
c.ina.purple      # "#594967"
c.ina.gold        # "#eaa36d"
c.suisei.blue     # "#76a7e8"

ax.set_facecolor(c.neutral.white)
c.named["fubuki"]  # Named lookup
```

The default style uses `paper`. Other palettes are `duo`, `soft`, `contrast`,
`basic`, `ina`, `ina_contrast`, `ina_dark_contrast`, and `suisei`.
Use `p.get("paper")` or `rpl.palette("paper")` to retrieve one by name;
`p.cycle("paper")` produces a Matplotlib property cycle.

### Adjust the plot

`o.line()` and `o.markerline()` return dictionaries of plotting keywords.
Override any value in the call, just as you would with Matplotlib:

```python
ax.plot(x, y, **o.line(c.ina.purple, linewidth=1.2, linestyle="--"))
```

There are presets for other common plotting calls too:

```python
ax.plot(x, y, **o.markers(c.ina.purple, markersize=3))
ax.scatter(x, y, **o.scatter(c.suisei.blue, s=12))
ax.errorbar(x, y, yerr, **o.errorbar(c.mio.base, capsize=4))
ax.fill_between(x, lo, hi, **o.fill(c.ina.gold, alpha=0.2))
ax.hist(samples, **o.hist(c.ina.purple, bins=24))
```

In the first figure, `clean_axes()` keeps the left and bottom spines and removes
tick marks. It enables the grid by default; we passed `grid=False`.
`clean_legend()` creates a compact legend from the labeled series.

For a response expressed as a fraction, format the y axis as percentages:

```python
rpl.percent_axis(ax, axis="y", xmax=1.0, decimals=0)
```

For a panel figure, add a label or remove repeated axis labels:

```python
rpl.label_panel(ax, "A")
rpl.drop_axis_labels(ax, axis="x", tick_labels=False, ticks=False)
```

`drop_axis_labels()` removes tick labels and tick marks too unless you keep
them as above. All axes helpers return the axes.

### Change the figure size

`layout.subplots()` uses PRL column widths: 243 TeX points for a single column,
486 for a double column. `aspect` sets height divided by width. Other arguments
pass through to `matplotlib.pyplot.subplots`.

```python
fig, axs = layout.subplots(1, 2, width="double", aspect=0.45)
fig, ax = layout.subplots(width=300, unit="pt", aspect=0.62)
fig, ax = layout.subplots(figsize=(3.3, 3.0))
```

An explicit `figsize` takes precedence. For use with `plt.subplots()` directly,
`layout.size("single", aspect=0.75)` returns a size in inches. The constants
`layout.PRL_SINGLE_IN` and `layout.PRL_DOUBLE_IN` give the column widths,
converted using 72.27 TeX points per inch.

### Save the result

Save inside the style context when using LaTeX or other temporary text settings.
The export helper creates parent directories and returns the saved paths:

```python
from reiplotlib import export

export.savefig(fig, "figures/response")
export.savefig(fig, "figures/response.png")  # Also saves PNG and PDF
export.savefig(fig, "draft", formats=("png",), dpi=180)
export.saveclose(fig, "figures/response")   # Save, then close the figure
```

The defaults are `bbox_inches="tight"` and `dpi=300`. If you only need the save
options, use them with Matplotlib directly:

```python
fig.savefig("response.png", **o.savefig(transparent=True))
```

## Development

From a local checkout:

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

[MIT license](LICENSE).
