"""
Panel detail modal for viewing full panel information.
"""

from typing import Dict, Any, Optional, List
import dash_bootstrap_components as dbc
from dash import html, dcc
import base64
from pathlib import Path
import pandas as pd


def create_panel_detail_modal() -> dbc.Modal:
    """
    Create panel detail modal (empty initially, populated by callback).

    Returns
    -------
    dbc.Modal
        Modal component for panel details
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    dbc.Button("←", id="panel-detail-prev", size="sm", outline=True),
                                    html.Span(id="panel-detail-title", style={'margin': '0 15px', 'fontWeight': 'bold'}),
                                    dbc.Button("→", id="panel-detail-next", size="sm", outline=True)
                                ],
                                style={'display': 'flex', 'alignItems': 'center'}
                            ),
                            width=10
                        ),
                        dbc.Col(
                            dbc.Button("✕", id="panel-detail-close", size="sm", color="secondary", outline=True),
                            width=2,
                            className="text-end"
                        )
                    ],
                    align="center"
                ),
                close_button=False
            ),
            dbc.ModalBody(
                [
                    # Panel display area
                    html.Div(
                        id='panel-detail-content',
                        style={
                            'textAlign': 'center',
                            'marginBottom': '20px',
                            'maxHeight': '60vh',
                            'overflow': 'auto'
                        }
                    ),

                    # Metadata display
                    html.Div(
                        id='panel-detail-metadata',
                        style={'fontSize': '14px'}
                    )
                ],
                style={'padding': '20px'}
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Download Panel", id="panel-detail-download", color="primary", size="sm", className="me-2"),
                    dbc.Button("Copy Metadata", id="panel-detail-copy", color="secondary", size="sm", className="me-2"),
                    dbc.Button("Close", id="panel-detail-close-footer", color="secondary", size="sm")
                ]
            )
        ],
        id="panel-detail-modal",
        size="xl",
        is_open=False,
        centered=True,
        scrollable=True
    )


def format_panel_content(panel_path: Path, panel_type: str) -> html.Div:
    """
    Format panel content for display in modal.

    Parameters
    ----------
    panel_path : Path
        Path to panel file
    panel_type : str
        Type of panel ('image' or 'plotly')

    Returns
    -------
    html.Div
        Formatted panel content
    """
    if panel_type == 'image':
        # Display image
        try:
            with open(panel_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')

            ext = panel_path.suffix.lower()
            if ext in ['.png']:
                mime = 'image/png'
            elif ext in ['.jpg', '.jpeg']:
                mime = 'image/jpeg'
            elif ext in ['.svg']:
                mime = 'image/svg+xml'
            else:
                mime = 'image/png'

            return html.Img(
                src=f"data:{mime};base64,{encoded}",
                style={
                    'maxWidth': '100%',
                    'maxHeight': '60vh',
                    'objectFit': 'contain'
                }
            )
        except Exception as e:
            return html.Div(f"Error loading image: {e}", style={'color': 'red'})

    elif panel_type == 'plotly':
        # Display plotly HTML in iframe
        try:
            return html.Iframe(
                src=str(panel_path),
                style={
                    'width': '100%',
                    'height': '60vh',
                    'border': 'none'
                }
            )
        except Exception as e:
            return html.Div(f"Error loading panel: {e}", style={'color': 'red'})

    else:
        return html.Div("Unknown panel type", style={'color': 'gray'})


def format_metadata_table(panel_data: Dict[str, Any], display_info: Dict[str, Any]) -> html.Div:
    """
    Format metadata as a table.

    Parameters
    ----------
    panel_data : dict
        Panel data row (from cogData)
    display_info : dict
        Display configuration

    Returns
    -------
    html.Div
        Formatted metadata table
    """
    metas = display_info.get('metas', [])

    # Create metadata rows
    rows = []
    for meta in metas:
        varname = meta.get('varname')
        label = meta.get('label', varname)
        meta_type = meta.get('type')

        # Skip panel columns
        if meta_type in ['panel_src', 'panel_local']:
            continue

        # Get value
        value = panel_data.get(varname)

        # For factors, also check label column
        if meta_type == 'factor':
            label_col = f"{varname}_label"
            if label_col in panel_data:
                value = panel_data[label_col]
            else:
                # Map index to level
                levels = meta.get('levels', [])
                if isinstance(value, (int, float)) and 0 <= value < len(levels):
                    value = levels[int(value)]

        # Format value
        if value is None or (isinstance(value, float) and pd.isna(value)):
            formatted_value = html.Em("[missing]", style={'color': '#999'})
        elif meta_type == 'href':
            formatted_value = html.A(
                value if isinstance(value, dict) else str(value),
                href=value.get('href', '#') if isinstance(value, dict) else str(value),
                target='_blank',
                style={'color': '#007bff'}
            )
        elif meta_type == 'currency':
            formatted_value = f"${value:,.2f}" if isinstance(value, (int, float)) else str(value)
        elif meta_type == 'number':
            digits = meta.get('digits', 2)
            if isinstance(value, (int, float)):
                formatted_value = f"{value:,.{digits}f}"
            else:
                formatted_value = str(value)
        else:
            formatted_value = str(value)

        # Create row
        row = html.Tr(
            [
                html.Td(label, style={'fontWeight': 'bold', 'width': '30%', 'padding': '8px'}),
                html.Td(formatted_value, style={'padding': '8px'})
            ]
        )
        rows.append(row)

    if not rows:
        return html.Div("No metadata available", style={'color': '#999', 'fontStyle': 'italic'})

    return dbc.Table(
        [html.Tbody(rows)],
        bordered=True,
        hover=True,
        size='sm',
        style={'fontSize': '13px'}
    )


def get_panel_navigation_info(
    panel_index: int,
    total_panels: int
) -> tuple:
    """
    Get panel navigation information.

    Parameters
    ----------
    panel_index : int
        Current panel index (0-based)
    total_panels : int
        Total number of panels

    Returns
    -------
    tuple
        (title_text, prev_disabled, next_disabled)
    """
    # Panel numbers are 1-based for display
    panel_num = panel_index + 1

    title_text = f"Panel {panel_num} of {total_panels}"
    prev_disabled = panel_index <= 0
    next_disabled = panel_index >= total_panels - 1

    return title_text, prev_disabled, next_disabled
