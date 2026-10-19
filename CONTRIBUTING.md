# Working on reiplotlib

Install the development tools and run the checks:

```bash
pip install -e '.[dev]'
pytest
ruff check .
```

## Documentation

```bash
pip install -e '.[docs]'
python scripts/build_docs.py
python -m http.server --directory site 8000
```

Open `http://localhost:8000`. Material for MkDocs builds the guides and examples;
pdoc builds the standalone API under `site/api/`. The build uses temporary source
files and leaves the generated HTML in the ignored `site/` directory. Use
`--output /tmp/reiplotlib-site` to choose a different output directory.

Guide pages live in `docs/`; API text comes from source docstrings. Avoid adding
manual signature lists to the guides. Keep the README focused on the short
tutorial and figure highlights.

The example images are committed, so building the website does not require TeX.
To regenerate them, use the system's LaTeX installation:

```bash
PYTHONPATH=src python scripts/render_example.py
PYTHONPATH=src python scripts/render_palettes.py
PYTHONPATH=src python scripts/render_sizing.py
PYTHONPATH=src python scripts/render_style_comparison.py
```

## GitHub Pages

The docs workflow builds on pull requests and pushes to `main`; deployment runs
only on `main`. In the repository's **Settings → Pages**, choose **GitHub Actions**
as the source before the first deployment. No generated HTML needs to be committed.

The site currently uses `https://reiko-studio.github.io/reiplotlib/`, matching the
repository remote. If the repository is renamed, update `mkdocs.yml` and the
project URLs in `pyproject.toml`.
