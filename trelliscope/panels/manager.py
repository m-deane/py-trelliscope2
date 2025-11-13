"""Panel manager for coordinating panel rendering adapters."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from trelliscope.panels import PanelRenderer
from trelliscope.panels.matplotlib_adapter import MatplotlibAdapter
from trelliscope.panels.plotly_adapter import PlotlyAdapter


class PanelManager:
    """Manager for detecting and rendering panels with multiple adapters.

    PanelManager coordinates multiple PanelRenderer adapters, automatically
    detecting which adapter can handle each panel object and delegating
    the save operation appropriately.

    The manager tries adapters in registration order (last registered first).
    This allows users to register custom adapters that take precedence over
    built-in ones.

    Example:
        >>> from trelliscope.panels.manager import PanelManager
        >>> import matplotlib.pyplot as plt
        >>>
        >>> manager = PanelManager()
        >>>
        >>> fig, ax = plt.subplots()
        >>> ax.plot([1, 2, 3])
        >>>
        >>> path = manager.save_panel(fig, Path('/tmp'), 'plot1')
        >>> print(path)
        /tmp/plot1.png
    """

    def __init__(self) -> None:
        """Initialize PanelManager with default adapters.

        Default adapters (in order):
        1. MatplotlibAdapter (PNG)
        2. PlotlyAdapter (HTML)
        """
        self.adapters: List[PanelRenderer] = [
            MatplotlibAdapter(),
            PlotlyAdapter(),
        ]

    def register_adapter(self, adapter: PanelRenderer, prepend: bool = True) -> None:
        """Register a new adapter.

        Args:
            adapter: PanelRenderer instance to register
            prepend: If True, add to beginning (higher priority). Default: True

        Example:
            >>> manager = PanelManager()
            >>> custom_adapter = MyCustomAdapter()
            >>> manager.register_adapter(custom_adapter)
        """
        if prepend:
            self.adapters.insert(0, adapter)
        else:
            self.adapters.append(adapter)

    def detect_adapter(self, obj: Any) -> Optional[PanelRenderer]:
        """Find the first adapter that can handle the object.

        Tries adapters in registration order (last registered first).

        Args:
            obj: Object to detect (figure, chart, callable, etc.)

        Returns:
            PanelRenderer if found, None otherwise

        Example:
            >>> manager = PanelManager()
            >>> adapter = manager.detect_adapter(matplotlib_fig)
            >>> print(adapter.__class__.__name__)
            MatplotlibAdapter
        """
        # Handle callables first
        if callable(obj):
            try:
                obj = obj()
            except Exception as e:
                raise ValueError(f"Failed to execute callable panel: {e}") from e

        # Try each adapter
        for adapter in self.adapters:
            if adapter.detect(obj):
                return adapter

        return None

    def save_panel(
        self, obj: Any, output_dir: Path, panel_id: str, **kwargs: Any
    ) -> Path:
        """Save panel using the appropriate adapter.

        This is the main entry point for panel rendering. It:
        1. Executes obj if it's a callable (lazy evaluation)
        2. Detects the appropriate adapter
        3. Saves the panel to output_dir/panel_id.{format}

        Args:
            obj: Panel object (figure, chart, callable, etc.)
            output_dir: Directory to save panel in
            panel_id: Identifier for panel (used as filename)
            **kwargs: Additional options passed to adapter.save()

        Returns:
            Path: Full path to saved panel file

        Raises:
            ValueError: If no adapter can handle the object
            Exception: If save operation fails

        Example:
            >>> manager = PanelManager()
            >>> path = manager.save_panel(
            ...     fig,
            ...     Path('/tmp/panels'),
            ...     'myplot',
            ...     dpi=150
            ... )
        """
        # Create output directory if needed
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Handle callables (lazy evaluation)
        original_obj = obj
        if callable(obj):
            try:
                obj = obj()
            except Exception as e:
                raise ValueError(
                    f"Failed to execute callable panel '{panel_id}': {e}"
                ) from e

        # Find appropriate adapter
        adapter = self.detect_adapter(obj)
        if adapter is None:
            # Provide helpful error message
            obj_type = type(original_obj).__name__
            supported_types = [
                "matplotlib.figure.Figure",
                "plotly.graph_objects.Figure",
                "callable returning one of the above",
            ]
            raise ValueError(
                f"No adapter found for panel '{panel_id}' of type '{obj_type}'. "
                f"Supported types: {', '.join(supported_types)}. "
                f"You may need to install additional visualization libraries "
                f"or register a custom adapter."
            )

        # Create base path for panel
        panel_path = output_dir / panel_id

        # Save panel using adapter
        try:
            saved_path = adapter.save(obj, panel_path, **kwargs)
            return saved_path
        except Exception as e:
            raise RuntimeError(f"Failed to save panel '{panel_id}': {e}") from e

    def get_panel_interface(self) -> Dict[str, Any]:
        """Get panelInterface configuration based on most common adapter.

        Returns:
            dict: panelInterface configuration

        Example:
            >>> manager = PanelManager()
            >>> interface = manager.get_panel_interface()
            >>> print(interface['type'])
            panel_local
        """
        # Use first adapter as default
        if not self.adapters:
            return {"type": "panel_local", "format": "png"}

        adapter = self.adapters[0]
        return {"type": adapter.get_interface_type(), "format": adapter.get_format()}
