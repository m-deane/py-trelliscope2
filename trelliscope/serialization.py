"""
JSON serialization for trelliscope displays.

Converts Display objects to displayInfo.json format for the JavaScript viewer.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from trelliscope.display import Display


def serialize_display_info(display: "Display") -> Dict[str, Any]:
    """
    Serialize Display to displayInfo.json format.

    This produces the JSON specification consumed by trelliscopejs-lib viewer.

    Parameters
    ----------
    display : Display
        Display object to serialize.

    Returns
    -------
    dict
        Dictionary matching displayInfo.json schema.

    Examples
    --------
    >>> from trelliscope import Display
    >>> import pandas as pd
    >>>
    >>> df = pd.DataFrame({"value": [1, 2, 3]})
    >>> display = Display(df, name="example")
    >>> display.infer_metas()
    >>>
    >>> info = serialize_display_info(display)
    >>> info["name"]
    'example'
    """
    from trelliscope.panel_interface import (
        LocalPanelInterface,
        PanelInterface,
        RESTPanelInterface,
    )

    # Serialize meta variables
    metas = []
    for varname in sorted(display._meta_vars.keys()):
        meta = display._meta_vars[varname]
        meta_dict = meta.to_dict()
        # Ensure all required fields for viewer compatibility
        if "tags" not in meta_dict:
            meta_dict["tags"] = []
        if "filterable" not in meta_dict:
            meta_dict["filterable"] = True
        if "sortable" not in meta_dict:
            meta_dict["sortable"] = True
        metas.append(meta_dict)

    # Add panel column metadata if panel column is set
    # The panel meta IS required in metas array for viewer to load panels
    if display.panel_column is not None:
        # Determine panel source configuration
        panel_source = None
        if display.panel_interface is not None:
            # Use configured panel interface
            if isinstance(display.panel_interface, RESTPanelInterface):
                # REST panel source
                panel_source = display.panel_interface.to_dict()
            elif isinstance(display.panel_interface, LocalPanelInterface):
                # Local file panel source
                panel_source = {
                    "type": "file",
                    "isLocal": True,
                    "port": 0,
                }
            elif isinstance(display.panel_interface, PanelInterface):
                # Generic panel interface - get dict representation
                source_dict = display.panel_interface.to_dict()
                # Ensure required fields
                if "type" not in source_dict:
                    source_dict["type"] = "file"
                if "isLocal" not in source_dict:
                    source_dict["isLocal"] = True
                panel_source = source_dict
        else:
            # Default to local file panels
            panel_source = {
                "type": "file",
                "isLocal": True,
                "port": 0,
            }

        # Detect panel type based on format
        panel_type = "img"  # Default to image panels
        if hasattr(display, "_panel_format") and display._panel_format == "html":
            panel_type = "iframe"  # HTML panels use iframe

        # Build panel meta variable
        panel_meta = {
            "varname": display.panel_column,
            "type": "panel",
            "label": "Panel",
            "paneltype": panel_type,
            "tags": [],
            "filterable": False,
            "sortable": False,
        }

        # Add panel aspect ratio if specified
        if display.panel_options.get("aspect") is not None:
            panel_meta["aspect"] = display.panel_options["aspect"]
        else:
            panel_meta["aspect"] = 1.0  # Default square aspect

        # Add panel source configuration
        panel_meta["source"] = panel_source

        # Add panel meta to metas list
        metas.append(panel_meta)

    # Build cogInfo structure (detailed metadata for each variable)
    cog_info = {}
    for varname in sorted(display._meta_vars.keys()):
        meta = display._meta_vars[varname]
        cog_info[varname] = {
            "name": varname,
            "label": meta.label if hasattr(meta, "label") else varname,
            "type": meta.type,
            "group": None,
            "defLabel": True,
            "defActive": True,
            "filterable": True,
            "sortable": True,
            "log": None,
        }
        # Add type-specific fields
        if meta.type == "factor" and hasattr(meta, "levels"):
            cog_info[varname]["levels"] = meta.levels

    # Add panelKey to cogInfo
    cog_info["panelKey"] = {
        "name": "panelKey",
        "label": "panelKey",
        "type": "panelKey",
        "group": None,
        "defLabel": False,
        "defActive": False,
        "filterable": False,
        "sortable": False,
        "log": None,
    }

    # Generate cogData from DataFrame
    cog_data = _serialize_cog_data(display)

    # Build top-level panelInterface
    panel_interface_dict = None
    if display.panel_column is not None:
        if isinstance(display.panel_interface, RESTPanelInterface):
            panel_interface_dict = display.panel_interface.to_dict()
        else:
            # Detect panel type from rendered files
            # Check if panels are HTML (iframe) or images (file)
            panel_type = "file"  # Default to image files
            panel_format = "png"  # Default extension

            # Check for HTML panels by looking at display attribute
            if hasattr(display, "_panel_format"):
                # Use format set by display
                panel_format = display._panel_format
                panel_type = "iframe" if panel_format == "html" else "file"

            # File-based panel interface
            # CRITICAL: type must be "file" for images, "iframe" for HTML
            # base must be "panels", NOT "./panels"
            panel_interface_dict = {
                "type": panel_type,
                "panelCol": display.panel_column,
                "base": "panels",
            }

            # Note: width, height, aspect, forceSize are NOT part of panelInterface
            # They are in panel_options at display level

    # Build displayInfo structure with ALL required fields
    info = {
        "name": display.name,
        "group": "common",  # Default group
        "description": display.description,
        "keysig": display.keysig,
        "n": (
            len(display.data)
            if hasattr(display, "data") and display.data is not None
            else 0
        ),
        "height": display.panel_options.get("height") or 500,
        "width": display.panel_options.get("width") or 500,
        "tags": [],
        "keycols": [],
        "metas": metas,
        "inputs": None,
        "cogInterface": {
            "name": display.name,
            "group": "common",
            "type": "JSON",
        },
        "cogInfo": cog_info,
        "cogDistns": {},
        "cogData": cog_data,
        "state": {
            "layout": display.state["layout"].copy(),
            "labels": display.state["labels"].copy(),
            "sort": display.state["sorts"].copy(),
            "filter": display.state["filters"].copy(),
        },
        "views": [view.copy() for view in display.views],
        "imgSrcLookup": {},
    }

    # Set primary panel and panelInterface if panel column is set
    if display.panel_column is not None:
        info["primarypanel"] = display.panel_column
        if panel_interface_dict is not None:
            info["panelInterface"] = panel_interface_dict

    return info


def _serialize_cog_data(display: "Display") -> List[Dict[str, Any]]:
    """
    Generate cogData array from Display's DataFrame.

    Converts DataFrame rows to cogData objects with panel references.
    For file-based panels, uses relative paths like "panels/0.png".

    Parameters
    ----------
    display : Display
        Display object with data.

    Returns
    -------
    list of dict
        cogData array with panel references and metadata.
    """
    from trelliscope.panel_interface import RESTPanelInterface

    cog_data = []

    for idx, row in display.data.iterrows():
        # Build cogData entry for this row
        entry = {}

        # Add all meta variable values
        for varname in display._meta_vars.keys():
            if varname in row:
                value = row[varname]
                # Convert numpy/pandas types to Python native types
                if hasattr(value, "item"):
                    value = value.item()
                # Convert pd.Timestamp to ISO format string
                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                # CRITICAL: Convert factor indices from 0-based to 1-based (R-style)
                # The trelliscopejs viewer expects R-style 1-based factor indexing
                # where levels[1-1] = levels[0] = first level
                meta = display._meta_vars.get(varname)
                if meta and meta.type == "factor":
                    if isinstance(value, (int, float)) and not (
                        isinstance(value, float) and value != value
                    ):
                        # Numeric categorical code (0, 1, 2...) but not NaN
                        # Note: NaN != NaN, so we check for that
                        value = int(value) + 1  # Convert 0-based to 1-based
                    elif (
                        isinstance(value, str)
                        and hasattr(meta, "levels")
                        and meta.levels
                    ):
                        # String value - look up index in levels and convert to 1-based
                        try:
                            idx = meta.levels.index(value)
                            value = idx + 1  # Convert to 1-based index
                        except (ValueError, AttributeError):
                            # Keep string value if not in levels
                            pass
                    # NaN/None values are kept as-is

                entry[varname] = value

        # Add panelKey (using index as panel ID)
        panel_id = str(idx)
        entry["panelKey"] = panel_id

        # Add panel reference
        if display.panel_column is not None:
            if isinstance(display.panel_interface, RESTPanelInterface):
                # For REST panels, panel value is the endpoint path
                entry[display.panel_column] = f"/panels/{panel_id}"
            else:
                # For file-based panels, use relative path with correct extension
                panel_format = "png"  # Default
                if hasattr(display, "_panel_format"):
                    panel_format = display._panel_format
                entry[display.panel_column] = f"{panel_id}.{panel_format}"

        cog_data.append(entry)

    return cog_data


def write_metadata_json(display: "Display", output_path: Path) -> Path:
    """
    Write metaData.json file with cogData array.

    This file contains the same cogData as embedded in displayInfo.json,
    but with relative panel paths like "panels/0.png".

    Parameters
    ----------
    display : Display
        Display object to serialize.
    output_path : Path
        Output directory path. File will be written to output_path/metaData.json.

    Returns
    -------
    Path
        Path to written metaData.json file.

    Raises
    ------
    OSError
        If file cannot be written.
    """
    from trelliscope.panel_interface import RESTPanelInterface

    # Build metadata array with relative panel paths
    metadata = []

    for idx, row in display.data.iterrows():
        entry = {}

        # Add all meta variable values
        for varname in display._meta_vars.keys():
            if varname in row:
                value = row[varname]
                # Convert numpy/pandas types to Python native types
                if hasattr(value, "item"):
                    value = value.item()
                # Convert pd.Timestamp to ISO format string
                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                # CRITICAL: Convert factor indices from 0-based to 1-based (R-style)
                meta = display._meta_vars.get(varname)
                if meta and meta.type == "factor":
                    if isinstance(value, (int, float)) and not (
                        isinstance(value, float) and value != value
                    ):
                        value = int(value) + 1
                    elif (
                        isinstance(value, str)
                        and hasattr(meta, "levels")
                        and meta.levels
                    ):
                        try:
                            idx_temp = meta.levels.index(value)
                            value = idx_temp + 1
                        except (ValueError, AttributeError):
                            pass

                entry[varname] = value

        # Add panelKey
        panel_id = str(idx)
        entry["panelKey"] = panel_id

        # Add panel reference with RELATIVE path for file-based panels
        if display.panel_column is not None:
            if isinstance(display.panel_interface, RESTPanelInterface):
                entry[display.panel_column] = f"/panels/{panel_id}"
            else:
                # Use correct extension for file-based panels
                panel_format = "png"  # Default
                if hasattr(display, "_panel_format"):
                    panel_format = display._panel_format
                # CRITICAL: Use "panels/{id}.{format}" format for viewer to find files
                entry[display.panel_column] = f"panels/{panel_id}.{panel_format}"

        metadata.append(entry)

    # Write JSON file
    json_path = output_path / "metaData.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return json_path


def write_metadata_js(display: "Display", output_path: Path) -> Path:
    """
    Write metaData.js file with window.metaData wrapper.

    This file is REQUIRED by trelliscopejs-lib viewer even when cogData
    is embedded in displayInfo.json. It must contain:
    window.metaData = [...];

    Parameters
    ----------
    display : Display
        Display object to serialize.
    output_path : Path
        Output directory path. File will be written to output_path/metaData.js.

    Returns
    -------
    Path
        Path to written metaData.js file.

    Raises
    ------
    OSError
        If file cannot be written.
    """
    from trelliscope.panel_interface import RESTPanelInterface

    # Build metadata array (same as metaData.json)
    metadata = []

    for idx, row in display.data.iterrows():
        entry = {}

        # Add all meta variable values
        for varname in display._meta_vars.keys():
            if varname in row:
                value = row[varname]
                # Convert numpy/pandas types to Python native types
                if hasattr(value, "item"):
                    value = value.item()
                # Convert pd.Timestamp to ISO format string
                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                # CRITICAL: Convert factor indices from 0-based to 1-based (R-style)
                meta = display._meta_vars.get(varname)
                if meta and meta.type == "factor":
                    if isinstance(value, (int, float)) and not (
                        isinstance(value, float) and value != value
                    ):
                        value = int(value) + 1
                    elif (
                        isinstance(value, str)
                        and hasattr(meta, "levels")
                        and meta.levels
                    ):
                        try:
                            idx_temp = meta.levels.index(value)
                            value = idx_temp + 1
                        except (ValueError, AttributeError):
                            pass

                entry[varname] = value

        # Add panelKey
        panel_id = str(idx)
        entry["panelKey"] = panel_id

        # Add panel reference
        if display.panel_column is not None:
            if isinstance(display.panel_interface, RESTPanelInterface):
                entry[display.panel_column] = f"/panels/{panel_id}"
            else:
                # Use correct extension for file-based panels
                panel_format = "png"  # Default
                if hasattr(display, "_panel_format"):
                    panel_format = display._panel_format
                # CRITICAL: Use "panels/{id}.{format}" format
                entry[display.panel_column] = f"panels/{panel_id}.{panel_format}"

        metadata.append(entry)

    # Convert to JSON string
    json_str = json.dumps(metadata, indent=2, ensure_ascii=False)

    # Wrap in window.metaData assignment
    js_content = f"window.metaData = {json_str};\n"

    # Write JavaScript file
    js_path = output_path / "metaData.js"
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    return js_path


def write_display_info(display: "Display", output_path: Path) -> Path:
    """
    Write displayInfo.json file for Display.

    Parameters
    ----------
    display : Display
        Display object to serialize.
    output_path : Path
        Output directory path. File will be written to output_path/displayInfo.json.

    Returns
    -------
    Path
        Path to written displayInfo.json file.

    Raises
    ------
    OSError
        If directory cannot be created or file cannot be written.

    Examples
    --------
    >>> from trelliscope import Display
    >>> from pathlib import Path
    >>>
    >>> display = Display(df, name="example")
    >>> output = Path("./output")
    >>>
    >>> json_path = write_display_info(display, output)
    >>> print(json_path)
    output/displayInfo.json
    """
    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Serialize display info
    info = serialize_display_info(display)

    # Write JSON file
    json_path = output_path / "displayInfo.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    return json_path


def serialize_to_json_string(display: "Display", indent: int = 2) -> str:
    """
    Serialize Display to JSON string.

    Parameters
    ----------
    display : Display
        Display object to serialize.
    indent : int, default=2
        JSON indentation level.

    Returns
    -------
    str
        JSON string representation.

    Examples
    --------
    >>> json_str = serialize_to_json_string(display)
    >>> print(json_str)
    {
      "name": "example",
      ...
    }
    """
    info = serialize_display_info(display)
    return json.dumps(info, indent=indent, ensure_ascii=False)


def validate_display_info(info: Dict[str, Any]) -> List[str]:
    """
    Validate displayInfo dictionary structure.

    Checks for required fields and correct types.

    Parameters
    ----------
    info : dict
        Display info dictionary to validate.

    Returns
    -------
    list of str
        List of validation error messages. Empty if valid.

    Examples
    --------
    >>> info = serialize_display_info(display)
    >>> errors = validate_display_info(info)
    >>> if not errors:
    ...     print("Valid!")
    """
    errors = []

    # Required fields
    required = ["name", "description", "keysig", "metas", "state"]
    for field in required:
        if field not in info:
            errors.append(f"Missing required field: {field}")

    # Validate name
    if "name" in info:
        if not isinstance(info["name"], str):
            errors.append(f"'name' must be string, got {type(info['name']).__name__}")
        elif not info["name"].strip():
            errors.append("'name' cannot be empty")

    # Validate metas
    if "metas" in info:
        if not isinstance(info["metas"], list):
            errors.append(f"'metas' must be list, got {type(info['metas']).__name__}")
        else:
            for i, meta in enumerate(info["metas"]):
                if not isinstance(meta, dict):
                    errors.append(f"metas[{i}] must be dict")
                elif "varname" not in meta:
                    errors.append(f"metas[{i}] missing 'varname'")
                elif "type" not in meta:
                    errors.append(f"metas[{i}] missing 'type'")

    # Validate state
    if "state" in info:
        if not isinstance(info["state"], dict):
            errors.append(f"'state' must be dict, got {type(info['state']).__name__}")
        else:
            state_required = ["layout", "labels", "sort", "filter"]
            for field in state_required:
                if field not in info["state"]:
                    errors.append(f"state missing required field: {field}")

    return errors
