"""Render the README plotting examples with LaTeX enabled.

Run with PYTHONPATH=src python scripts/render_example.py.
"""

import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import matplotlib

matplotlib.use("Agg")


def main():
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text()
    destination = root / "docs/images"
    destination.mkdir(parents=True, exist_ok=True)
    previous = Path.cwd()
    with TemporaryDirectory() as temporary:
        try:
            os.chdir(temporary)
            namespace = {}
            for heading, stem in (
                ("## A first figure", "response"),
                ("### Your own color", "custom-color"),
                ("## A figure with two panels", "panels"),
                ("## Keeping series consistent", "series-styles"),
                ("### Shaded bands", "shading"),
                ("### Error bars", "errorbars"),
                ("### Visible limits", "autoscale"),
            ):
                section = readme.split(heading + "\n", 1)[1]
                example = section.split("```python\n", 1)[1].split("```", 1)[0]
                exec(compile(example, f"README.md: {heading}", "exec"), namespace)
                shutil.copyfile(f"figures/{stem}.png", destination / f"{stem}.png")
        finally:
            os.chdir(previous)


if __name__ == "__main__":
    main()
