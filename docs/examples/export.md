# Export

```python
import numpy as np
import reiplotlib as rpl
from reiplotlib import layouts as layout

rpl.export.savefig(fig, "figures/response")                 # PNG + PDF, 300 dpi
rpl.export.savefig(fig, "figures/draft", formats=("png",))  # PNG only
rpl.export.saveclose(fig, "figures/response")               # Save and close
```

The export helper creates the output directory if needed. Keep the save call
inside the style context so LaTeX and the other settings are still active when
the figure is rendered. Matplotlib's usual save options also work here, including
`transparent=True` and `bbox_inches=None`.

