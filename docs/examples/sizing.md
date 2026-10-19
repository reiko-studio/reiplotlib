# Size and style

Journal figures need to fit the manuscript's columns while keeping their labels
readable alongside the surrounding text. Resizing a finished plot also scales
its fonts, markers, and line widths, so a figure that looked balanced on screen
may feel quite different on the page. Starting at the intended size makes these
choices easier to judge and leaves less to adjust when inserting the figure.

Reiplotlib provides column widths through the `journal` argument to
`layouts.subplots()`. Choose a single- or double-column figure and set its
height with `aspect`, the ratio of height to width. PRL (`journal="prl"`) is
the current preset; more journal sizes are planned.

![Figure sizes drawn to a common scale: single column, double column with two panels, and a custom size](../images/sizing.png){ width="720" }

```python
import numpy as np
import reiplotlib as rpl
from reiplotlib import layouts as layout

from reiplotlib import layouts as layout

fig, ax = layout.subplots(journal="prl", width="single", aspect=0.75)
fig, axs = layout.subplots(1, 2, journal="prl", width="double", aspect=0.45)
fig, ax = layout.subplots(figsize=(3.3, 3.0))
```

For the PRL preset, the widths are 243 TeX points (3.36 inches) for a single
column and 486 points (6.72 inches) for two columns. The size applies to the
whole figure, including all panels. In the sketches above, the outer rectangles
share a common scale and the dashed boxes indicate the plot areas.

You can also supply `figsize` directly, which takes precedence over the preset.
If you prefer creating axes with `plt.subplots()`,
`layout.size("single", journal="prl", aspect=0.75)` returns the corresponding
dimensions in inches. These describe the figure canvas; tight cropping can
change the saved bounds, so pass `bbox_inches=None` when exporting to preserve
the exact dimensions.

The option presets are already curated to choose line widths, marker and scatter sizes, 
error-bar caps, and fill opacity with paper figures in mind. You can use them as they are,
without tuning each element separately:

```python
from reiplotlib import options as o

ax.plot(x, y, **o.line())
ax.scatter(x, y, **o.scatter())
ax.fill_between(x, lo, hi, **o.fill())
```

They return ordinary keyword dictionaries, so an occasional adjustment is still
easy: `o.line(linewidth=1.2, linestyle="--")`. Without a color argument,
Matplotlib chooses from the axes' palette. You can still choose one explicitly,
as in `o.line(c.blue)`. Lines and fills follow Matplotlib's separate cycles;
use `rpl.shade()` when a band should match the line you just drew.

For a lighter frame, `rpl.clean_axes(ax, grid=False)` removes the top and right
spines while keeping the ticks. The style includes short minor ticks between
the major ticks on both axes. `rpl.clean_legend(ax)` gathers labeled artists
into a compact legend. Panel labels can be added with `rpl.label_panel(ax, "A")`,
and fractions can be displayed as percentages with `rpl.percent_axis(ax, axis="y")`.
