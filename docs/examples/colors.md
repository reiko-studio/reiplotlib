# Colors

## Palettes


Reiplotlib has a few curated palettes, grove is the default, but a different palette can give the same figure a rather different character. Set it on the axes before drawing the lines:

```python
import numpy as np
import reiplotlib as rpl
from reiplotlib import layouts as layout

from reiplotlib import palettes as p

rpl.use_palette(ax, p.myth)
ax.plot(x, y)
```

![Categorical palettes and their hex codes](../images/palettes.png){ width="720" }

Individual colors are available too: `p.grove[0]` is the first color, and
`p.get("grove")` retrieves the palette by name. These are ordinary color strings,
so they can be used anywhere Matplotlib expects a color. Once a cycle runs out,
it starts again; for many curves, different markers or line styles help.

Paper combines ink and gray with teal, burgundy, gold, and green. Myth draws on
[Hololive Myth's](https://hololive.hololivepro.com/en/talents?gp=myth) member colors, adapted for plotting .
Contrast and Duo offer smaller sets.
[Tol Bright](https://sronpersonalpages.nl/~pault/#sec:qualitative) uses Paul Tol's
seven published colors and recommended order.

## Named colors

Sometimes a curve needs a particular color, or a shaded region needs to belong
to the same family as its outline. The named colors give us a few shades to
choose from:

```python
from reiplotlib import colors as c

ax.plot(x, y, color=c.red)
ax.plot(x, y_reference, color=c.blue.dark)
ax.fill_between(x, lo, hi, color=c.red.pale)
```

![Named color families with dark, base, bright, light, and pale shades](../images/color-families.png){ width="720" }

`c.red` is shorthand for the base color. The darker shades work well for lines
and outlines, while the light and pale shades leave room for other information
when used as fills. Each family has `.dark`, `.base`, `.bright`, `.light`, and
`.pale`; these shades are chosen individually.
For lookup by name, use `c.named["red.dark"]` or browse `c.families`.

### Your own color

If you already have a color in mind, `NamedColor` can suggest a family around it.
The generated shades are a starting point, and any of them can be adjusted:

```python
custom = rpl.NamedColor("#467A9B")
custom.dark = "#233F59"  # Override one generated shade.

with rpl.rc_context({"text.usetex": True}):
    fig, ax = layout.subplots(width="single", aspect=0.65, layout="constrained")
    x = np.linspace(0, 6, 200)
    y = np.exp(-x / 2)
    ax.fill_between(x, 0, y, color=custom.pale)
    ax.plot(x, y, color=custom, label=r"$e^{-t/2}$")
    ax.plot(x, 0.8 * y, color=custom.dark, ls="--", label=r"$0.8e^{-t/2}$")
    ax.set(xlabel=r"Time, $t$", ylabel="Response", xlim=(0, 6), ylim=(0, 1.05))
    rpl.clean_axes(ax, grid=False)
    rpl.clean_legend(ax)
    rpl.export.savefig(fig, "figures/custom-color")
```

![A custom generated color family used for lines and a filled region](../images/custom-color.png){ width="360" }

Starting from a `#RGB` or `#RRGGBB` value, the darker shade mixes in 35% black;
the light and pale shades mix in 55% and 85% white in sRGB. The bright shade
increases HLS saturation and lightness toward their maxima by 25% and 10%.
This is a simple approximation, so some starting colors will need more
adjustment than others.

Changing `custom.base` generates a fresh family, so make any individual shade
adjustments afterward. `custom` itself works as a Matplotlib color, while
`custom.base` gives its hex string. To recolor a line that has already been
drawn, use `line.set_color(custom.base)`.

### Neutrals

For text and the quieter parts of a figure, there is a small neutral family:

![Neutral named colors: ink, muted, grid, paper, and white](../images/neutrals.png){ width="720" }

```python
from reiplotlib import colors as c

ax.axhline(0, color=c.neutral.muted, linestyle=":")
ax.set_facecolor(c.neutral.paper)
ax.set_title("Response", color=c.neutral.ink)
```

The default style uses `ink` for text and outlines, `white` for the background,
and `grid` for gridlines. `muted` is useful for reference lines and secondary
annotations; `paper` gives a slightly warmer background when pure white feels
too stark.
