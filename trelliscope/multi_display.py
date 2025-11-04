"""
Multi-display structure generation for trelliscope.

The viewer expects this structure:
root/
├── index.html
├── config.json
└── displays/
    ├── displayList.json
    └── display_name/
        ├── displayInfo.json
        ├── metaData.json
        ├── metaData.js
        └── panels/
"""

from pathlib import Path
import json
from typing import List, Dict, Any


def create_config_json(
    output_path: Path,
    name: str = "Trelliscope Display",
    display_base: str = "displays"
) -> Path:
    """
    Create config.json file at root.

    Parameters
    ----------
    output_path : Path
        Root directory path.
    name : str
        Display collection name.
    display_base : str
        Subdirectory containing displays.

    Returns
    -------
    Path
        Path to created config.json.
    """
    config = {
        "name": name,
        "datatype": "json",
        "id": "trelliscope_root",
        "display_base": display_base
    }

    config_path = output_path / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    return config_path


def create_display_list(
    displays_dir: Path,
    display_entries: List[Dict[str, Any]]
) -> Path:
    """
    Create displayList.json file.

    Parameters
    ----------
    displays_dir : Path
        Path to displays directory.
    display_entries : list of dict
        List of display entries with name, description, etc.

    Returns
    -------
    Path
        Path to created displayList.json.
    """
    list_path = displays_dir / "displayList.json"
    with open(list_path, "w", encoding="utf-8") as f:
        json.dump(display_entries, f, indent=2)

    return list_path


def create_multi_display_structure(
    output_path: Path,
    display_name: str,
    description: str = "",
    collection_name: str = "Trelliscope Displays"
) -> Dict[str, Path]:
    """
    Create proper multi-display directory structure.

    Parameters
    ----------
    output_path : Path
        Root output directory.
    display_name : str
        Name of the display.
    description : str, optional
        Display description.
    collection_name : str, optional
        Name of the display collection.

    Returns
    -------
    dict
        Paths to created directories:
        - root: Root directory
        - displays_dir: displays/ subdirectory
        - display_dir: displays/display_name/ subdirectory
        - panels_dir: displays/display_name/panels/ subdirectory
    """
    # Create root directory
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create displays subdirectory
    displays_dir = output_path / "displays"
    displays_dir.mkdir(exist_ok=True)

    # Create display-specific directory
    display_dir = displays_dir / display_name
    display_dir.mkdir(exist_ok=True)

    # Create panels subdirectory
    panels_dir = display_dir / "panels"
    panels_dir.mkdir(exist_ok=True)

    # Create config.json
    create_config_json(output_path, name=collection_name, display_base="displays")

    # Create displayList.json
    display_entry = {
        "name": display_name,
        "description": description,
        "tags": [],
        "thumbnailurl": f"{display_name}/panels/0.png",
        "order": 0
    }
    create_display_list(displays_dir, [display_entry])

    return {
        "root": output_path,
        "displays_dir": displays_dir,
        "display_dir": display_dir,
        "panels_dir": panels_dir
    }
