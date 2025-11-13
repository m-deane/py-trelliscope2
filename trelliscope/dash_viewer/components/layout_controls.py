"""
Layout controls component for Dash viewer.

Allows users to dynamically adjust grid layout (ncol, nrow, arrangement).
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any


def create_layout_controls() -> html.Div:
    """
    Create layout controls panel.

    Returns
    -------
    html.Div
        Layout controls panel with ncol, nrow, and arrangement controls
    """
    return html.Div([
        html.H6("Layout", className="mb-3"),

        # Number of columns
        html.Label("Columns", className="form-label small"),
        dbc.Row([
            dbc.Col([
                dcc.Slider(
                    id='layout-ncol-slider',
                    min=1,
                    max=10,
                    step=1,
                    value=4,
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ], width=10),
            dbc.Col([
                dbc.Input(
                    id='layout-ncol-input',
                    type='number',
                    min=1,
                    max=10,
                    value=4,
                    size='sm'
                )
            ], width=2)
        ], className="mb-3"),

        # Number of rows
        html.Label("Rows", className="form-label small"),
        dbc.Row([
            dbc.Col([
                dcc.Slider(
                    id='layout-nrow-slider',
                    min=1,
                    max=10,
                    step=1,
                    value=2,
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ], width=10),
            dbc.Col([
                dbc.Input(
                    id='layout-nrow-input',
                    type='number',
                    min=1,
                    max=10,
                    value=2,
                    size='sm'
                )
            ], width=2)
        ], className="mb-3"),

        # Arrangement
        html.Label("Arrangement", className="form-label small"),
        dbc.RadioItems(
            id='layout-arrangement',
            options=[
                {'label': 'Row-major (left to right, top to bottom)', 'value': 'row'},
                {'label': 'Column-major (top to bottom, left to right)', 'value': 'col'}
            ],
            value='row',
            className="mb-3"
        ),

        # Panels per page display
        html.Div([
            html.Small([
                html.I(className="bi bi-info-circle me-2"),
                html.Span(id='layout-panels-per-page', children="Panels per page: 8")
            ], className="text-muted")
        ], className="mb-3"),

        # Apply button
        dbc.Button(
            "Apply Layout",
            id='apply-layout-btn',
            color='primary',
            size='sm',
            className="w-100 mb-2"
        ),

        # Reset button
        dbc.Button(
            "Reset to Default",
            id='reset-layout-btn',
            color='secondary',
            size='sm',
            outline=True,
            className="w-100"
        ),

        html.Hr(className="my-3"),

    ], className="mb-3")


def get_layout_from_state(display_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract layout configuration from display info.

    Parameters
    ----------
    display_info : dict
        Display configuration

    Returns
    -------
    dict
        Layout configuration with ncol, nrow, arrangement
    """
    default_layout = {
        'ncol': 4,
        'nrow': 2,
        'arrangement': 'row'
    }

    if 'state' not in display_info:
        return default_layout

    state = display_info['state']
    if 'layout' not in state:
        return default_layout

    layout = state['layout']
    return {
        'ncol': layout.get('ncol', default_layout['ncol']),
        'nrow': layout.get('nrow', default_layout['nrow']),
        'arrangement': layout.get('arrangement', default_layout['arrangement'])
    }


def validate_layout_values(ncol: int, nrow: int) -> tuple[int, int, str]:
    """
    Validate and constrain layout values.

    Parameters
    ----------
    ncol : int
        Number of columns
    nrow : int
        Number of rows

    Returns
    -------
    tuple
        (ncol, nrow, error_message) - error_message is empty string if valid
    """
    errors = []

    # Constrain ncol
    if ncol < 1:
        ncol = 1
        errors.append("Columns must be >= 1")
    elif ncol > 10:
        ncol = 10
        errors.append("Columns must be <= 10")

    # Constrain nrow
    if nrow < 1:
        nrow = 1
        errors.append("Rows must be >= 1")
    elif nrow > 10:
        nrow = 10
        errors.append("Rows must be <= 10")

    error_msg = "; ".join(errors) if errors else ""
    return ncol, nrow, error_msg


def format_layout_summary(ncol: int, nrow: int, arrangement: str) -> str:
    """
    Format layout configuration as summary string.

    Parameters
    ----------
    ncol : int
        Number of columns
    nrow : int
        Number of rows
    arrangement : str
        Arrangement type ('row' or 'col')

    Returns
    -------
    str
        Formatted summary
    """
    panels_per_page = ncol * nrow
    arr_name = "row-major" if arrangement == "row" else "column-major"

    return f"{ncol}×{nrow} grid ({panels_per_page} panels/page, {arr_name})"
