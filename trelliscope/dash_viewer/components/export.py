"""
Export and share functionality for Dash viewer.

Allows exporting filtered data and view configurations.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any, List
import pandas as pd
import json
from datetime import datetime


def create_export_panel() -> html.Div:
    """
    Create export panel with download options.

    Returns
    -------
    html.Div
        Export panel container
    """
    return html.Div([
        html.H6("Export", className="mb-3"),

        html.P([
            html.Small([
                html.I(className="bi bi-download me-2"),
                "Export filtered data or configuration"
            ], className="text-muted")
        ], className="mb-3"),

        # Export options
        dbc.Stack([
            dbc.Button(
                [html.I(className="bi bi-file-earmark-spreadsheet me-2"), "Export Data (CSV)"],
                id='export-csv-btn',
                color='primary',
                size='sm',
                outline=True,
                className="w-100 mb-2"
            ),
            dbc.Button(
                [html.I(className="bi bi-file-earmark-code me-2"), "Export View (JSON)"],
                id='export-view-btn',
                color='primary',
                size='sm',
                outline=True,
                className="w-100 mb-2"
            ),
            dbc.Button(
                [html.I(className="bi bi-file-earmark-text me-2"), "Export Config"],
                id='export-config-btn',
                color='primary',
                size='sm',
                outline=True,
                className="w-100 mb-2"
            ),
        ], gap=1),

        # Download components (hidden)
        dcc.Download(id='download-csv'),
        dcc.Download(id='download-view'),
        dcc.Download(id='download-config'),

        # Export info
        html.Div([
            dbc.Button(
                [html.I(className="bi bi-question-circle me-2"), "Export Info"],
                id='export-info-btn',
                color='link',
                size='sm',
                className="p-0 mt-2"
            ),
            dbc.Collapse([
                dbc.Card([
                    dbc.CardBody([
                        html.P([
                            html.Strong("Export Options:"),
                            html.Br(),
                            "• CSV: Filtered data with metadata",
                            html.Br(),
                            "• View: Current filter/sort state",
                            html.Br(),
                            "• Config: Display configuration"
                        ], className="small mb-0")
                    ])
                ], className="mt-2")
            ], id='export-info-collapse', is_open=False)
        ]),

        html.Hr(className="my-3"),

    ], className="mb-3")


def prepare_csv_export(
    data: pd.DataFrame,
    display_info: Dict[str, Any],
    include_internal: bool = False
) -> str:
    """
    Prepare data for CSV export.

    Parameters
    ----------
    data : pd.DataFrame
        Filtered data to export
    display_info : dict
        Display configuration
    include_internal : bool
        Include internal columns (starting with _)

    Returns
    -------
    str
        CSV string
    """
    # Remove internal columns if requested
    if not include_internal:
        export_cols = [col for col in data.columns if not col.startswith('_')]
        export_data = data[export_cols].copy()
    else:
        export_data = data.copy()

    # Convert to CSV
    return export_data.to_csv(index=False)


def prepare_view_export(
    filters: Dict[str, Any],
    sorts: List[tuple],
    labels: List[str],
    layout: Dict[str, Any],
    view_name: str = ""
) -> str:
    """
    Prepare view configuration for export.

    Parameters
    ----------
    filters : dict
        Active filters
    sorts : list
        Active sorts
    labels : list
        Active labels
    layout : dict
        Layout configuration
    view_name : str
        Name of the view

    Returns
    -------
    str
        JSON string
    """
    view_config = {
        'name': view_name or f"exported_view_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'exported_at': datetime.now().isoformat(),
        'state': {
            'filters': [
                {'varname': v, 'value': val}
                for v, val in filters.items()
            ],
            'sorts': [
                {'varname': v, 'dir': d}
                for v, d in sorts
            ],
            'labels': labels,
            'layout': layout
        }
    }

    return json.dumps(view_config, indent=2)


def prepare_config_export(display_info: Dict[str, Any]) -> str:
    """
    Prepare full display configuration for export.

    Parameters
    ----------
    display_info : dict
        Display configuration

    Returns
    -------
    str
        JSON string
    """
    # Create export-friendly version (remove large data)
    config = {
        'name': display_info.get('name'),
        'description': display_info.get('description'),
        'exported_at': datetime.now().isoformat(),
        'n': display_info.get('n'),
        'metas': display_info.get('metas', []),
        'state': display_info.get('state', {}),
        'panelInterface': display_info.get('panelInterface', {}),
    }

    return json.dumps(config, indent=2)


def generate_export_filename(
    display_name: str,
    export_type: str,
    extension: str
) -> str:
    """
    Generate export filename.

    Parameters
    ----------
    display_name : str
        Name of display
    export_type : str
        Type of export (data, view, config)
    extension : str
        File extension

    Returns
    -------
    str
        Filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{display_name}_{export_type}_{timestamp}.{extension}"


def create_share_link(
    display_path: str,
    view_name: str = "",
    base_url: str = ""
) -> str:
    """
    Create shareable link to display.

    Parameters
    ----------
    display_path : str
        Path to display
    view_name : str
        Name of view to load
    base_url : str
        Base URL for the application

    Returns
    -------
    str
        Shareable URL
    """
    # Construct URL
    url = f"{base_url}/?display={display_path}"

    if view_name:
        url += f"&view={view_name}"

    return url


def create_copy_link_button(url: str) -> dbc.Button:
    """
    Create button to copy link to clipboard.

    Parameters
    ----------
    url : str
        URL to copy

    Returns
    -------
    dbc.Button
        Copy button with JavaScript
    """
    return dbc.Button(
        [html.I(className="bi bi-clipboard me-2"), "Copy Link"],
        id='copy-link-btn',
        color='secondary',
        size='sm',
        outline=True,
        n_clicks=0
    )
