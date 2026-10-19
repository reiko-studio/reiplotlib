"""Build Material guides and a standalone pdoc API into one static site.

Install with pip install -e '.[docs]', then run python scripts/build_docs.py.
Preview with python -m http.server --directory site 8000.
"""

from __future__ import annotations

import argparse
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("site"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    protected = [
        root / name for name in ("docs", "src", "scripts", "tests", ".git", ".github")
    ]
    if (
        output == root
        or output in root.parents
        or any(output == path or path in output.parents for path in protected)
    ):
        parser.error("output must be a generated-site directory, not source files")
    with TemporaryDirectory(prefix="reiplotlib-docs-") as temporary:
        temporary = Path(temporary)
        source = temporary / "docs"
        shutil.copytree(root / "docs", source)
        environment = os.environ.copy()
        environment["PYTHONPATH"] = (
            str(root / "src") + os.pathsep + environment.get("PYTHONPATH", "")
        )
        environment["MPLBACKEND"] = "Agg"
        environment["PDOC_ALLOW_EXEC"] = "1"
        environment.setdefault("MPLCONFIGDIR", str(temporary / "matplotlib"))
        os.environ.setdefault("MPLBACKEND", "Agg")
        os.environ.setdefault("MPLCONFIGDIR", str(temporary / "matplotlib"))
        package = importlib.import_module("reiplotlib")
        exported_modules = {
            value.__name__
            for name in package.__all__
            if isinstance(value := getattr(package, name), ModuleType)
        }
        modules = ["reiplotlib"] + [
            f"reiplotlib.{path.stem}"
            for path in sorted((root / "src/reiplotlib").glob("*.py"))
            if not path.stem.startswith("_")
            and f"reiplotlib.{path.stem}" not in exported_modules
        ]
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pdoc",
                *modules,
                "-o",
                str(source / "api"),
                "-t",
                str(root / "scripts/pdoc-template"),
            ],
            cwd=root,
            env=environment,
            check=True,
        )
        from mkdocs.commands.build import build
        from mkdocs.config import load_config

        config = load_config(
            config_file=str(root / "mkdocs.yml"),
            docs_dir=str(source),
            site_dir=str(output),
            strict=True,
        )
        build(config)
    print(f"Built guides and API reference in {output}")


if __name__ == "__main__":
    main()
