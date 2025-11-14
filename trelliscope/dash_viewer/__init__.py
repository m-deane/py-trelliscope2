"""
Plotly Dash interactive viewer for Trelliscope displays.

This module provides an interactive Python-based viewer that can be launched
from Jupyter notebooks or as a standalone web application.
"""

from pathlib import Path
from trelliscope.dash_viewer.app import DashViewer


def create_dash_app(display, mode='external', debug=False, force_write=True):
    """
    Create a Dash viewer app from a Display object.

    This is a convenience function that handles writing the display if needed
    and creating the DashViewer instance.

    Parameters
    ----------
    display : Display
        Trelliscope Display object to visualize. If not yet written,
        this function will call display.write() automatically.
    mode : str, default='external'
        Viewer mode: 'external' (opens browser) or 'inline' (for notebooks)
    debug : bool, default=False
        Enable Dash debug mode
    force_write : bool, default=True
        If True, force rewriting the display even if it already exists.
        Passed to display.write(force=force_write).

    Returns
    -------
    DashViewer
        DashViewer instance with .run() method ready to launch viewer

    Examples
    --------
    >>> from trelliscope import Display
    >>> from trelliscope.dash_viewer import create_dash_app
    >>>
    >>> # Create display - writing is automatic
    >>> display = (Display(df, name="my_display")
    ...     .set_panel_column("plot")
    ...     .infer_metas())
    >>>
    >>> # Create and run viewer (force_write=True by default)
    >>> app = create_dash_app(display)
    >>> app.run(port=8053)
    >>>
    >>> # Skip rewriting if display already exists
    >>> app = create_dash_app(display, force_write=False)
    >>> app.run(port=8053)
    """
    # Get the display path - check if already written
    if hasattr(display, '_output_path') and display._output_path and not force_write:
        # Display has been written, use the stored path
        display_path = display._output_path
    else:
        # Write the display first - this returns root_path
        root_path = display.write(force=force_write)
        # But we need the display output path, which is stored in _output_path
        display_path = display._output_path

    # Create and return DashViewer
    return DashViewer(display_path, mode=mode, debug=debug)


__all__ = ["DashViewer", "create_dash_app"]
