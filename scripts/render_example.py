"""Render the README quick start and documentation examples with LaTeX enabled.

Run with PYTHONPATH=src python scripts/render_example.py.
"""

import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import matplotlib

matplotlib.use("Agg")

from render_inset_comparison import main as render_inset_comparison


def main():
    root = Path(__file__).resolve().parents[1]
    destination = root / "docs/images"
    destination.mkdir(parents=True, exist_ok=True)
    previous = Path.cwd()
    with TemporaryDirectory() as temporary:
        try:
            os.chdir(temporary)
            namespace = {}
            for source, heading, stem in (
                ("README.md", "## A first figure", "response"),
                (
                    "docs/examples/color-scales.md",
                    "# Numeric color scales",
                    "color-scale",
                ),
                ("docs/examples/color-scales.md", "### Discrete bins", "discrete-bins"),
                (
                    "docs/examples/color-scales.md",
                    "### A colorbar in place of a legend",
                    "decay-colorbar",
                ),
                ("docs/examples/colors.md", "### Your own color", "custom-color"),
                ("docs/examples/panels.md", "# A figure with two panels", "panels"),
                (
                    "docs/examples/series.md",
                    "# Keeping series consistent",
                    "series-styles",
                ),
                ("docs/examples/legends.md", "# Shared legends", "shared-legends"),
                (
                    "docs/examples/legends.md",
                    "### A shared legend inside one panel",
                    "panel-legend",
                ),
                (
                    "docs/examples/secondary-axes.md",
                    "# Secondary axes",
                    "secondary-axes",
                ),
                ("docs/examples/insets.md", "# Insets", "insets"),
                ("docs/examples/uncertainty.md", "### Shaded bands", "shading"),
                ("docs/examples/uncertainty.md", "### Error bars", "errorbars"),
                ("docs/examples/uncertainty.md", "### Visible limits", "autoscale"),
                (
                    "docs/examples/uncertainty.md",
                    "### Shaded bands with a fixed baseline",
                    "autoscale-band",
                ),
            ):
                text = (root / source).read_text()
                section = text.split(heading + "\n", 1)[1]
                example = section.split("```python\n", 1)[1].split("```", 1)[0]
                exec(compile(example, f"{source}: {heading}", "exec"), namespace)
                shutil.copyfile(f"figures/{stem}.png", destination / f"{stem}.png")
            render_inset_comparison()
        finally:
            os.chdir(previous)


if __name__ == "__main__":
    main()
