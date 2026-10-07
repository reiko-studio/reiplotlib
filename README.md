# reiplotlib

Matplotlib utilities, styles, and presets for consistent research figures.

```python
import reiplotlib as rpl

with rpl.rc_context({"text.usetex": False}):
    fig, ax = rpl.layouts.subplots()
    ax.plot([0, 1, 2], [0.2, 0.5, 0.9], **rpl.options.line())
    ax.set(xlabel="Time", ylabel="Response")
    rpl.clean_axes(ax)
    rpl.export.saveclose(fig, "response")  # PNG + PDF
```

Part of **Reiko Studio**. Reiplot is its plotting and visualization identity;
`reiplotlib` brings it to Python. A little personality, consistent plots.

<!-- Future Reiplot artwork can sit here without changing the documentation. -->

## Install

Requires Python ≥3.10 and Matplotlib ≥3.7.

```bash
pip install git+https://github.com/leogabac/fubumio.git
```

The repository currently uses its original name, `fubumio`. The installed
package is `reiplotlib`; use `import reiplotlib as rpl`.

## Styles

Use a temporary style for a figure, or apply defaults for a whole script:

```python
with rpl.rc_context({"font.size": 11}):
    fig, ax = rpl.layouts.subplots(width="double")
    # Plot with the same Matplotlib API you already use.

rpl.apply_style()  # Global rcParams
```

The default style uses white backgrounds, the `paper` color cycle, serif text,
and LaTeX rendering. It assumes a working LaTeX installation, with an
`amsfonts` preamble and `pdflatex` configured for PGF. Pass
`{"text.usetex": False}` to either style helper to use Matplotlib text rendering.
`rc_context()` restores the previous settings on exit.

## Colors & palettes

Named colors work directly as Matplotlib color values. Palettes are ordered
color sequences.

```python
from reiplotlib import colors as c, palettes as p

c.fubuki.base     # "#58BFCB"
c.mio.base        # "#D35C7F"
c.ina.purple      # "#594967"
c.ina.gold        # "#eaa36d"
c.suisei.blue     # "#76a7e8"

ax.plot(x, y, color=c.ina.gold)
rpl.use_palette(ax, p.ina_contrast)
ax.set_prop_cycle(p.cycle("paper"))

rpl.palette("ina_contrast")  # Tuple of color tokens
c.named["fubuki"]            # Dictionary lookup
```

| Palette | Colors / use |
| --- | --- |
| `paper` | Darker colors; the default style cycle |
| `duo` | Cyan, rose, gold, and green |
| `soft` | Lighter colors for fills and bands |
| `contrast` | Stronger line colors |
| `basic` | Red and blue variants |
| `ina` | Purple, gold, and pink variants |
| `ina_contrast` | Purple and gold |
| `ina_dark_contrast` | Darker purple and gold |
| `suisei` | Two blue tones |

## Plot presets

Presets return ordinary Matplotlib keyword dictionaries. Every preset accepts
overrides.

```python
from reiplotlib import options as o

ax.plot(x, y, **o.line(c.ina.gold, linewidth=1.2))
ax.plot(x, y, **o.markers(c.ina.purple, markersize=3))
ax.plot(x, y, **o.markerline(c.suisei.blue))
ax.scatter(x, y, **o.scatter(c.suisei.blue, s=12))
ax.errorbar(x, y, yerr, **o.errorbar(c.mio.base, capsize=4))
ax.fill_between(x, lo, hi, **o.fill(c.ina.gold, alpha=0.2))
ax.hist(samples, **o.hist(c.ina.purple, bins=24))
```

## Figure sizes & export

Layout helpers compute `figsize` and pass other arguments through to
`matplotlib.pyplot.subplots`. PRL widths are the default: 243 TeX points for
one column, 486 for two. `aspect` is height divided by width.

```python
from reiplotlib import layouts as layout

fig, ax = layout.subplots(width="single")
fig, axs = layout.subplots(1, 2, width="double", aspect=0.45)
fig, ax = layout.subplots(width=300, unit="pt", aspect=0.62)
fig, ax = layout.subplots(figsize=(3.3, 3.0))

layout.size("single", aspect=0.62)  # (width, height) in inches
layout.PRL_SINGLE_IN               # 243 / 72.27
layout.PRL_DOUBLE_IN               # 486 / 72.27
```

Export helpers save PNG and PDF by default, create parent directories, and
return the saved paths. Export defaults are `bbox_inches="tight"` and `dpi=300`.

```python
from reiplotlib import export

export.savefig(fig, "figures/result")      # result.png + result.pdf
export.savefig(fig, "figures/result.png")  # Same two formats
export.saveclose(fig, "figures/result")    # Save, then close
export.savefig(fig, "draft", formats=("png",), dpi=180)

fig.savefig("plot.png", **o.savefig(transparent=True))
```

## Axes helpers

All axes helpers return the axes.

```python
rpl.clean_axes(ax, keep=("left", "bottom"), grid=True)
rpl.clean_legend(ax, ncols=2)
rpl.percent_axis(ax, axis="y", decimals=0, xmax=1.0)
rpl.label_panel(ax, "A")
rpl.drop_axis_labels(ax, axis="x", tick_labels=False, ticks=False)
```

`clean_axes()` hides unused spines, removes tick marks, sets grid visibility,
and removes an existing legend frame. `clean_legend()` builds a compact legend
from labeled artists and does nothing if none exist. `drop_axis_labels()`
removes axis labels and, by default, tick labels and ticks; the example above
keeps both.

## Development

From a local checkout:

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

Small helpers, regular Matplotlib. Keep analysis logic in your own code.

[MIT license](LICENSE).
