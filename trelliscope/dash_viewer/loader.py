"""
Load display configuration and data for Dash viewer.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd


class DisplayLoader:
    """
    Loads trelliscope display data from output directory.

    Reads displayInfo.json, cogData, and panel files for rendering
    in the Dash viewer.
    """

    def __init__(self, display_path: Path):
        """
        Initialize loader with display output path.

        Parameters
        ----------
        display_path : Path
            Path to display output directory (contains displayInfo.json or
            displays/ subdirectory)
        """
        self.display_path = Path(display_path)
        self._display_info: Optional[Dict[str, Any]] = None
        self._cog_data: Optional[pd.DataFrame] = None

    def load(self) -> Dict[str, Any]:
        """
        Load display configuration and data.

        Returns
        -------
        dict
            Dictionary with keys:
            - display_info: Display configuration from displayInfo.json
            - cog_data: DataFrame with panel metadata
            - panel_base_path: Path to panels directory
            - display_name: Name of the display

        Raises
        ------
        FileNotFoundError
            If displayInfo.json not found
        ValueError
            If display data is invalid
        """
        # Find displayInfo.json
        display_info_path = self._find_display_info()

        if not display_info_path.exists():
            raise FileNotFoundError(
                f"displayInfo.json not found in {self.display_path}"
            )

        # Load display configuration
        with open(display_info_path, 'r', encoding='utf-8') as f:
            self._display_info = json.load(f)

        # Extract cogData
        if 'cogData' not in self._display_info:
            raise ValueError("displayInfo.json missing 'cogData' field")

        self._cog_data = pd.DataFrame(self._display_info['cogData'])

        # Convert factor indices from 1-based to 0-based for Python
        self._convert_factor_indices()

        # Get panel base path
        panel_base_path = display_info_path.parent / "panels"

        # Add full panel paths to DataFrame
        self._add_panel_paths(panel_base_path)

        return {
            'display_info': self._display_info,
            'cog_data': self._cog_data,
            'panel_base_path': panel_base_path,
            'display_name': self._display_info.get('name', 'display')
        }

    def _find_display_info(self) -> Path:
        """
        Find displayInfo.json in display directory.

        Handles both single-display and multi-display structures:
        - {path}/displayInfo.json (single display)
        - {path}/displays/{name}/displayInfo.json (multi-display)

        Returns
        -------
        Path
            Path to displayInfo.json file
        """
        # Try direct path first
        direct_path = self.display_path / "displayInfo.json"
        if direct_path.exists():
            return direct_path

        # Try displays subdirectory
        displays_dir = self.display_path / "displays"
        if displays_dir.exists():
            # Find first display
            display_dirs = [d for d in displays_dir.iterdir() if d.is_dir()]
            if display_dirs:
                display_info = display_dirs[0] / "displayInfo.json"
                if display_info.exists():
                    return display_info

        # Try one level up (in case we're in displays/name/)
        parent_info = self.display_path / "displayInfo.json"
        if parent_info.exists():
            return parent_info

        raise FileNotFoundError(
            f"Could not find displayInfo.json in {self.display_path}"
        )

    def _convert_factor_indices(self):
        """
        Convert factor indices from 1-based (R-style) to 0-based (Python).

        The displayInfo.json uses 1-based factor indexing for compatibility
        with R. We need to convert to 0-based for Python pandas operations.
        """
        if self._display_info is None or self._cog_data is None:
            return

        # Get factor metas
        factor_metas = {
            meta['varname']: meta
            for meta in self._display_info.get('metas', [])
            if meta.get('type') == 'factor'
        }

        # Convert indices in DataFrame
        for varname, meta in factor_metas.items():
            if varname in self._cog_data.columns:
                # Convert from 1-based to 0-based
                self._cog_data[varname] = self._cog_data[varname].apply(
                    lambda x: int(x) - 1 if pd.notna(x) and isinstance(x, (int, float)) else x
                )

                # Map to level strings for easier filtering/display
                levels = meta.get('levels', [])
                if levels:
                    self._cog_data[f"{varname}_label"] = self._cog_data[varname].apply(
                        lambda x: levels[int(x)] if pd.notna(x) and 0 <= int(x) < len(levels) else None
                    )

    def _add_panel_paths(self, panel_base_path: Path):
        """
        Add full panel file paths to cogData DataFrame.

        Parameters
        ----------
        panel_base_path : Path
            Base directory containing panel files
        """
        if self._cog_data is None:
            return

        # Get panel column name
        panel_col = self._display_info.get('primarypanel', 'panel')

        if panel_col not in self._cog_data.columns:
            return

        # Add full paths (convert to strings for JSON serialization)
        self._cog_data['_panel_full_path'] = self._cog_data[panel_col].apply(
            lambda p: str(panel_base_path / Path(p).name) if pd.notna(p) else None
        )

        # Detect panel type from file extension
        self._cog_data['_panel_type'] = self._cog_data['_panel_full_path'].apply(
            lambda p: self._detect_panel_type(p) if p else None
        )

    @staticmethod
    def _detect_panel_type(panel_path) -> str:
        """
        Detect panel type from file extension.

        Parameters
        ----------
        panel_path : str or Path
            Path to panel file (string or Path object)

        Returns
        -------
        str
            "image" for PNG/JPEG/etc, "plotly" for HTML, "unknown" otherwise
        """
        if panel_path is None:
            return "unknown"

        # Convert to Path if it's a string
        if isinstance(panel_path, str):
            panel_path = Path(panel_path)

        ext = panel_path.suffix.lower()

        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
            return "image"
        elif ext in ['.html', '.htm']:
            return "plotly"
        else:
            return "unknown"

    def get_panel_meta(self, varname: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific variable.

        Parameters
        ----------
        varname : str
            Variable name

        Returns
        -------
        dict or None
            Metadata dictionary or None if not found
        """
        if self._display_info is None:
            return None

        for meta in self._display_info.get('metas', []):
            if meta.get('varname') == varname:
                return meta

        return None

    def get_filterable_metas(self) -> List[Dict[str, Any]]:
        """
        Get list of metadata variables that can be filtered.

        Returns
        -------
        list
            List of meta dictionaries for filterable variables
        """
        if self._display_info is None:
            return []

        # Exclude panel columns
        panel_col = self._display_info.get('primarypanel', 'panel')

        return [
            meta for meta in self._display_info.get('metas', [])
            if meta.get('varname') != panel_col and meta.get('type') != 'panel'
        ]

    def get_sortable_metas(self) -> List[Dict[str, Any]]:
        """
        Get list of metadata variables that can be sorted.

        Returns
        -------
        list
            List of meta dictionaries for sortable variables
        """
        # Same as filterable for now
        return self.get_filterable_metas()

    @property
    def display_info(self) -> Optional[Dict[str, Any]]:
        """Get loaded display info."""
        return self._display_info

    @property
    def cog_data(self) -> Optional[pd.DataFrame]:
        """Get loaded cognostics data."""
        return self._cog_data
