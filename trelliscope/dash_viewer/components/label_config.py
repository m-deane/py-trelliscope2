"""
Label configuration component for Dash viewer.

Allows users to select which metadata fields appear as panel labels.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any, List
import pandas as pd


def create_label_config_panel(metas: List[Dict[str, Any]], active_labels: List[str]) -> html.Div:
    """
    Create label configuration panel.

    Parameters
    ----------
    metas : list
        List of metadata definitions
    active_labels : list
        Currently active label variable names

    Returns
    -------
    html.Div
        Label configuration panel
    """
    # Get labelable metadata (exclude panel types)
    labelable_metas = [
        meta for meta in metas
        if meta.get('type') not in ['panel_local', 'panel_src']
    ]

    # Create checkbox options
    label_options = [
        {
            'label': html.Span([
                html.Strong(meta.get('label', meta.get('varname'))),
                html.Small(f" ({meta.get('type')})", className="text-muted ms-1")
            ]),
            'value': meta.get('varname')
        }
        for meta in labelable_metas
    ]

    # Determine which are checked
    checked_values = [
        meta.get('varname') for meta in labelable_metas
        if meta.get('varname') in active_labels
    ]

    return html.Div([
        html.H6("Labels", className="mb-3"),

        html.P([
            html.Small([
                html.I(className="bi bi-info-circle me-2"),
                "Select metadata to display under each panel"
            ], className="text-muted")
        ], className="mb-2"),

        # Label checklist
        dbc.Checklist(
            id='label-checklist',
            options=label_options,
            value=checked_values,
            className="mb-3",
            style={'maxHeight': '200px', 'overflowY': 'auto'}
        ),

        # Control buttons
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Select All",
                    id='label-select-all-btn',
                    color='secondary',
                    size='sm',
                    outline=True,
                    className="w-100"
                )
            ], width=6),
            dbc.Col([
                dbc.Button(
                    "Clear All",
                    id='label-clear-all-btn',
                    color='secondary',
                    size='sm',
                    outline=True,
                    className="w-100"
                )
            ], width=6)
        ], className="mb-3"),

        # Info collapse
        html.Div([
            dbc.Button(
                [html.I(className="bi bi-question-circle me-2"), "Label Tips"],
                id='label-info-btn',
                color='link',
                size='sm',
                className="p-0"
            ),
            dbc.Collapse([
                dbc.Card([
                    dbc.CardBody([
                        html.P([
                            html.Strong("Label Tips:"),
                            html.Br(),
                            "• Labels appear below each panel",
                            html.Br(),
                            "• Reorder by dragging (future feature)",
                            html.Br(),
                            "• Label changes apply immediately",
                            html.Br(),
                            "• Saved in views"
                        ], className="small mb-0")
                    ])
                ], className="mt-2")
            ], id='label-info-collapse', is_open=False)
        ]),

        html.Hr(className="my-3"),

    ], className="mb-3")


def get_labelable_metas(metas: List[Dict[str, Any]]) -> List[str]:
    """
    Get list of labelable metadata variable names.

    Parameters
    ----------
    metas : list
        List of metadata definitions

    Returns
    -------
    list
        List of variable names that can be used as labels
    """
    return [
        meta.get('varname') for meta in metas
        if meta.get('type') not in ['panel_local', 'panel_src']
    ]


def format_label_value(value: Any, meta: Dict[str, Any]) -> str:
    """
    Format a metadata value for display as a label.

    Parameters
    ----------
    value : any
        Metadata value
    meta : dict
        Metadata definition

    Returns
    -------
    str
        Formatted label string
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "[missing]"

    meta_type = meta.get('type', 'base')

    if meta_type == 'factor':
        # Already a label string if from _label column
        return str(value)

    elif meta_type == 'number':
        # Format with appropriate precision
        digits = meta.get('digits', 2)
        if isinstance(value, (int, float)):
            if digits == 0:
                return f"{int(value):,}"
            else:
                return f"{value:,.{digits}f}"
        return str(value)

    elif meta_type == 'currency':
        # Format as currency
        digits = meta.get('digits', 2)
        if isinstance(value, (int, float)):
            return f"${value:,.{digits}f}"
        return str(value)

    elif meta_type in ['date', 'time']:
        # Return as-is (should already be formatted)
        return str(value)

    elif meta_type == 'href':
        # Extract label if dict, otherwise use value
        if isinstance(value, dict):
            return value.get('label', value.get('href', str(value)))
        return str(value)

    else:  # base, graph, etc.
        return str(value)


def create_panel_labels_html(
    panel_data: Dict[str, Any],
    active_labels: List[str],
    metas: List[Dict[str, Any]]
) -> List[html.Div]:
    """
    Create HTML for panel labels.

    Parameters
    ----------
    panel_data : dict
        Panel data row
    active_labels : list
        Active label variable names
    metas : list
        Metadata definitions

    Returns
    -------
    list
        List of html.Div elements for labels
    """
    labels = []
    meta_dict = {m.get('varname'): m for m in metas}

    for varname in active_labels:
        if varname not in panel_data or varname not in meta_dict:
            continue

        value = panel_data[varname]
        meta = meta_dict[varname]

        # For factors, check if there's a _label column
        if meta.get('type') == 'factor':
            label_col = f"{varname}_label"
            if label_col in panel_data:
                value = panel_data[label_col]

        formatted_value = format_label_value(value, meta)
        label_text = meta.get('label', varname)

        labels.append(
            html.Div([
                html.Strong(f"{label_text}: ", className="me-1"),
                html.Span(formatted_value)
            ], className="panel-label-item small")
        )

    return labels
