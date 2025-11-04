"""Plotly adapter for panel rendering."""

from pathlib import Path
from typing import Any

from trelliscope.panels import PanelRenderer


class PlotlyAdapter(PanelRenderer):
    """Adapter for rendering plotly figures to HTML or static images.

    Supports HTML (with CDN plotly.js), PNG, JPEG, SVG, and PDF formats.
    HTML is the default and recommended format for interactive plots.

    Static image export (PNG, JPEG, SVG, PDF) requires the kaleido
    package to be installed.

    Args:
        format: Output format ('html', 'png', 'jpeg', 'svg', 'pdf'). Default: 'html'
        include_plotlyjs: How to include plotly.js in HTML ('cdn', True, False). Default: 'cdn'
        width: Width in pixels for static exports. Default: None (use figure default)
        height: Height in pixels for static exports. Default: None (use figure default)

    Example:
        >>> import plotly.graph_objects as go
        >>> from trelliscope.panels.plotly_adapter import PlotlyAdapter
        >>>
        >>> fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[1, 4, 9])])
        >>>
        >>> adapter = PlotlyAdapter(format='html')
        >>> path = adapter.save(fig, Path('/tmp/myplot'))
        >>> print(path)
        /tmp/myplot.html
    """

    def __init__(
        self,
        format: str = "html",
        include_plotlyjs: str = "cdn",
        width: int = None,
        height: int = None
    ):
        """Initialize PlotlyAdapter.

        Args:
            format: Output format. Default: 'html'
            include_plotlyjs: Plotly.js inclusion mode. Default: 'cdn'
            width: Width for static exports. Default: None
            height: Height for static exports. Default: None
        """
        valid_formats = ["html", "png", "jpeg", "jpg", "svg", "pdf"]
        if format not in valid_formats:
            raise ValueError(
                f"Invalid format '{format}'. "
                f"Valid formats: {valid_formats}"
            )

        self.format = format
        self.include_plotlyjs = include_plotlyjs
        self.width = width
        self.height = height

    def detect(self, obj: Any) -> bool:
        """Detect plotly Figure objects.

        Detects both plotly.graph_objects.Figure and dict-like
        plotly specifications.

        Args:
            obj: Object to check

        Returns:
            bool: True if obj is a plotly Figure or dict spec
        """
        try:
            import plotly.graph_objects as go

            # Check for Figure instance
            if isinstance(obj, go.Figure):
                return True

            # Check for dict with plotly structure
            if isinstance(obj, dict) and ('data' in obj or 'layout' in obj):
                return True

            return False
        except ImportError:
            return False

    def save(self, obj: Any, path: Path, **kwargs) -> Path:
        """Save plotly figure to file.

        For HTML format, saves interactive plot with plotly.js from CDN.
        For static formats (PNG, JPEG, SVG, PDF), requires kaleido package.

        Args:
            obj: plotly Figure to save
            path: Base path for output (extension added automatically)
            **kwargs: Override default settings (format, width, height, include_plotlyjs)

        Returns:
            Path: Path to saved file with extension

        Raises:
            ValueError: If obj is not a plotly Figure
            ImportError: If kaleido not installed for static export
            Exception: If save operation fails
        """
        if not self.detect(obj):
            raise ValueError(
                f"Object is not a plotly Figure: {type(obj)}"
            )

        # Get settings (kwargs override defaults)
        format = kwargs.get("format", self.format)
        width = kwargs.get("width", self.width)
        height = kwargs.get("height", self.height)

        # Create output path with extension
        output_path = path.with_suffix(f".{format}")

        # Import plotly
        import plotly.io as pio

        # Save based on format
        if format == "html":
            include_plotlyjs = kwargs.get("include_plotlyjs", self.include_plotlyjs)
            pio.write_html(
                obj,
                output_path,
                include_plotlyjs=include_plotlyjs
            )
        else:
            # Static image export (requires kaleido)
            try:
                pio.write_image(
                    obj,
                    output_path,
                    format=format,
                    width=width,
                    height=height
                )
            except ValueError as e:
                if "kaleido" in str(e).lower():
                    raise ImportError(
                        f"Static image export requires kaleido package. "
                        f"Install with: pip install kaleido"
                    ) from e
                raise

        return output_path

    def get_interface_type(self) -> str:
        """Return panelInterface type.

        Returns:
            str: 'iframe' for HTML, 'panel_local' for images
        """
        if self.format == "html":
            return "iframe"
        return "panel_local"

    def get_format(self) -> str:
        """Return file format.

        Returns:
            str: File extension (e.g., 'html', 'png')
        """
        return self.format
