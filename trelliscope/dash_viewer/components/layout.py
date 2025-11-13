"""
Grid layout components for panel display.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

from dash import html
from trelliscope.dash_viewer.components.panels import PanelRenderer


def create_panel_grid(
    panel_data: pd.DataFrame,
    ncol: int,
    nrow: int,
    active_labels: List[str],
    display_info: Dict[str, Any],
    panel_width: Optional[int] = None,
    panel_height: Optional[int] = None
) -> html.Div:
    """
    Create grid of panels with labels.

    Parameters
    ----------
    panel_data : pd.DataFrame
        DataFrame containing panel data for current page
    ncol : int
        Number of columns
    nrow : int
        Number of rows
    active_labels : list
        List of variable names to display as labels
    display_info : dict
        Display configuration
    panel_width : int, optional
        Panel width in pixels
    panel_height : int, optional
        Panel height in pixels

    Returns
    -------
    html.Div
        Grid container with panels
    """
    if panel_data.empty:
        return html.Div(
            "No panels to display",
            style={
                'padding': '40px',
                'textAlign': 'center',
                'color': '#666',
                'fontSize': '18px'
            }
        )

    renderer = PanelRenderer()
    grid_items = []

    # Get primary panel column name
    panel_col = display_info.get('primarypanel', 'panel')

    # Get meta lookup for formatting
    meta_lookup = {
        meta['varname']: meta
        for meta in display_info.get('metas', [])
    }

    for idx, row in panel_data.iterrows():
        # Get panel path and type
        panel_path = row.get('_panel_full_path')
        panel_type = row.get('_panel_type', 'unknown')
        panel_key = str(row.get('panelKey', idx))

        if panel_path is None or not Path(panel_path).exists():
            panel_component = html.Div(
                "Panel not found",
                style={
                    'width': '100%',
                    'height': '400px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'backgroundColor': '#f8f9fa',
                    'color': '#6c757d',
                    'border': '1px dashed #dee2e6'
                }
            )
        elif panel_type == 'image':
            panel_component = renderer.render_image_panel(
                Path(panel_path),
                width=panel_width,
                height=panel_height,
                panel_key=panel_key
            )
        elif panel_type == 'plotly':
            panel_component = renderer.render_plotly_panel(
                Path(panel_path),
                width=panel_width,
                height=panel_height,
                panel_key=panel_key
            )
        else:
            panel_component = html.Div(
                f"Unknown panel type: {panel_type}",
                style={
                    'width': '100%',
                    'height': '400px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'backgroundColor': '#fff3cd',
                    'color': '#856404'
                }
            )

        # Create labels
        label_elements = []
        for varname in active_labels:
            if varname not in row:
                continue

            value = row[varname]
            meta = meta_lookup.get(varname, {})

            # Format value based on meta type
            formatted_value = format_value(value, meta)

            label_text = f"{meta.get('label', varname)}: {formatted_value}"

            label_elements.append(
                html.Div(
                    label_text,
                    className='panel-label',
                    style={
                        'fontSize': '12px',
                        'marginBottom': '4px',
                        'color': '#495057'
                    }
                )
            )

        # Create panel container (clickable for modal)
        panel_container = html.Div(
            [
                html.Div(
                    panel_component,
                    className='panel-content',
                    style={
                        'backgroundColor': 'white',
                        'border': '1px solid #dee2e6',
                        'borderRadius': '4px 4px 0 0',
                        'overflow': 'hidden'
                    }
                ),
                html.Div(
                    label_elements,
                    className='panel-labels',
                    style={
                        'padding': '10px',
                        'backgroundColor': '#f8f9fa',
                        'border': '1px solid #dee2e6',
                        'borderTop': 'none',
                        'borderRadius': '0 0 4px 4px'
                    }
                ) if label_elements else html.Div()
            ],
            id={'type': 'panel-item', 'index': int(idx)},
            className='panel-container',
            style={
                'marginBottom': '0',
                'cursor': 'pointer',
                'transition': 'transform 0.2s, box-shadow 0.2s'
            },
            n_clicks=0
        )

        grid_items.append(panel_container)

    # Create grid
    grid_style = {
        'display': 'grid',
        'gridTemplateColumns': f'repeat({ncol}, 1fr)',
        'gap': '20px',
        'padding': '20px',
        'backgroundColor': '#ffffff'
    }

    return html.Div(
        grid_items,
        id='panel-grid',
        style=grid_style
    )


def format_value(value: Any, meta: Dict[str, Any]) -> str:
    """
    Format value based on meta type.

    Parameters
    ----------
    value : any
        Value to format
    meta : dict
        Meta configuration

    Returns
    -------
    str
        Formatted value string
    """
    if pd.isna(value):
        return "N/A"

    meta_type = meta.get('type', 'string')

    if meta_type == 'number':
        digits = meta.get('digits', 2)
        try:
            return f"{float(value):.{digits}f}"
        except (ValueError, TypeError):
            return str(value)

    elif meta_type == 'currency':
        digits = meta.get('digits', 2)
        try:
            return f"${float(value):,.{digits}f}"
        except (ValueError, TypeError):
            return str(value)

    elif meta_type == 'date':
        # Format date
        try:
            return pd.to_datetime(value).strftime('%Y-%m-%d')
        except:
            return str(value)

    elif meta_type == 'time':
        # Format datetime
        try:
            return pd.to_datetime(value).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(value)

    else:
        return str(value)
