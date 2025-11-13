"""Development server for viewing trelliscope displays locally."""

import http.server
import os
import socketserver
import threading
from pathlib import Path
from typing import Any, Optional


class DisplayServer:
    """Simple HTTP server for viewing displays locally.

    This server allows you to view trelliscope displays in a web browser
    during development. It serves static files from the display directory
    using Python's built-in HTTP server.

    Parameters
    ----------
    display_dir : Path
        Path to the display directory to serve
    port : int, optional
        Port number for the server. Default: 8000

    Attributes
    ----------
    display_dir : Path
        The display directory being served
    port : int
        The server port
    httpd : socketserver.TCPServer or None
        The underlying HTTP server instance
    thread : threading.Thread or None
        Thread for non-blocking server mode

    Examples
    --------
    >>> server = DisplayServer(Path("output/my_display"), port=8000)
    >>> server.start(blocking=False)  # Run in background
    >>> # Do other work...
    >>> server.stop()  # Shutdown when done

    >>> # Or run in blocking mode:
    >>> server.start(blocking=True)  # Ctrl+C to stop
    """

    def __init__(self, display_dir: Path, port: int = 8000):
        """Initialize the display server.

        Parameters
        ----------
        display_dir : Path
            Path to the display directory to serve
        port : int, optional
            Port number for the server. Default: 8000
        """
        self.display_dir = Path(display_dir)
        self.port = port
        self.httpd: Optional[socketserver.TCPServer] = None
        self.thread: Optional[threading.Thread] = None
        self._original_dir: Optional[Path] = None

        if not self.display_dir.exists():
            raise ValueError(f"Display directory does not exist: {self.display_dir}")

    def start(self, blocking: bool = False) -> None:
        """Start the HTTP server.

        Parameters
        ----------
        blocking : bool, optional
            If True, block until server is stopped (Ctrl+C).
            If False, run server in background thread. Default: False

        Raises
        ------
        RuntimeError
            If server is already running
        OSError
            If port is already in use

        Examples
        --------
        >>> server = DisplayServer(Path("output/my_display"))
        >>> server.start(blocking=False)  # Non-blocking
        >>> print("Server running in background")
        >>> server.stop()

        >>> server.start(blocking=True)  # Blocking - Ctrl+C to stop
        """
        if self.httpd is not None:
            raise RuntimeError("Server is already running")

        # Save current directory and change to parent of display dir
        try:
            self._original_dir = Path.cwd()
        except (FileNotFoundError, OSError):
            # Current directory may not exist (e.g., temp directory was deleted)
            # Default to display's parent directory
            self._original_dir = self.display_dir.parent

        os.chdir(self.display_dir.parent)

        # Create server with simple file handler
        handler = http.server.SimpleHTTPRequestHandler

        try:
            self.httpd = socketserver.TCPServer(("localhost", self.port), handler)
        except OSError as e:
            # Restore directory if server creation fails
            os.chdir(self._original_dir)
            raise OSError(f"Cannot start server on port {self.port}: {e}") from e

        if blocking:
            # Run in current thread (blocks until Ctrl+C)
            print(f"Serving at http://localhost:{self.port}")
            print("Press Ctrl+C to stop")
            try:
                self.httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                self.stop()
        else:
            # Run in background thread (non-blocking)
            self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        """Stop the HTTP server and cleanup.

        This method shuts down the server and restores the original
        working directory.

        Examples
        --------
        >>> server = DisplayServer(Path("output/my_display"))
        >>> server.start(blocking=False)
        >>> # ... do work ...
        >>> server.stop()
        """
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None

        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None

        # Restore original directory
        if self._original_dir:
            os.chdir(self._original_dir)
            self._original_dir = None

    def is_running(self) -> bool:
        """Check if server is currently running.

        Returns
        -------
        bool
            True if server is running, False otherwise

        Examples
        --------
        >>> server = DisplayServer(Path("output/my_display"))
        >>> server.is_running()
        False
        >>> server.start(blocking=False)
        >>> server.is_running()
        True
        >>> server.stop()
        >>> server.is_running()
        False
        """
        return self.httpd is not None

    def get_url(self) -> str:
        """Get the server URL.

        Returns
        -------
        str
            The base URL where the server is accessible

        Examples
        --------
        >>> server = DisplayServer(Path("output/my_display"))
        >>> server.get_url()
        'http://localhost:8000'
        """
        return f"http://localhost:{self.port}"

    def __enter__(self) -> "DisplayServer":
        """Context manager entry."""
        self.start(blocking=False)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()

    def __repr__(self) -> str:
        """String representation."""
        status = "running" if self.is_running() else "stopped"
        return (
            f"DisplayServer(dir={self.display_dir.name}, "
            f"port={self.port}, status={status})"
        )
