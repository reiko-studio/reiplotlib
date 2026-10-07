"""Figure export helpers."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from . import options as o


def savefig(
    fig: Figure,
    out_file: str | Path,
    *,
    formats: Iterable[str] = ("png", "pdf"),
    parents: bool = True,
    **overrides: Any,
) -> tuple[Path, ...]:
    """Save a figure to one or more formats."""

    path = Path(out_file)
    base = path.with_suffix("") if path.suffix else path

    if parents:
        base.parent.mkdir(parents=True, exist_ok=True)

    save_options = o.savefig(**overrides)
    saved: list[Path] = []
    for fmt in formats:
        suffix = fmt if fmt.startswith(".") else f".{fmt}"
        target = base.with_suffix(suffix)
        fig.savefig(target, **save_options)
        saved.append(target)

    return tuple(saved)


def saveclose(
    fig: Figure,
    out_file: str | Path,
    *,
    formats: Iterable[str] = ("png", "pdf"),
    parents: bool = True,
    **overrides: Any,
) -> tuple[Path, ...]:
    """Save a figure and close it."""

    saved = savefig(
        fig,
        out_file,
        formats=formats,
        parents=parents,
        **overrides,
    )
    plt.close(fig)
    return saved


__all__ = ["saveclose", "savefig"]
