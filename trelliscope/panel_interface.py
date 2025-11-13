"""
Panel interface configuration for different panel source types.

Defines how panels are loaded in the viewer:
- LocalPanelInterface: Panels loaded from local files (default)
- RESTPanelInterface: Panels loaded via REST API
- WebSocketPanelInterface: Panels streamed via WebSocket (future)
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PanelInterface:
    """Base class for panel interface configuration."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        raise NotImplementedError("Subclasses must implement to_dict()")


@dataclass
class LocalPanelInterface(PanelInterface):
    """
    Configuration for local file-based panels.

    Panels are pre-rendered to files and served from the local filesystem.
    This is the default panel interface.

    Parameters
    ----------
    format : str, default="png"
        Panel file format: "png", "jpg", "html", "svg"
    base : str, default="./panels"
        Base directory for panel files relative to display directory

    Examples
    --------
    >>> interface = LocalPanelInterface(format="png")
    >>> display.set_panel_interface(interface)
    """

    format: str = "png"
    base: str = "./panels"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to displayInfo.json panelInterface format."""
        return {
            "type": "file",
            "format": self.format,
            "base": self.base,
        }


@dataclass
class RESTPanelInterface(PanelInterface):
    """
    Configuration for REST API-based panels.

    Panels are served dynamically from a REST API endpoint. The viewer
    constructs panel URLs as: {base}/{panel_id}

    Parameters
    ----------
    base : str
        Base URL for panel API (e.g., "http://localhost:5001/api/panels/my_display")
    port : int, optional
        Server port number (for display purposes)
    api_key : str, optional
        API key for authenticated requests
    headers : dict, optional
        Additional HTTP headers to send with panel requests

    Examples
    --------
    >>> interface = RESTPanelInterface(
    ...     base="http://localhost:5001/api/panels/my_display"
    ... )
    >>> display.set_panel_interface(interface)

    >>> # With authentication
    >>> interface = RESTPanelInterface(
    ...     base="https://api.example.com/panels/display_123",
    ...     api_key="secret_key_123"
    ... )
    """

    base: str
    port: Optional[int] = None
    api_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

    def __post_init__(self) -> None:
        """Validate base URL."""
        if not self.base:
            raise ValueError("base URL cannot be empty")
        if not (self.base.startswith("http://") or self.base.startswith("https://")):
            raise ValueError(f"base must be a valid HTTP(S) URL, got: {self.base}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to displayInfo.json panelInterface format for REST panels."""
        # Build panel meta source configuration
        source = {
            "type": "REST",
            "url": self.base,
            "isLocal": self.base.startswith("http://localhost")
            or self.base.startswith("http://127.0.0.1"),
        }

        if self.port is not None:
            source["port"] = self.port

        if self.api_key is not None:
            source["apiKey"] = self.api_key

        if self.headers is not None:
            # Convert headers dict to string format expected by viewer
            # Format: "Header1: value1; Header2: value2"
            headers_str = "; ".join(f"{k}: {v}" for k, v in self.headers.items())
            source["headers"] = headers_str

        return source


@dataclass
class WebSocketPanelInterface(PanelInterface):
    """
    Configuration for WebSocket-based panels (future enhancement).

    Panels are streamed dynamically via WebSocket connection.

    Parameters
    ----------
    url : str
        WebSocket URL (e.g., "ws://localhost:8080/panels")

    Examples
    --------
    >>> interface = WebSocketPanelInterface(
    ...     url="ws://localhost:8080/panels"
    ... )
    """

    url: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to displayInfo.json panelInterface format."""
        return {
            "type": "localWebSocket",
            "url": self.url,
        }


def create_panel_interface(panel_type: str, **kwargs: Any) -> PanelInterface:
    """
    Factory function to create panel interfaces.

    Parameters
    ----------
    panel_type : str
        Interface type: "local", "rest", or "websocket"
    **kwargs
        Type-specific parameters

    Returns
    -------
    PanelInterface
        Configured panel interface instance

    Raises
    ------
    ValueError
        If panel_type is unknown

    Examples
    --------
    >>> # Create local interface
    >>> interface = create_panel_interface("local", format="png")

    >>> # Create REST interface
    >>> interface = create_panel_interface(
    ...     "rest",
    ...     base="http://localhost:5001/api/panels/display1"
    ... )
    """
    type_map = {
        "local": LocalPanelInterface,
        "rest": RESTPanelInterface,
        "websocket": WebSocketPanelInterface,
    }

    if panel_type not in type_map:
        raise ValueError(
            f"Unknown panel interface type '{panel_type}'. "
            f"Must be one of: {list(type_map.keys())}"
        )

    interface_class = type_map[panel_type]
    return interface_class(**kwargs)  # type: ignore[no-any-return]
