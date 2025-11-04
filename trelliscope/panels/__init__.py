"""Panel rendering system for trelliscope displays.

This module provides adapters for rendering panels from various
visualization libraries (matplotlib, plotly, altair) to disk formats
(PNG, HTML, SVG).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class PanelRenderer(ABC):
    """Base class for panel rendering adapters.

    PanelRenderer provides an adapter pattern interface for detecting
    and saving visualization objects from different libraries.

    Subclasses must implement:
    - detect(): Check if object is compatible
    - save(): Save object to file
    - get_interface_type(): Return panelInterface type
    - get_format(): Return file extension
    """

    @abstractmethod
    def detect(self, obj: Any) -> bool:
        """Check if this adapter can handle the given object.

        Args:
            obj: Object to check (figure, chart, etc.)

        Returns:
            bool: True if this adapter can handle the object

        Example:
            >>> adapter = MatplotlibAdapter()
            >>> adapter.detect(matplotlib_fig)
            True
            >>> adapter.detect(plotly_fig)
            False
        """
        pass

    @abstractmethod
    def save(self, obj: Any, path: Path, **kwargs) -> Path:
        """Save the object to a file.

        Args:
            obj: Object to save (figure, chart, etc.)
            path: Base path for output file (extension will be added)
            **kwargs: Additional format-specific options

        Returns:
            Path: Actual path to saved file (with extension)

        Raises:
            Exception: If saving fails

        Example:
            >>> adapter = MatplotlibAdapter()
            >>> path = adapter.save(fig, Path('/tmp/panel'))
            >>> print(path)
            /tmp/panel.png
        """
        pass

    @abstractmethod
    def get_interface_type(self) -> str:
        """Return the panelInterface type for this adapter.

        Returns:
            str: One of 'panel_local', 'panel_url', 'iframe'

        Example:
            >>> adapter = MatplotlibAdapter()
            >>> adapter.get_interface_type()
            'panel_local'
        """
        pass

    @abstractmethod
    def get_format(self) -> str:
        """Return the file format/extension for this adapter.

        Returns:
            str: File extension without dot (e.g., 'png', 'html')

        Example:
            >>> adapter = MatplotlibAdapter()
            >>> adapter.get_format()
            'png'
        """
        pass


__all__ = ["PanelRenderer"]
