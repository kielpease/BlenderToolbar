"""Read and atomically replace the toolbar's local layout file."""

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from ..core.layout import validate_layout


def read_layout(path: Path, action_ids: set[str], icon_ids: set[str]) -> dict | None:
    """Validate and migrate a candidate layout, or return None before the first save."""
    try:
        with path.open(encoding="utf-8") as source:
            layout = json.load(source)
    except FileNotFoundError:
        return None
    return validate_layout(layout, action_ids, icon_ids)


def write_layout(path: Path, layout: dict, action_ids: set[str], icon_ids: set[str]) -> None:
    """Replace the previous layout only after the new file is written."""
    layout = validate_layout(layout, action_ids, icon_ids)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as output:
            temporary = Path(output.name)
            json.dump(layout, output, ensure_ascii=False, indent=2)
            output.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
