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

Compare three damped oscillations using Grove colors, matching shaded bands,
and LaTeX labels. The bands below are illustrative widths, not estimated errors.

```python
import numpy as np
import reiplotlib as rpl
from reiplotlib import layouts as layout, options as o, palettes as p

x = np.linspace(0, 12, 400)

with rpl.rc_context({"text.usetex": True}):
    fig, ax = layout.subplots(width="double", aspect=0.46, layout="constrained")
    for tau, color in zip((1.5, 3.0, 6.0), p.grove[:3]):
        envelope = np.exp(-x / tau)
        y = envelope * np.cos(2 * np.pi * x / 4)
        band = 0.06 * envelope
        ax.fill_between(x, y - band, y + band, **o.fill(color, alpha=0.16))
        ax.plot(x, y, label=rf"$\tau={tau:g}$",
                **o.markerline(color, markevery=32, linewidth=1.5))
    ax.axhline(0, color=rpl.colors.neutral.muted, lw=0.7, ls=":")
    ax.set(xlim=(0, 12), xlabel=r"Time, $t$",
           ylabel=r"Response, $C(t)$",
           title=r"$C(t)=e^{-t/\tau}\cos(\pi t/2)$")
    rpl.clean_axes(ax, grid=False)
    rpl.clean_legend(ax, ncols=3, loc="upper right")
    rpl.export.savefig(fig, "figures/response")
```

![Damped oscillations in three Grove colors, with LaTeX labels and illustrative bands](docs/images/response.png)

This saves `figures/response.png` and `figures/response.pdf`. The context applies
reiplotlib's style while making and saving the figure, then restores your previous
Matplotlib settings. The default style uses neutral text and axes with Grove
series colors; here the colors are explicit so each band matches its curve.

This example requires a working LaTeX installation. The style loads `amsfonts`
and configures `pdflatex` for PGF output. For a preview without LaTeX, change the
context to `rpl.rc_context({"text.usetex": False})`.

For a script where every figure should share the same style, apply it once:

```python
rpl.apply_style({"text.usetex": False, "font.size": 11})
```

### Palettes

![Categorical palettes grouped by size, with color swatches and hex codes](docs/images/palettes.png)

| Palette | Colors | Description |
| --- | --- | --- |
| `paper` | 6 | Original cycle: ink, dark teal, burgundy, gold, green, and gray. |
| `grove` | 6 | Default: muted blue, ochre, teal, rose, violet, and olive. |
| `myth` | 5 | Hololive Myth-inspired blue, orange, purple, pink, and gold. |
| `contrast` | 5 | Dark teal, pink, ink, gold, and green. |
| `duo` | 4 | Brighter cyan, rose, gold, and green. |
| `tol_bright` | 7 | Paul Tol's Bright scheme, in its recommended cycle order. |

`tol_bright` reproduces the hex values from
[Paul Tol's colour schemes](https://sronpersonalpages.nl/~pault/#sec:qualitative),
where Bright is documented as a colour-blind-safe scheme for lines and labels.

These palettes represent categories, not numeric magnitude. Myth adapts the
member colors for plotting on white; its hex values are not official color
specifications. Existing palettes remain available unchanged.

```python
from reiplotlib import palettes as p

rpl.use_palette(ax, p.grove)  # Or p.myth / p.paper
ax.plot(x, y, label="Measurement")
ax.plot(x, y_reference, label="Reference")
```

For explicit colors, use `p.grove[0]`, `p.grove[1]`, and so on. Entries are strings
accepted by Matplotlib. `p.get("grove")` and `rpl.palette("grove")` retrieve the
same colors; `p.cycle("grove")` returns a Matplotlib property cycle. Colors repeat
when the cycle runs out. Keep series colors consistent across panels.

Matching bands can use the same color with a lower opacity:

```python
ax.plot(x, y, color=p.grove[0])
ax.fill_between(x, lo, hi, color=p.grove[0], alpha=0.16)
```

For crowded or monochrome figures, also distinguish curves with markers or line
styles. The custom palettes have not yet been validated for color-vision
accessibility; Tol Bright's accessibility guidance comes from its author.
The default style uses Grove for series, neutral ink for text and axes, white
backgrounds, and neutral gray gridlines.

### Adaptive error bars

`rpl.errorbar()` draws a normal Matplotlib errorbar plot, but skips individual
error bars whose full displayed span is smaller than the marker:

```python
rpl.errorbar(ax, x, y, yerr=se, **o.errorbar(p.grove[3]))
```

The check runs before each render, so zooming, resizing, log scales, and PNG/PDF
exports use the current layout. Skipped bars can reappear; their caps disappear
with them. Markers and connecting lines are unchanged. Asymmetric errors use
their complete lower-to-upper span; x and y errors are checked independently.
The original uncertainties remain in the autoscaling bounds. No estimates or
uncertainties are changed, and visibility is not a significance test.

Set `hide_small_errors=False` to draw every bar, or `min_error_size=1.5` to
require a span greater than 1.5 marker diameters. Without markers, finite
nonzero bars remain visible. Automatic hiding supports rectilinear axes;
polar axes and one-sided limit arrows require opting out. The function returns
an ErrorbarContainer compatible with legends and `remove()`. Data/error inputs
are fixed at creation; redraws adapt visibility, not the underlying estimates.
`rpl.options.errorbar()` remains a keyword preset and is unchanged.

### Adjust the plot

`o.line()` and `o.markerline()` return dictionaries of plotting keywords.
Override any value in the call, just as you would with Matplotlib:

```python
ax.plot(x, y, **o.line(p.grove[0], linewidth=1.2, linestyle="--"))
```

There are presets for other common plotting calls too:

```python
ax.plot(x, y, **o.markers(p.grove[0], markersize=3))
ax.scatter(x, y, **o.scatter(p.grove[2], s=12))
ax.errorbar(x, y, yerr, **o.errorbar(p.grove[3], capsize=4))
ax.fill_between(x, lo, hi, **o.fill(p.grove[1], alpha=0.2))
ax.hist(samples, **o.hist(p.grove[0], bins=24))
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

Regenerate the palette preview with:

```bash
PYTHONPATH=src python scripts/render_palettes.py
PYTHONPATH=src python scripts/render_example.py
```

### Scale y to the visible x range

Call this after plotting and setting your x limits:

```python
ax.set_xlim(1.6, 10)
rpl.autoscale_y(ax, margin=0.05)
```

Off-screen points no longer stretch the y axis. Shared-y panes combine the
visible ranges of all siblings, including error bars and clipped line segments.
Explicit y limits are preserved; use `override=True` to replace them.
`watch=True` updates on x-limit changes and returns `(axes, callback_id)` pairs
that can be disconnected with `axes.callbacks.disconnect(callback_id)`.
The helper supports lines, scatter, and line collections, not images or filled
patches. It changes limits only, never data. Use `visible_only=False` to include
the full data range.

[MIT license](LICENSE).
