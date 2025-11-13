"""
Views manager for persisting display views to disk.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ViewsManager:
    """
    Manages saving and loading views for a display.

    Views are stored in the displayInfo.json file under the "views" array.
    """

    def __init__(self, display_path: Path):
        """
        Initialize views manager.

        Parameters
        ----------
        display_path : Path
            Path to display directory (contains displayInfo.json)
        """
        self.display_path = Path(display_path)
        self.display_info_path = self._find_display_info()
        self._display_info: Optional[Dict[str, Any]] = None

    def _find_display_info(self) -> Path:
        """Find displayInfo.json path."""
        # Try direct path first
        direct_path = self.display_path / "displayInfo.json"
        if direct_path.exists():
            return direct_path

        # Try displays subdirectory
        displays_dir = self.display_path / "displays"
        if displays_dir.exists():
            # Look for first displayInfo.json in subdirectories
            for subdir in displays_dir.iterdir():
                if subdir.is_dir():
                    info_path = subdir / "displayInfo.json"
                    if info_path.exists():
                        return info_path

        return direct_path  # Return default even if doesn't exist

    def _load_display_info(self) -> Dict[str, Any]:
        """Load displayInfo.json."""
        if self._display_info is None:
            try:
                with open(self.display_info_path, 'r', encoding='utf-8') as f:
                    self._display_info = json.load(f)
            except FileNotFoundError:
                logger.error(f"displayInfo.json not found at {self.display_info_path}")
                self._display_info = {}
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing displayInfo.json: {e}")
                self._display_info = {}

        return self._display_info

    def _save_display_info(self, display_info: Dict[str, Any]):
        """Save displayInfo.json."""
        try:
            with open(self.display_info_path, 'w', encoding='utf-8') as f:
                json.dump(display_info, f, indent=2, ensure_ascii=False)
            self._display_info = display_info  # Update cache
        except Exception as e:
            logger.error(f"Error saving displayInfo.json: {e}")
            raise

    def get_views(self) -> List[Dict[str, Any]]:
        """
        Get all saved views.

        Returns
        -------
        list
            List of view dictionaries
        """
        display_info = self._load_display_info()
        return display_info.get('views', [])

    def save_view(self, view: Dict[str, Any]) -> bool:
        """
        Save a new view.

        Parameters
        ----------
        view : dict
            View configuration with 'name' and 'state' keys

        Returns
        -------
        bool
            True if saved successfully
        """
        try:
            display_info = self._load_display_info()

            # Initialize views array if not present
            if 'views' not in display_info:
                display_info['views'] = []

            # Check if view with same name exists
            views = display_info['views']
            existing_index = next(
                (i for i, v in enumerate(views) if v.get('name') == view.get('name')),
                None
            )

            if existing_index is not None:
                # Update existing view
                views[existing_index] = view
                logger.info(f"Updated existing view: {view.get('name')}")
            else:
                # Add new view
                views.append(view)
                logger.info(f"Added new view: {view.get('name')}")

            # Save back to disk
            self._save_display_info(display_info)
            return True

        except Exception as e:
            logger.error(f"Error saving view: {e}")
            return False

    def delete_view(self, index: int) -> bool:
        """
        Delete a view by index.

        Parameters
        ----------
        index : int
            Index of view to delete

        Returns
        -------
        bool
            True if deleted successfully
        """
        try:
            display_info = self._load_display_info()
            views = display_info.get('views', [])

            if 0 <= index < len(views):
                removed_view = views.pop(index)
                self._save_display_info(display_info)
                logger.info(f"Deleted view: {removed_view.get('name')}")
                return True
            else:
                logger.warning(f"Invalid view index: {index}")
                return False

        except Exception as e:
            logger.error(f"Error deleting view: {e}")
            return False

    def get_view(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific view by index.

        Parameters
        ----------
        index : int
            View index

        Returns
        -------
        dict or None
            View configuration or None if not found
        """
        views = self.get_views()
        if 0 <= index < len(views):
            return views[index]
        return None

    def clear_all_views(self) -> bool:
        """
        Delete all saved views.

        Returns
        -------
        bool
            True if cleared successfully
        """
        try:
            display_info = self._load_display_info()
            display_info['views'] = []
            self._save_display_info(display_info)
            logger.info("Cleared all views")
            return True

        except Exception as e:
            logger.error(f"Error clearing views: {e}")
            return False
