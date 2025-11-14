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
from trelliscope.dash_viewer.components.sorts import create_sort_panel, update_sort_panel_state
from trelliscope.dash_viewer.components.controls import create_control_bar, create_header
from trelliscope.dash_viewer.components.layout import create_panel_grid
from trelliscope.dash_viewer.components.views import create_views_panel, update_views_panel_state
from trelliscope.dash_viewer.components.search import create_search_panel, search_dataframe, get_searchable_columns
from trelliscope.dash_viewer.components.panel_detail import create_panel_detail_modal
from trelliscope.dash_viewer.components.layout_controls import create_layout_controls, get_layout_from_state
from trelliscope.dash_viewer.components.label_config import create_label_config_panel, get_labelable_metas
from trelliscope.dash_viewer.components.keyboard import (
    create_keyboard_help_modal, 
    create_keyboard_help_button,
    create_keyboard_listener,
    get_keyboard_action
)
from trelliscope.dash_viewer.components.export import create_export_panel, prepare_csv_export, prepare_view_export, generate_export_filename
from trelliscope.dash_viewer.components.notifications import create_toast_container, create_success_toast, create_error_toast, create_info_toast
from trelliscope.dash_viewer.components.help import create_help_modal, create_help_button
from trelliscope.dash_viewer.views_manager import ViewsManager


