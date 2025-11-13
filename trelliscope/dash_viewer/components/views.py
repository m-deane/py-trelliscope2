"""
Views components for saving and loading display states.
"""

from typing import List, Dict, Any
import dash_bootstrap_components as dbc
from dash import html, dcc


def create_views_panel(views: List[Dict[str, Any]]) -> html.Div:
    """
    Create views panel for managing saved views.

    Parameters
    ----------
    views : list
        List of saved view dictionaries

    Returns
    -------
    html.Div
        Views panel container
    """
    # Create view selector options
    view_options = [
        {'label': view.get('name', f"View {i+1}"), 'value': str(i)}
        for i, view in enumerate(views)
    ]

    # Create saved views list
    view_items = []
    if views:
        for i, view in enumerate(views):
            view_item = create_view_item(i, view)
            view_items.append(view_item)
    else:
        view_items = [
            html.Div(
                "No saved views",
                className='text-muted text-center',
                style={'padding': '20px', 'fontSize': '13px'}
            )
        ]

    return html.Div(
        [
            html.H6("Views", className='mb-3', style={'fontWeight': 'bold'}),

            # Save current view
            html.Div(
                [
                    html.Label("Save Current View:", style={'fontSize': '13px', 'marginBottom': '5px'}),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id='save-view-name',
                                    placeholder='View name...',
                                    type='text',
                                    size='sm',
                                    style={'fontSize': '13px'}
                                ),
                                width=8
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Save",
                                    id='save-view-btn',
                                    color='primary',
                                    size='sm',
                                    className='w-100'
                                ),
                                width=4
                            )
                        ],
                        className='g-2'
                    ),
                ],
                className='mb-3'
            ),

            # Load saved view
            html.Div(
                [
                    html.Label("Load Saved View:", style={'fontSize': '13px', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='load-view-select',
                        options=view_options,
                        placeholder='Select view...',
                        clearable=True,
                        style={'fontSize': '13px', 'marginBottom': '10px'}
                    ),
                ],
                className='mb-3'
            ),

            # Saved views list
            html.Div(
                [
                    html.Label("Saved Views:", style={'fontSize': '13px', 'marginBottom': '10px'}),
                    html.Div(
                        view_items,
                        id='saved-views-list'
                    )
                ]
            )
        ],
        style={
            'padding': '15px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '4px',
            'marginBottom': '20px'
        }
    )


def create_view_item(index: int, view: Dict[str, Any]) -> html.Div:
    """
    Create individual saved view item display.

    Parameters
    ----------
    index : int
        View index in list
    view : dict
        View configuration dictionary

    Returns
    -------
    html.Div
        View item component
    """
    view_name = view.get('name', f"View {index + 1}")
    state = view.get('state', {})

    # Build summary of view state
    summary_parts = []

    # Filters count
    filters = state.get('filters', [])
    if filters:
        summary_parts.append(f"{len(filters)} filter(s)")

    # Sorts count
    sorts = state.get('sorts', [])
    if sorts:
        summary_parts.append(f"{len(sorts)} sort(s)")

    # Layout
    layout = state.get('layout', {})
    if layout:
        ncol = layout.get('ncol', 3)
        nrow = layout.get('nrow', 2)
        summary_parts.append(f"{ncol}×{nrow} grid")

    summary_text = ", ".join(summary_parts) if summary_parts else "Default state"

    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    view_name,
                                    style={'fontWeight': '500', 'fontSize': '13px'}
                                ),
                                html.Div(
                                    summary_text,
                                    style={'fontSize': '11px', 'color': '#6c757d'}
                                )
                            ],
                            width=8
                        ),
                        dbc.Col(
                            [
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "Load",
                                            id={'type': 'load-view-btn', 'index': index},
                                            size='sm',
                                            color='primary',
                                            outline=True,
                                            style={'fontSize': '11px', 'padding': '2px 8px'}
                                        ),
                                        dbc.Button(
                                            "✕",
                                            id={'type': 'delete-view-btn', 'index': index},
                                            size='sm',
                                            color='danger',
                                            outline=True,
                                            style={'fontSize': '11px', 'padding': '2px 8px'}
                                        )
                                    ],
                                    size='sm'
                                )
                            ],
                            width=4,
                            className='text-end'
                        )
                    ],
                    align='center'
                )
            ],
            style={'padding': '8px 12px'}
        ),
        className='mb-2',
        style={'border': '1px solid #dee2e6', 'fontSize': '13px'}
    )


def update_views_panel_state(views: List[Dict[str, Any]]) -> tuple:
    """
    Update views panel display based on current views.

    Parameters
    ----------
    views : list
        List of saved views

    Returns
    -------
    tuple
        (view_items, dropdown_options)
    """
    # Create view items
    view_items = []
    if views:
        for i, view in enumerate(views):
            view_item = create_view_item(i, view)
            view_items.append(view_item)
    else:
        view_items = [
            html.Div(
                "No saved views",
                className='text-muted text-center',
                style={'padding': '20px', 'fontSize': '13px'}
            )
        ]

    # Create dropdown options
    view_options = [
        {'label': view.get('name', f"View {i+1}"), 'value': str(i)}
        for i, view in enumerate(views)
    ]

    return view_items, view_options


def create_view_notification(message: str, success: bool = True) -> dbc.Toast:
    """
    Create notification toast for view operations.

    Parameters
    ----------
    message : str
        Notification message
    success : bool
        Whether operation was successful

    Returns
    -------
    dbc.Toast
        Toast notification component
    """
    return dbc.Toast(
        message,
        id="view-notification",
        header="Views" if success else "Error",
        is_open=True,
        dismissable=True,
        duration=3000,
        icon="success" if success else "danger",
        style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 1050}
    )
