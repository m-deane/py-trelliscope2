"""Matplotlib adapter for panel rendering."""

from pathlib import Path
from typing import Any

from trelliscope.panels import PanelRenderer


class MatplotlibAdapter(PanelRenderer):
    """Adapter for rendering matplotlib figures to image files.

    Supports PNG, JPEG, SVG, and PDF formats. Uses matplotlib's
    savefig() method with sensible defaults.

    Args:
        output_format: Output format ('png', 'jpeg', 'svg', 'pdf'). Default: 'png'
        dpi: Resolution in dots per inch. Default: 100
        bbox_inches: Bounding box mode. Default: 'tight'

    Example:
        >>> import matplotlib.pyplot as plt
        >>> from trelliscope.panels.matplotlib_adapter import MatplotlibAdapter
        >>>
        >>> fig, ax = plt.subplots()
        >>> ax.plot([1, 2, 3], [1, 4, 9])
        >>>
        >>> adapter = MatplotlibAdapter(format='png', dpi=150)
        >>> path = adapter.save(fig, Path('/tmp/myplot'))
        >>> print(path)
        /tmp/myplot.png
    """

    def __init__(
        self, output_format: str = "png", dpi: int = 100, bbox_inches: str = "tight"
    ):
        """Initialize MatplotlibAdapter.

        Args:
            output_format: Output format. Default: 'png'
            dpi: Resolution. Default: 100
            bbox_inches: Bounding box mode. Default: 'tight'
        """
        valid_formats = ["png", "jpeg", "jpg", "svg", "pdf"]
        if output_format not in valid_formats:
            raise ValueError(
                f"Invalid format '{output_format}'. " f"Valid formats: {valid_formats}"
            )

        self.format = output_format
        self.dpi = dpi
        self.bbox_inches = bbox_inches

    def detect(self, obj: Any) -> bool:
        """Detect matplotlib Figure objects.

        Args:
            obj: Object to check

        Returns:
            bool: True if obj is a matplotlib Figure
        """
        try:
            import matplotlib.figure

            return isinstance(obj, matplotlib.figure.Figure)
        except ImportError:
            return False

    def save(self, obj: Any, path: Path, **kwargs: Any) -> Path:
        """Save matplotlib figure to file.

        Args:
            obj: matplotlib Figure to save
            path: Base path for output (extension added automatically)
            **kwargs: Override default settings (dpi, format, bbox_inches)

        Returns:
            Path: Path to saved file with extension

        Raises:
            ValueError: If obj is not a matplotlib Figure
            Exception: If save operation fails
        """
        if not self.detect(obj):
            raise ValueError(f"Object is not a matplotlib Figure: {type(obj)}")

        # Get settings (kwargs override defaults)
        dpi = kwargs.get("dpi", self.dpi)
        file_format = kwargs.get("format", self.format)
        bbox_inches = kwargs.get("bbox_inches", self.bbox_inches)

        # Create output path with extension
        output_path = path.with_suffix(f".{file_format}")

        # Save figure
        obj.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches, format=file_format)

        return output_path

    def get_interface_type(self) -> str:
        """Return panelInterface type.

        Returns:
            str: 'panel_local' for image files
        """
        return "panel_local"

    def get_format(self) -> str:
        """Return file format.

        Returns:
            str: File extension (e.g., 'png')
        """
        return self.format