def _convert_paths_to_strings(data_dict):
    """
    Convert any Path objects in a dictionary to strings for JSON serialization.
    
    Parameters
    ----------
    data_dict : list of dict
        List of dictionaries (records from DataFrame.to_dict('records'))
    
    Returns
    -------
    list of dict
        Same structure with Path objects converted to strings
    """
    if isinstance(data_dict, list):
        for record in data_dict:
            if isinstance(record, dict):
                for key, value in record.items():
                    if isinstance(value, Path):
                        record[key] = str(value)
    return data_dict


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

        # Initialize views manager
        self.views_manager = ViewsManager(self.display_path)

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

        # Register callbacks FIRST (before setting layout)
        # This ensures callbacks are available when layout is validated
        self._register_callbacks(app)
        
        # Create layout AFTER callbacks are registered
        app.layout = self._create_layout()

        return app

    def _create_layout(self) -> html.Div:
        """Create main application layout."""
        # Get filterable and sortable metas
        filterable_metas = self.loader.get_filterable_metas()
        sortable_metas = self.loader.get_sortable_metas()

        # Create initial panel grid
        filtered_data = self.state.filter_data(self.cog_data)
        sorted_data = self.state.sort_data(filtered_data)
        page_data = self.state.get_page_data(sorted_data)

        total_panels = len(filtered_data)
        total_pages = self.state.get_total_pages(total_panels)

        # Convert DataFrame to dict, ensuring Path objects are converted to strings
        filtered_data_dict = _convert_paths_to_strings(filtered_data.to_dict('records'))
        
        return html.Div(
            [
                # Store components for state
                dcc.Store(id='filtered-data-store', data=filtered_data_dict),
                dcc.Store(id='current-page-store', data=self.state.current_page),
                dcc.Store(id='active-sorts-store', data=self.state.active_sorts),
                dcc.Store(id='current-panel-index', storage_type='memory'),

                # Header
                create_header(self.display_info),

                # Main container
                dbc.Row(
                    [
                        # Left sidebar: Search + Layout + Labels + Filters + Sorts + Views
                        dbc.Col(
                            html.Div(
                                [
                                    create_search_panel(),
                                    create_layout_controls(),
                                    create_label_config_panel(
                                        self.display_info.get('metas', []),
                                        self.state.active_labels
                                    ),
                                    create_filter_panel(filterable_metas, self.cog_data),
                                    create_sort_panel(sortable_metas, self.state.active_sorts),
                                    create_views_panel(self.views_manager.get_views()),
                                    create_export_panel()
                                ],
                                style={
                                    'height': '100vh',
                                    'overflowY': 'auto',
                                    'backgroundColor': '#f8f9fa',
                                    'borderRight': '1px solid #dee2e6'
                                }
                            ),
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

                                # Panel grid with loading state
                                dcc.Loading(
                                    id='panel-grid-loading',
                                    type='default',
                                    children=html.Div(
                                        create_panel_grid(
                                            panel_data=page_data,
                                            ncol=self.state.ncol,
                                            nrow=self.state.nrow,
                                            active_labels=self.state.active_labels,
                                            display_info=self.display_info
                                        ),
                                        id='panel-grid-container'
                                    )
                                )
                            ],
                            width=10,
                            style={'padding': 0}
                        )
                    ],
                    className='g-0',
                    style={'height': '100vh'}
                ),

                # Panel detail modal
                create_panel_detail_modal(),

                # Help modal
                create_help_modal(),

                # Keyboard shortcuts modal
                create_keyboard_help_modal(),

                # Keyboard event listener
                create_keyboard_listener(),

                # Toast notifications container
                create_toast_container()
            ],
            style={'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'}
        )

    def _register_callbacks(self, app: dash.Dash):
        """Register all Dash callbacks."""

        # Callback: Update filtered data and panel grid when filters, search, or sorts change
        @app.callback(
            [
                Output('filtered-data-store', 'data'),
                Output('panel-grid-container', 'children'),
                Output('panel-count', 'children'),
                Output('page-info', 'children'),
                Output('prev-page-btn', 'disabled'),
                Output('next-page-btn', 'disabled'),
                Output('active-sorts-list', 'children'),
                Output('clear-sorts-btn', 'disabled'),
                Output('search-results-summary', 'children'),
                Output('current-page-store', 'data')
            ],
            [
                Input({'type': 'filter', 'varname': ALL}, 'value'),
                Input('clear-filters-btn', 'n_clicks'),
                Input('global-search-input', 'value'),
                Input('clear-search-btn', 'n_clicks'),
                Input('prev-page-btn', 'n_clicks'),
                Input('next-page-btn', 'n_clicks'),
                Input('ncol-select', 'value'),
                Input('nrow-select', 'value'),
                Input('add-sort-select', 'value'),
                Input({'type': 'sort-asc', 'varname': ALL}, 'n_clicks'),
                Input({'type': 'sort-desc', 'varname': ALL}, 'n_clicks'),
                Input({'type': 'sort-remove', 'varname': ALL}, 'n_clicks'),
                Input('clear-sorts-btn', 'n_clicks')
            ],
            [
                State({'type': 'filter', 'varname': ALL}, 'id'),
                State({'type': 'sort-asc', 'varname': ALL}, 'id'),
                State({'type': 'sort-desc', 'varname': ALL}, 'id'),
                State({'type': 'sort-remove', 'varname': ALL}, 'id'),
                State('current-page-store', 'data')
            ],
            prevent_initial_call=False
        )
        def update_display(
            filter_values, clear_filters_clicks,
            search_query, clear_search_clicks,
            prev_clicks, next_clicks,
            ncol, nrow,
            add_sort_value,
            sort_asc_clicks, sort_desc_clicks, sort_remove_clicks,
            clear_sorts_clicks,
            filter_ids, sort_asc_ids, sort_desc_ids, sort_remove_ids,
            current_page
        ):
            # Determine what triggered the callback
            triggered_id = ctx.triggered_id if ctx.triggered_id else None
            
            # Debug logging
            if self.debug:
                print(f"[DEBUG] ===== Callback triggered =====")
                print(f"[DEBUG] Triggered ID: {triggered_id}")
                print(f"[DEBUG] Triggered prop: {ctx.triggered[0]['prop_id'] if ctx.triggered else 'None'}")
                print(f"[DEBUG] Current page from state: {self.state.current_page}, from store: {current_page}")
                print(f"[DEBUG] Input values - prev_clicks: {prev_clicks}, next_clicks: {next_clicks}")

            # Handle pagination FIRST (before syncing from store)
            # This ensures pagination updates take precedence
            if triggered_id == 'prev-page-btn':
                self.state.prev_page()
                if self.debug:
                    print(f"[DEBUG] Previous page clicked. New page: {self.state.current_page}")
            elif triggered_id == 'next-page-btn':
                # Calculate total pages before updating (need filtered data)
                filtered_data_temp = self.state.filter_data(self.cog_data)
                total_pages = self.state.get_total_pages(len(filtered_data_temp))
                self.state.next_page(total_pages)
                if self.debug:
                    print(f"[DEBUG] Next page clicked. New page: {self.state.current_page}, Total pages: {total_pages}")
            
            # Sync current_page from store if it's different (handles initial load)
            # BUT: Don't sync if we just handled pagination (we want to use the updated state value)
            if current_page is not None and current_page != self.state.current_page:
                if triggered_id not in ['prev-page-btn', 'next-page-btn']:
                    self.state.current_page = current_page
                    if self.debug:
                        print(f"[DEBUG] Synced page from store: {current_page}")

            # Update layout if changed
            if ncol != self.state.ncol or nrow != self.state.nrow:
                self.state.set_layout(ncol=ncol, nrow=nrow)

            # Handle clear filters
            if triggered_id == 'clear-filters-btn':
                self.state.clear_filters()
            elif triggered_id not in ['prev-page-btn', 'next-page-btn']:
                # Update filters from inputs (but NOT if pagination was triggered)
                # set_filter() resets page to 1, which would override pagination
                for filter_id, value in zip(filter_ids, filter_values):
                    varname = filter_id['varname']
                    self.state.set_filter(varname, value)

            # Handle clear search
            if triggered_id == 'clear-search-btn':
                search_query = None

            # Handle sorting actions
            if triggered_id == 'add-sort-select' and add_sort_value:
                # Add new sort (ascending by default)
                self.state.set_sort(add_sort_value, 'asc')
            elif triggered_id == 'clear-sorts-btn':
                # Clear all sorts
                self.state.clear_sorts()
            elif isinstance(triggered_id, dict):
                # Handle sort button clicks
                if triggered_id['type'] == 'sort-asc':
                    self.state.set_sort(triggered_id['varname'], 'asc')
                elif triggered_id['type'] == 'sort-desc':
                    self.state.set_sort(triggered_id['varname'], 'desc')
                elif triggered_id['type'] == 'sort-remove':
                    self.state.remove_sort(triggered_id['varname'])

            # Apply filters
            filtered_data = self.state.filter_data(self.cog_data)

            # Apply search (on top of filters)
            searchable_cols = get_searchable_columns(self.display_info)
            searched_data, match_count, total_before_search = search_dataframe(
                filtered_data,
                search_query if search_query else "",
                searchable_cols
            )

            # Format search summary
            from trelliscope.dash_viewer.components.search import format_search_summary
            search_summary = format_search_summary(match_count, total_before_search, search_query if search_query else "")

            # Apply sorts
            sorted_data = self.state.sort_data(searched_data)

            # Get page data
            page_data = self.state.get_page_data(sorted_data)

            # Calculate totals
            total_panels = len(searched_data)
            total_pages = self.state.get_total_pages(total_panels)

            # Calculate panel range
            panels_per_page = self.state.panels_per_page
            start_panel = (self.state.current_page - 1) * panels_per_page + 1
            end_panel = min(self.state.current_page * panels_per_page, total_panels)

            # Debug pagination
            if self.debug:
                print(f"[DEBUG] Pagination state:")
                print(f"  Current page: {self.state.current_page}")
                print(f"  Total pages: {total_pages}")
                print(f"  Total panels: {total_panels}")
                print(f"  Panels per page: {panels_per_page}")
                print(f"  Page data length: {len(page_data)}")
                print(f"  Panel range: {start_panel}-{end_panel}")

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

            # Update sort panel
            sortable_metas = self.loader.get_sortable_metas()
            active_sorts_list, clear_sorts_disabled = update_sort_panel_state(
                sortable_metas,
                self.state.active_sorts
            )

            return (
                _convert_paths_to_strings(searched_data.to_dict('records')),
                panel_grid,
                panel_count_text,
                page_info_text,
                prev_disabled,
                next_disabled,
                active_sorts_list,
                clear_sorts_disabled,
                search_summary,
                self.state.current_page  # Update current page store
            )

        # Callback: Save current view
        @app.callback(
            [
                Output('saved-views-list', 'children'),
                Output('load-view-select', 'options'),
                Output('save-view-name', 'value')
            ],
            [Input('save-view-btn', 'n_clicks')],
            [
                State('save-view-name', 'value'),
                State('filtered-data-store', 'data'),
                State('current-page-store', 'data')
            ],
            prevent_initial_call=True
        )
        def save_view(n_clicks, view_name, filtered_data, current_page):
            """Save current display state as a named view."""
            if not n_clicks or not view_name:
                raise dash.exceptions.PreventUpdate

            # Create view from current state
            view = self.state.save_view(view_name)

            # Save to disk
            success = self.views_manager.save_view(view)

            if success:
                # Update views list
                views = self.views_manager.get_views()
                view_items, view_options = update_views_panel_state(views)
                return view_items, view_options, ""  # Clear input
            else:
                raise dash.exceptions.PreventUpdate

        # Callback: Load view from dropdown
        @app.callback(
            [
                Output({'type': 'filter', 'varname': ALL}, 'value'),
                Output('ncol-select', 'value', allow_duplicate=True),
                Output('nrow-select', 'value', allow_duplicate=True),
                Output('add-sort-select', 'value')
            ],
            [Input('load-view-select', 'value')],
            [State({'type': 'filter', 'varname': ALL}, 'id')],
            prevent_initial_call=True
        )
        def load_view_from_dropdown(view_index, filter_ids):
            """Load a saved view from dropdown selection."""
            if view_index is None:
                raise dash.exceptions.PreventUpdate

            # Get view
            view = self.views_manager.get_view(int(view_index))
            if not view:
                raise dash.exceptions.PreventUpdate

            # Load into state
            self.state.load_view(view)

            # Prepare filter values
            filter_values = []
            for filter_id in filter_ids:
                varname = filter_id['varname']
                filter_val = self.state.active_filters.get(varname)
                filter_values.append(filter_val)

            return (
                filter_values,
                self.state.ncol,
                self.state.nrow,
                None  # Clear sort selector
            )

        # Callback: Load view from button in list
        @app.callback(
            [
                Output({'type': 'filter', 'varname': ALL}, 'value', allow_duplicate=True),
                Output('ncol-select', 'value', allow_duplicate=True),
                Output('nrow-select', 'value', allow_duplicate=True)
            ],
            [Input({'type': 'load-view-btn', 'index': ALL}, 'n_clicks')],
            [State({'type': 'filter', 'varname': ALL}, 'id')],
            prevent_initial_call=True
        )
        def load_view_from_button(n_clicks_list, filter_ids):
            """Load view when clicking load button in views list."""
            if not any(n_clicks_list) or not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            # Get which button was clicked
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if not triggered_id:
                raise dash.exceptions.PreventUpdate

            import json
            button_id = json.loads(triggered_id)
            view_index = button_id['index']

            # Get view
            view = self.views_manager.get_view(view_index)
            if not view:
                raise dash.exceptions.PreventUpdate

            # Load into state
            self.state.load_view(view)

            # Prepare filter values
            filter_values = []
            for filter_id in filter_ids:
                varname = filter_id['varname']
                filter_val = self.state.active_filters.get(varname)
                filter_values.append(filter_val)

            return (
                filter_values,
                self.state.ncol,
                self.state.nrow
            )

        # Callback: Delete view
        @app.callback(
            [
                Output('saved-views-list', 'children', allow_duplicate=True),
                Output('load-view-select', 'options', allow_duplicate=True)
            ],
            [Input({'type': 'delete-view-btn', 'index': ALL}, 'n_clicks')],
            prevent_initial_call=True
        )
        def delete_view(n_clicks_list):
            """Delete a saved view."""
            if not any(n_clicks_list) or not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            # Get which button was clicked
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if not triggered_id:
                raise dash.exceptions.PreventUpdate

            import json
            button_id = json.loads(triggered_id)
            view_index = button_id['index']

            # Delete from disk
            success = self.views_manager.delete_view(view_index)

            if success:
                # Update views list
                views = self.views_manager.get_views()
                view_items, view_options = update_views_panel_state(views)
                return view_items, view_options
            else:
                raise dash.exceptions.PreventUpdate

        # Callback: Toggle search info
        @app.callback(
            Output('search-info-collapse', 'is_open'),
            [Input('search-info-btn', 'n_clicks')],
            [State('search-info-collapse', 'is_open')],
            prevent_initial_call=True
        )
        def toggle_search_info(n_clicks, is_open):
            """Toggle search info panel."""
            if n_clicks:
                return not is_open
            return is_open

        # Callback: Clear search on button click
        @app.callback(
            Output('global-search-input', 'value'),
            [Input('clear-search-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def clear_search_input(n_clicks):
            """Clear search input."""
            if n_clicks:
                return ""
            raise dash.exceptions.PreventUpdate

        # Callback: Open panel detail modal
        @app.callback(
            [
                Output('panel-detail-modal', 'is_open'),
                Output('panel-detail-title', 'children'),
                Output('panel-detail-content', 'children'),
                Output('panel-detail-metadata', 'children'),
                Output('panel-detail-prev', 'disabled'),
                Output('panel-detail-next', 'disabled'),
                Output('current-panel-index', 'data')
            ],
            [
                Input({'type': 'panel-item', 'index': ALL}, 'n_clicks'),
                Input('panel-detail-close', 'n_clicks'),
                Input('panel-detail-close-footer', 'n_clicks'),
                Input('panel-detail-prev', 'n_clicks'),
                Input('panel-detail-next', 'n_clicks')
            ],
            [
                State('current-panel-index', 'data'),
                State('filtered-data-store', 'data'),
                State('panel-detail-modal', 'is_open')
            ],
            prevent_initial_call=True
        )
        def handle_panel_modal(
            panel_clicks, close_clicks, close_footer_clicks, prev_clicks, next_clicks,
            current_index, filtered_data, is_open
        ):
            """Handle panel detail modal interactions."""
            from trelliscope.dash_viewer.components.panel_detail import (
                format_panel_content,
                format_metadata_table,
                get_panel_navigation_info
            )
            import pandas as pd

            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            triggered_id = ctx.triggered_id

            # Close modal
            if triggered_id in ['panel-detail-close', 'panel-detail-close-footer']:
                return False, "", "", "", True, True, None

            # Convert filtered data to DataFrame
            if not filtered_data:
                raise dash.exceptions.PreventUpdate

            df = pd.DataFrame(filtered_data)
            total_panels = len(df)

            if total_panels == 0:
                raise dash.exceptions.PreventUpdate

            # Determine panel index
            panel_index = None

            if isinstance(triggered_id, dict) and triggered_id.get('type') == 'panel-item':
                # Panel was clicked - verify an actual click occurred
                # panel_clicks is a list matching ALL panel items in order
                # Check if any panel actually has n_clicks > 0
                if not panel_clicks or not any(clicks and clicks > 0 for clicks in panel_clicks):
                    # No actual click detected - this might be a layout update
                    raise dash.exceptions.PreventUpdate
                
                # Find which panel was clicked
                clicked_index = triggered_id['index']
                # Find this index in filtered data
                panel_indices = df.index.tolist()
                if clicked_index in panel_indices:
                    panel_index = df.index.get_loc(clicked_index)
                else:
                    # Index not found, try to find by position
                    # The triggered_id['index'] should match a DataFrame index
                    # If not found, prevent update
                    raise dash.exceptions.PreventUpdate

            elif triggered_id == 'panel-detail-prev' and current_index is not None:
                # Navigate to previous
                panel_index = max(0, current_index - 1)

            elif triggered_id == 'panel-detail-next' and current_index is not None:
                # Navigate to next
                panel_index = min(total_panels - 1, current_index + 1)

            elif current_index is not None:
                panel_index = current_index
            else:
                panel_index = 0

            # Get panel data
            panel_row = df.iloc[panel_index]

            # Get panel path and type
            panel_path = panel_row.get('_panel_full_path')
            panel_type = panel_row.get('_panel_type', 'unknown')

            if not panel_path:
                return False, "", "Panel not available", "", True, True, None

            # Format panel content
            from pathlib import Path
            panel_content = format_panel_content(Path(panel_path), panel_type)

            # Format metadata
            metadata_table = format_metadata_table(panel_row.to_dict(), self.display_info)

            # Get navigation info
            title, prev_disabled, next_disabled = get_panel_navigation_info(
                panel_index, total_panels
            )

            return (
                True,  # is_open
                title,
                panel_content,
                metadata_table,
                prev_disabled,
                next_disabled,
                panel_index  # Store current index
            )

        # Layout Controls Callbacks

        # Sync ncol slider and input
        @app.callback(
            [Output('layout-ncol-slider', 'value'),
             Output('layout-ncol-input', 'value')],
            [Input('layout-ncol-slider', 'value'),
             Input('layout-ncol-input', 'value')],
            prevent_initial_call=True
        )
        def sync_ncol(slider_val, input_val):
            """Sync ncol slider and input."""
            if ctx.triggered_id == 'layout-ncol-slider':
                return slider_val, slider_val
            else:
                # Constrain input value
                val = max(1, min(10, input_val if input_val else 1))
                return val, val

        # Sync nrow slider and input
        @app.callback(
            [Output('layout-nrow-slider', 'value'),
             Output('layout-nrow-input', 'value')],
            [Input('layout-nrow-slider', 'value'),
             Input('layout-nrow-input', 'value')],
            prevent_initial_call=True
        )
        def sync_nrow(slider_val, input_val):
            """Sync nrow slider and input."""
            if ctx.triggered_id == 'layout-nrow-slider':
                return slider_val, slider_val
            else:
                # Constrain input value
                val = max(1, min(10, input_val if input_val else 1))
                return val, val

        # Update panels per page display
        @app.callback(
            Output('layout-panels-per-page', 'children'),
            [Input('layout-ncol-slider', 'value'),
             Input('layout-nrow-slider', 'value')]
        )
        def update_panels_per_page(ncol, nrow):
            """Update panels per page display."""
            panels_per_page = (ncol or 1) * (nrow or 1)
            return f"Panels per page: {panels_per_page}"

        # Reset layout to defaults
        @app.callback(
            [Output('layout-ncol-slider', 'value', allow_duplicate=True),
             Output('layout-nrow-slider', 'value', allow_duplicate=True),
             Output('layout-arrangement', 'value')],
            [Input('reset-layout-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def reset_layout(n_clicks):
            """Reset layout to default values."""
            if n_clicks:
                # Get defaults from display info
                layout = get_layout_from_state(self.display_info)
                return layout['ncol'], layout['nrow'], layout['arrangement']
            raise dash.exceptions.PreventUpdate

        # Apply layout changes to main controls
        @app.callback(
            [Output('ncol-select', 'value', allow_duplicate=True),
             Output('nrow-select', 'value', allow_duplicate=True)],
            [Input('apply-layout-btn', 'n_clicks')],
            [State('layout-ncol-slider', 'value'),
             State('layout-nrow-slider', 'value'),
             State('layout-arrangement', 'value')],
            prevent_initial_call=True
        )
        def apply_layout(n_clicks, ncol, nrow, arrangement):
            """Apply layout changes from sidebar to main display."""
            if n_clicks:
                # Update DisplayState arrangement if changed
                if arrangement != self.state.arrangement:
                    self.state.arrangement = arrangement
                # Return new values to trigger main callback
                return ncol, nrow
            raise dash.exceptions.PreventUpdate

        # Label Configuration Callbacks

        # Toggle label info collapse
        @app.callback(
            Output('label-info-collapse', 'is_open'),
            [Input('label-info-btn', 'n_clicks')],
            [State('label-info-collapse', 'is_open')],
            prevent_initial_call=True
        )
        def toggle_label_info(n_clicks, is_open):
            """Toggle label info collapse."""
            if n_clicks:
                return not is_open
            raise dash.exceptions.PreventUpdate

        # Select all labels
        @app.callback(
            Output('label-checklist', 'value'),
            [Input('label-select-all-btn', 'n_clicks'),
             Input('label-clear-all-btn', 'n_clicks')],
            [State('label-checklist', 'options')],
            prevent_initial_call=True
        )
        def handle_label_select_clear(select_clicks, clear_clicks, options):
            """Handle select all / clear all buttons."""
            if ctx.triggered_id == 'label-select-all-btn':
                # Select all
                return [opt['value'] for opt in options]
            elif ctx.triggered_id == 'label-clear-all-btn':
                # Clear all
                return []
            raise dash.exceptions.PreventUpdate

        # Update active labels in state when checklist changes
        @app.callback(
            Output('panel-grid-container', 'children', allow_duplicate=True),
            [Input('label-checklist', 'value')],
            [State('filtered-data-store', 'data'),
             State('ncol-select', 'value'),
             State('nrow-select', 'value')],
            prevent_initial_call=True
        )
        def update_labels(selected_labels, filtered_data, ncol, nrow):
            """Update labels and re-render grid."""
            if selected_labels is None:
                selected_labels = []

            # Update state
            self.state.active_labels = selected_labels

            # Re-render grid with new labels
            import pandas as pd
            df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()

            if df.empty:
                return html.Div("No panels to display", className="text-center mt-5")

            # Apply pagination
            page_data = self.state.get_page_data(df)

            return create_panel_grid(
                page_data,
                ncol or self.state.ncol,
                nrow or self.state.nrow,
                selected_labels,
                self.display_info
            )

        # Help Modal Callbacks

        # Open/close help modal
        @app.callback(
            Output('help-modal', 'is_open'),
            [Input('show-help-btn', 'n_clicks'),
             Input('help-modal-close', 'n_clicks'),
             Input('quick-start-help-btn', 'n_clicks')],
            [State('help-modal', 'is_open')],
            prevent_initial_call=True
        )
        def toggle_help_modal(show_clicks, close_clicks, quickstart_clicks, is_open):
            """Toggle help modal."""
            if ctx.triggered_id in ['show-help-btn', 'quick-start-help-btn']:
                return True
            elif ctx.triggered_id == 'help-modal-close':
                return False
            return is_open

        # Open keyboard help from help modal
        @app.callback(
            [Output('keyboard-help-modal', 'is_open', allow_duplicate=True),
             Output('help-modal', 'is_open', allow_duplicate=True)],
            [Input('help-show-shortcuts-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def open_keyboard_help_from_help(n_clicks):
            """Open keyboard help modal from help modal."""
            if n_clicks:
                return True, False  # Open keyboard modal, close help modal
            raise dash.exceptions.PreventUpdate

        # Keyboard Help Modal Callbacks

        # Open/close keyboard help modal
        @app.callback(
            Output('keyboard-help-modal', 'is_open'),
            [Input('show-keyboard-help-btn', 'n_clicks'),
             Input('keyboard-help-close', 'n_clicks'),
             Input('keyboard-event-store', 'data')],
            [State('keyboard-help-modal', 'is_open')],
            prevent_initial_call=True
        )
        def toggle_keyboard_help_modal(show_clicks, close_clicks, keyboard_event, is_open):
            """Toggle keyboard help modal."""
            triggered_id = ctx.triggered_id
            
            if triggered_id == 'show-keyboard-help-btn':
                return True
            elif triggered_id == 'keyboard-help-close':
                return False
            elif triggered_id == 'keyboard-event-store' and keyboard_event:
                # Handle keyboard shortcut for help
                action = get_keyboard_action(
                    keyboard_event.get('key', ''),
                    keyboard_event.get('ctrlKey', False),
                    keyboard_event.get('shiftKey', False),
                    keyboard_event.get('altKey', False)
                )
                if action == 'toggle_help':
                    return not is_open
            
            return is_open

        # Handle keyboard shortcuts - parse from hidden input
        @app.callback(
            Output('keyboard-event-store', 'data'),
            [Input('keyboard-input', 'value')],
            prevent_initial_call=True
        )
        def parse_keyboard_input(input_value):
            """Parse keyboard input and store event data."""
            if not input_value:
                raise dash.exceptions.PreventUpdate
            
            try:
                import json
                event_data = json.loads(input_value)
                return event_data
            except (json.JSONDecodeError, TypeError):
                raise dash.exceptions.PreventUpdate

        # Handle keyboard shortcuts
        @app.callback(
            [
                Output('prev-page-btn', 'n_clicks', allow_duplicate=True),
                Output('next-page-btn', 'n_clicks', allow_duplicate=True),
                Output('global-search-input', 'value', allow_duplicate=True),
                Output('keyboard-input', 'value', allow_duplicate=True),
                Output('keyboard-help-modal', 'is_open', allow_duplicate=True),
                Output('current-page-store', 'data', allow_duplicate=True)
            ],
            [Input('keyboard-event-store', 'data')],
            [
                State('prev-page-btn', 'n_clicks'),
                State('next-page-btn', 'n_clicks'),
                State('global-search-input', 'value'),
                State('current-page-store', 'data'),
                State('filtered-data-store', 'data'),
                State('keyboard-help-modal', 'is_open')
            ],
            prevent_initial_call=True
        )
        def handle_keyboard_shortcuts(
            keyboard_event,
            prev_clicks, next_clicks, search_value,
            current_page, filtered_data, help_modal_open
        ):
            """Handle keyboard shortcuts."""
            if not keyboard_event:
                raise dash.exceptions.PreventUpdate
            
            key = keyboard_event.get('key', '')
            ctrl = keyboard_event.get('ctrlKey', False)
            shift = keyboard_event.get('shiftKey', False)
            alt = keyboard_event.get('altKey', False)
            
            action = get_keyboard_action(key, ctrl, shift, alt)
            
            if self.debug:
                print(f"[DEBUG] Keyboard shortcut: {key} -> {action}")
            
            # Handle actions
            if action == 'prev_page':
                # Trigger previous page click
                return (
                    (prev_clicks or 0) + 1,
                    dash.no_update,
                    dash.no_update,
                    '',  # Clear keyboard input
                    dash.no_update,
                    dash.no_update  # current-page-store
                )
            elif action == 'next_page':
                # Trigger next page click
                return (
                    dash.no_update,
                    (next_clicks or 0) + 1,
                    dash.no_update,
                    '',  # Clear keyboard input
                    dash.no_update,
                    dash.no_update  # current-page-store
                )
            elif action == 'first_page':
                # Go to first page - update state and trigger refresh
                self.state.current_page = 1
                return (
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    '',  # Clear keyboard input
                    dash.no_update,
                    1  # Update current-page-store to trigger main callback
                )
            elif action == 'last_page':
                # Go to last page
                import pandas as pd
                df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()
                total_pages = self.state.get_total_pages(len(df))
                new_page = total_pages if total_pages > 0 else 1
                self.state.current_page = new_page
                return (
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    '',  # Clear keyboard input
                    dash.no_update,
                    new_page  # Update current-page-store to trigger main callback
                )
            elif action == 'focus_search':
                # Focus search input - will be handled by clientside callback
                return (
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    '',  # Clear keyboard input
                    dash.no_update,
                    dash.no_update
                )
            elif action == 'clear_search':
                # Clear search
                return (
                    dash.no_update,
                    dash.no_update,
                    "",
                    '',  # Clear keyboard input
                    dash.no_update,
                    dash.no_update
                )
            elif action == 'toggle_help':
                # Toggle keyboard help modal
                return (
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    '',  # Clear keyboard input
                    not help_modal_open,
                    dash.no_update
                )
            
            # Unknown action or no action
            raise dash.exceptions.PreventUpdate

        # Export Callbacks

        # Toggle export info collapse
        @app.callback(
            Output('export-info-collapse', 'is_open'),
            [Input('export-info-btn', 'n_clicks')],
            [State('export-info-collapse', 'is_open')],
            prevent_initial_call=True
        )
        def toggle_export_info(n_clicks, is_open):
            """Toggle export info collapse."""
            if n_clicks:
                return not is_open
            raise dash.exceptions.PreventUpdate

        # Export CSV
        @app.callback(
            Output('download-csv', 'data'),
            [Input('export-csv-btn', 'n_clicks')],
            [State('filtered-data-store', 'data')],
            prevent_initial_call=True
        )
        def export_csv(n_clicks, filtered_data):
            """Export filtered data as CSV."""
            if n_clicks and filtered_data:
                import pandas as pd
                df = pd.DataFrame(filtered_data)
                csv_content = prepare_csv_export(df, self.display_info, include_internal=False)
                filename = generate_export_filename(self.display_name, 'data', 'csv')
                return dict(content=csv_content, filename=filename)
            raise dash.exceptions.PreventUpdate

        # Export View
        @app.callback(
            Output('download-view', 'data'),
            [Input('export-view-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def export_view(n_clicks):
            """Export current view configuration as JSON."""
            if n_clicks:
                view_json = prepare_view_export(
                    filters=self.state.active_filters,
                    sorts=self.state.active_sorts,
                    labels=self.state.active_labels,
                    layout={
                        'ncol': self.state.ncol,
                        'nrow': self.state.nrow,
                        'arrangement': self.state.arrangement
                    },
                    view_name=f"{self.display_name}_view"
                )
                filename = generate_export_filename(self.display_name, 'view', 'json')
                return dict(content=view_json, filename=filename)
            raise dash.exceptions.PreventUpdate

        # Export Config
        @app.callback(
            Output('download-config', 'data'),
            [Input('export-config-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def export_config(n_clicks):
            """Export display configuration as JSON."""
            if n_clicks:
                from trelliscope.dash_viewer.components.export import prepare_config_export
                config_json = prepare_config_export(self.display_info)
                filename = generate_export_filename(self.display_name, 'config', 'json')
                return dict(content=config_json, filename=filename)
            raise dash.exceptions.PreventUpdate

    def run(self, port: int = 8050, debug: Optional[bool] = None, host: str = '127.0.0.1'):
        """
        Start Dash server.

        Parameters
        ----------
        port : int
            Port number (default: 8050)
        debug : bool, optional
            Enable debug mode (default: use instance setting)
        host : str
            Host address to bind to (default: '127.0.0.1')
        """
        if debug is None:
            debug = self.debug

        # Create app if not already created
        if self.app is None:
            self.app = self.create_app()

        # Run based on mode
        if self.mode == "inline":
            try:
                self.app.run_server(mode="inline", port=port, debug=debug, host=host)
            except AttributeError:
                print("Error: jupyter-dash not available. Falling back to external mode.")
                self._run_external(port, debug, host)

        elif self.mode == "jupyterlab":
            try:
                self.app.run_server(mode="jupyterlab", port=port, debug=debug, host=host)
            except AttributeError:
                print("Error: jupyter-dash not available. Falling back to external mode.")
                self._run_external(port, debug, host)

        else:  # external
            self._run_external(port, debug, host)

    def _run_external(self, port: int, debug: bool, host: str = '127.0.0.1'):
        """Run in external browser mode."""
        url = f"http://{host}:{port}"

        def open_browser():
            time.sleep(1.5)
            webbrowser.open(url)

        # Start browser in background thread
        threading.Thread(target=open_browser, daemon=True).start()

        print(f"🚀 Dash viewer starting on {url}")
        print(f"📊 Display: {self.display_name}")
        print(f"📈 Panels: {len(self.cog_data)}")
        print(f"\n✨ Opening browser...")

        # Use Flask's run method directly to avoid Dash's enable_dev_tools issue
        # Dash's run() tries to register error handlers after first request, causing AssertionError
        # By using Flask's run() directly, we bypass this issue
        # Disable reloader in Jupyter notebooks (it conflicts with IPython kernel)
        try:
            # Check if we're in a Jupyter/IPython environment
            from IPython import get_ipython
            in_jupyter = get_ipython() is not None
        except ImportError:
            in_jupyter = False
        
        # Disable reloader if in Jupyter or if debug is False
        use_reloader = debug and not in_jupyter
        
        self.app.server.run(port=port, debug=debug, host=host, use_reloader=use_reloader)

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
