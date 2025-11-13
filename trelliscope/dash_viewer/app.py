"""
Main Dash application for interactive Trelliscope viewer.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import webbrowser
import threading
import time

import dash
from dash import html, dcc, Input, Output, State, ALL, MATCH, ctx
import dash_bootstrap_components as dbc

from trelliscope.dash_viewer.loader import DisplayLoader
from trelliscope.dash_viewer.state import DisplayState
from trelliscope.dash_viewer.components.filters import create_filter_panel
from trelliscope.dash_viewer.components.controls import create_control_bar, create_header
from trelliscope.dash_viewer.components.layout import create_panel_grid


class DashViewer:
    """
    Interactive Plotly Dash viewer for Trelliscope displays.

    Provides an interactive Python-based viewer that can be launched
    from Jupyter notebooks or as a standalone web application.
    """

    def __init__(
        self,
        display_path: Path,
        mode: str = "external",
        debug: bool = False
    ):
        """
        Initialize Dash viewer.

        Parameters
        ----------
        display_path : Path
            Path to display output directory (contains displayInfo.json)
        mode : str
            Display mode:
            - "external": Open in external browser (default)
            - "inline": Embed in Jupyter notebook
            - "jupyterlab": JupyterLab mode
        debug : bool
            Enable debug mode (default: False)
        """
        self.display_path = Path(display_path)
        self.mode = mode
        self.debug = debug

        # Load display data
        self.loader = DisplayLoader(self.display_path)
        self.display_data = self.loader.load()

        self.display_info = self.display_data['display_info']
        self.cog_data = self.display_data['cog_data']
        self.display_name = self.display_data['display_name']

        # Initialize state
        self.state = DisplayState(display_info=self.display_info)

        # App instance
        self.app: Optional[dash.Dash] = None

    def create_app(self) -> dash.Dash:
        """
        Create and configure Dash application.

        Returns
        -------
        dash.Dash
            Configured Dash application
        """
        # Create app with Bootstrap theme
        if self.mode in ["inline", "jupyterlab"]:
            try:
                from jupyter_dash import JupyterDash
                app = JupyterDash(
                    __name__,
                    external_stylesheets=[dbc.themes.BOOTSTRAP],
                    suppress_callback_exceptions=True
                )
            except ImportError:
                print("Warning: jupyter-dash not installed. Using standard Dash.")
                print("Install with: pip install jupyter-dash")
                app = dash.Dash(
                    __name__,
                    external_stylesheets=[dbc.themes.BOOTSTRAP],
                    suppress_callback_exceptions=True
                )
        else:
            app = dash.Dash(
                __name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True
            )

        # Create layout
        app.layout = self._create_layout()

        # Register callbacks
        self._register_callbacks(app)

        return app

    def _create_layout(self) -> html.Div:
        """Create main application layout."""
        # Get filterable metas
        filterable_metas = self.loader.get_filterable_metas()

        # Create initial panel grid
        filtered_data = self.state.filter_data(self.cog_data)
        sorted_data = self.state.sort_data(filtered_data)
        page_data = self.state.get_page_data(sorted_data)

        total_panels = len(filtered_data)
        total_pages = self.state.get_total_pages(total_panels)

        return html.Div(
            [
                # Store components for state
                dcc.Store(id='filtered-data-store', data=filtered_data.to_dict('records')),
                dcc.Store(id='current-page-store', data=self.state.current_page),

                # Header
                create_header(self.display_info),

                # Main container
                dbc.Row(
                    [
                        # Left sidebar: Filters
                        dbc.Col(
                            create_filter_panel(filterable_metas, self.cog_data),
                            width=2,
                            style={'padding': 0}
                        ),

                        # Right content: Controls + Panels
                        dbc.Col(
                            [
                                # Control bar
                                create_control_bar(
                                    display_name=self.display_name,
                                    total_panels=total_panels,
                                    current_page=self.state.current_page,
                                    total_pages=total_pages,
                                    ncol=self.state.ncol,
                                    nrow=self.state.nrow
                                ),

                                # Panel grid
                                html.Div(
                                    create_panel_grid(
                                        panel_data=page_data,
                                        ncol=self.state.ncol,
                                        nrow=self.state.nrow,
                                        active_labels=self.state.active_labels,
                                        display_info=self.display_info
                                    ),
                                    id='panel-grid-container'
                                )
                            ],
                            width=10,
                            style={'padding': 0}
                        )
                    ],
                    className='g-0',
                    style={'height': '100vh'}
                )
            ],
            style={'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'}
        )

    def _register_callbacks(self, app: dash.Dash):
        """Register all Dash callbacks."""

        # Callback: Update filtered data and panel grid when filters change
        @app.callback(
            [
                Output('filtered-data-store', 'data'),
                Output('panel-grid-container', 'children'),
                Output('panel-count', 'children'),
                Output('page-info', 'children'),
                Output('prev-page-btn', 'disabled'),
                Output('next-page-btn', 'disabled')
            ],
            [
                Input({'type': 'filter', 'varname': ALL}, 'value'),
                Input('clear-filters-btn', 'n_clicks'),
                Input('prev-page-btn', 'n_clicks'),
                Input('next-page-btn', 'n_clicks'),
                Input('ncol-select', 'value'),
                Input('nrow-select', 'value')
            ],
            [
                State({'type': 'filter', 'varname': ALL}, 'id'),
                State('current-page-store', 'data')
            ],
            prevent_initial_call=False
        )
        def update_display(
            filter_values, clear_clicks, prev_clicks, next_clicks,
            ncol, nrow,
            filter_ids, current_page
        ):
            # Determine what triggered the callback
            triggered_id = ctx.triggered_id

            # Update layout if changed
            if ncol != self.state.ncol or nrow != self.state.nrow:
                self.state.set_layout(ncol=ncol, nrow=nrow)

            # Handle pagination
            if triggered_id == 'prev-page-btn':
                self.state.prev_page()
            elif triggered_id == 'next-page-btn':
                filtered_data = self.state.filter_data(self.cog_data)
                total_pages = self.state.get_total_pages(len(filtered_data))
                self.state.next_page(total_pages)

            # Handle clear filters
            if triggered_id == 'clear-filters-btn':
                self.state.clear_filters()
            else:
                # Update filters from inputs
                for filter_id, value in zip(filter_ids, filter_values):
                    varname = filter_id['varname']
                    self.state.set_filter(varname, value)

            # Apply filters and sorts
            filtered_data = self.state.filter_data(self.cog_data)
            sorted_data = self.state.sort_data(filtered_data)

            # Get page data
            page_data = self.state.get_page_data(sorted_data)

            # Calculate totals
            total_panels = len(filtered_data)
            total_pages = self.state.get_total_pages(total_panels)

            # Calculate panel range
            panels_per_page = self.state.panels_per_page
            start_panel = (self.state.current_page - 1) * panels_per_page + 1
            end_panel = min(self.state.current_page * panels_per_page, total_panels)

            # Create panel grid
            panel_grid = create_panel_grid(
                panel_data=page_data,
                ncol=self.state.ncol,
                nrow=self.state.nrow,
                active_labels=self.state.active_labels,
                display_info=self.display_info
            )

            # Update panel count text
            panel_count_text = f"Showing {start_panel}-{end_panel} of {total_panels} panels"

            # Update page info
            page_info_text = f"Page {self.state.current_page} of {total_pages}" if total_pages > 0 else "No pages"

            # Determine button states
            prev_disabled = self.state.current_page <= 1
            next_disabled = self.state.current_page >= total_pages or total_pages == 0

            return (
                filtered_data.to_dict('records'),
                panel_grid,
                panel_count_text,
                page_info_text,
                prev_disabled,
                next_disabled
            )

    def run(self, port: int = 8050, debug: Optional[bool] = None):
        """
        Start Dash server.

        Parameters
        ----------
        port : int
            Port number (default: 8050)
        debug : bool, optional
            Enable debug mode (default: use instance setting)
        """
        if debug is None:
            debug = self.debug

        # Create app if not already created
        if self.app is None:
            self.app = self.create_app()

        # Run based on mode
        if self.mode == "inline":
            try:
                self.app.run_server(mode="inline", port=port, debug=debug)
            except AttributeError:
                print("Error: jupyter-dash not available. Falling back to external mode.")
                self._run_external(port, debug)

        elif self.mode == "jupyterlab":
            try:
                self.app.run_server(mode="jupyterlab", port=port, debug=debug)
            except AttributeError:
                print("Error: jupyter-dash not available. Falling back to external mode.")
                self._run_external(port, debug)

        else:  # external
            self._run_external(port, debug)

    def _run_external(self, port: int, debug: bool):
        """Run in external browser mode."""
        url = f"http://localhost:{port}"

        def open_browser():
            time.sleep(1.5)
            webbrowser.open(url)

        # Start browser in background thread
        threading.Thread(target=open_browser, daemon=True).start()

        print(f"🚀 Dash viewer starting on {url}")
        print(f"📊 Display: {self.display_name}")
        print(f"📈 Panels: {len(self.cog_data)}")
        print(f"\n✨ Opening browser...")

        self.app.run_server(port=port, debug=debug)

    def show(self, port: int = 8050):
        """
        Convenience method to run viewer.

        Equivalent to run() with default settings.

        Parameters
        ----------
        port : int
            Port number (default: 8050)
        """
        self.run(port=port)
