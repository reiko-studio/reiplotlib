"""Render the exact first-figure example from the README with LaTeX enabled.

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
    section = (root / "README.md").read_text().split("## A first figure\n", 1)[1]
    example = section.split("```python\n", 1)[1].split("```", 1)[0]
    destination = root / "docs/images"
    destination.mkdir(parents=True, exist_ok=True)
    previous = Path.cwd()
    with TemporaryDirectory() as temporary:
        try:
            os.chdir(temporary)
            exec(compile(example, "README.md: first figure", "exec"), {})
            shutil.copyfile("figures/response.png", destination / "response.png")
        finally:
            os.chdir(previous)


if __name__ == "__main__":
    main()
