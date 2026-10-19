# reiplotlib

Reiplotlib is a collection of Matplotlib utilities, styles, and slightly
opinionated presets for consistent, publication-ready figures.

It brings together column-sized layouts, sensible line and marker sizes,
coordinated colors, and helpers for the repetitive parts of making a paper
figure. Plot with ordinary Matplotlib and adjust anything you need.

Part of **Reiko Studio**.

**[Documentation](https://reiko-studio.github.io/reiplotlib/)** ·
[Examples](https://reiko-studio.github.io/reiplotlib/examples/first-figure/) ·
[API reference](https://reiko-studio.github.io/reiplotlib/api/reiplotlib.html)

<img src="docs/images/style-comparison.png" alt="The same damped oscillations with default Matplotlib on the left and reiplotlib styling on the right" width="720">

## Installation

```bash
pip install git+https://github.com/reiko-studio/reiplotlib.git
```

Requires Python ≥3.10 and Matplotlib ≥3.7. The default style uses LaTeX, so you
will also need a TeX installation. To use Matplotlib's own text rendering,
pass `{"text.usetex": False}` to `rpl.rc_context()` or `rpl.apply_style()`.

## A first figure

We can start with a few damped oscillations. Most of this is ordinary Matplotlib:
reiplotlib sets the style and figure size, and each line takes its next color
from the Grove palette.

```python
import numpy as np
import reiplotlib as rpl
from reiplotlib import layouts as layout

x = np.linspace(0, 12, 400)

with rpl.rc_context():
    fig, ax = layout.subplots(width="single", aspect=0.75, layout="constrained")
    for tau in (1.5, 3.0, 6.0):
        y = np.exp(-x / tau) * np.cos(2 * np.pi * x / 4)
        ax.plot(x, y, label=rf"$\tau={tau:g}$")
    ax.set(xlim=(0, 12), xlabel=r"Time, $t$",
           ylabel=r"Response, $C(t)$")
    rpl.clean_axes(ax, grid=False)
    rpl.clean_legend(ax)
    rpl.export.savefig(fig, "figures/response")
```

<img src="docs/images/response.png" alt="Three damped oscillations using the default Grove colors in a single-column figure" width="360">

The export helper writes both PNG and PDF and creates the output directory.
`rc_context()` keeps the style local to this figure; use `rpl.apply_style()` at
the start of a script to apply it throughout.

## More examples

The [documentation](https://reiko-studio.github.io/reiplotlib/) includes rendered
examples and the full API:

- [Palettes and named colors](https://reiko-studio.github.io/reiplotlib/examples/colors/),
  including custom color families.
- [Figure sizing](https://reiko-studio.github.io/reiplotlib/examples/sizing/) and
  [multiple panels](https://reiko-studio.github.io/reiplotlib/examples/panels/).
- [Numeric color scales and colorbars](https://reiko-studio.github.io/reiplotlib/examples/color-scales/).
- [Consistent series styles](https://reiko-studio.github.io/reiplotlib/examples/series/)
  and [shared legends](https://reiko-studio.github.io/reiplotlib/examples/legends/).
- [Uncertainty bands, adaptive error bars, and visible-range limits](https://reiko-studio.github.io/reiplotlib/examples/uncertainty/).
- [Secondary axes](https://reiko-studio.github.io/reiplotlib/examples/secondary-axes/)
  and [export options](https://reiko-studio.github.io/reiplotlib/examples/export/).

[Contributing](CONTRIBUTING.md) · [MIT license](LICENSE)
