# A first figure

We can start with a few damped oscillations. Most of this is ordinary Matplotlib:
reiplotlib sets the style and figure size, and each line takes its next color
from the Grove palette.

```python
import numpy as np
import reiplotlib as rpl
from reiplotlib import layouts as layout

x = np.linspace(0, 12, 400)

with rpl.rc_context({"text.usetex": True}):
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

![Three damped oscillations using the default Grove colors in a single-column figure](../images/response.png){ width="360" }

By default, the figure is saved as both PNG `figures/response.png` and PDF `figures/response.pdf`, 
this is to make it simple to import a vectorize version into LaTeX and a rasterized version 
for a slide deck. 

Keeping the work inside `rc_context()` lets us use the style for this figure
without changing the rest of the session. For a script where every figure should
look the same, `rpl.apply_style()` applies it once at the beginning.
