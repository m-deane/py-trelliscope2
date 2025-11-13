"""
Sort components for Dash viewer.
"""

from typing import List, Dict, Any, Tuple
import dash_bootstrap_components as dbc
from dash import html, dcc


def create_sort_panel(
    sortable_metas: List[Dict[str, Any]],
    active_sorts: List[Tuple[str, str]]
) -> html.Div:
    """
    Create sort panel with sort controls.

    Parameters
    ----------
    sortable_metas : list
        List of meta dictionaries for sortable variables
    active_sorts : list
        List of active sorts as [(varname, direction), ...]

    Returns
    -------
    html.Div
        Sort panel container
    """
    # Create sort selector options
    sort_options = [
        {'label': meta.get('label', meta['varname']), 'value': meta['varname']}
        for meta in sortable_metas
    ]

    # Create active sort displays
    active_sort_items = []
    for i, (varname, direction) in enumerate(active_sorts):
        # Find meta for label
        meta = next((m for m in sortable_metas if m['varname'] == varname), None)
        label = meta.get('label', varname) if meta else varname

        sort_item = create_sort_item(i + 1, varname, label, direction)
        active_sort_items.append(sort_item)

    # If no active sorts, show placeholder
    if not active_sort_items:
        active_sort_items = [
            html.Div(
                "No active sorts",
                className='text-muted text-center',
                style={'padding': '20px', 'fontSize': '13px'}
            )
        ]

    return html.Div(
        [
            html.H6("Sort", className='mb-3', style={'fontWeight': 'bold'}),

            # Add sort selector
            html.Div(
                [
                    html.Label("Add Sort:", style={'fontSize': '13px', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='add-sort-select',
                        options=sort_options,
                        placeholder='Select variable...',
                        clearable=True,
                        style={'fontSize': '13px', 'marginBottom': '10px'}
                    ),
                ],
                className='mb-3'
            ),

            # Clear all sorts button
            dbc.Button(
                "Clear All Sorts",
                id='clear-sorts-btn',
                color='secondary',
                size='sm',
                className='w-100 mb-3',
                disabled=len(active_sorts) == 0
            ),

            # Active sorts list
            html.Div(
                [
                    html.Label("Active Sorts:", style={'fontSize': '13px', 'marginBottom': '10px'}),
                    html.Div(
                        active_sort_items,
                        id='active-sorts-list'
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


def create_sort_item(
    priority: int,
    varname: str,
    label: str,
    direction: str
) -> html.Div:
    """
    Create individual sort item display.

    Parameters
    ----------
    priority : int
        Sort priority (1 = highest)
    varname : str
        Variable name
    label : str
        Display label
    direction : str
        Sort direction ('asc' or 'desc')

    Returns
    -------
    html.Div
        Sort item component
    """
    # Direction indicator
    direction_icon = "↑" if direction == "asc" else "↓"
    direction_text = "ascending" if direction == "asc" else "descending"

    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Span(
                                    f"{priority}. ",
                                    style={'fontWeight': 'bold', 'color': '#007bff'}
                                ),
                                html.Span(
                                    label,
                                    style={'fontWeight': '500'}
                                ),
                                html.Span(
                                    f" {direction_icon}",
                                    style={'fontSize': '16px', 'color': '#6c757d'}
                                )
                            ],
                            width=8
                        ),
                        dbc.Col(
                            [
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "↑",
                                            id={'type': 'sort-asc', 'varname': varname},
                                            size='sm',
                                            color='primary' if direction == 'asc' else 'light',
                                            outline=direction != 'asc',
                                            style={'fontSize': '12px', 'padding': '2px 8px'}
                                        ),
                                        dbc.Button(
                                            "↓",
                                            id={'type': 'sort-desc', 'varname': varname},
                                            size='sm',
                                            color='primary' if direction == 'desc' else 'light',
                                            outline=direction != 'desc',
                                            style={'fontSize': '12px', 'padding': '2px 8px'}
                                        ),
                                        dbc.Button(
                                            "✕",
                                            id={'type': 'sort-remove', 'varname': varname},
                                            size='sm',
                                            color='danger',
                                            outline=True,
                                            style={'fontSize': '12px', 'padding': '2px 8px'}
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


def update_sort_panel_state(
    sortable_metas: List[Dict[str, Any]],
    active_sorts: List[Tuple[str, str]]
) -> Tuple[List[Any], bool]:
    """
    Update sort panel display based on current state.

    Parameters
    ----------
    sortable_metas : list
        List of sortable meta variables
    active_sorts : list
        Current active sorts

    Returns
    -------
    tuple
        (active_sort_items, clear_button_disabled)
    """
    active_sort_items = []

    for i, (varname, direction) in enumerate(active_sorts):
        # Find meta for label
        meta = next((m for m in sortable_metas if m['varname'] == varname), None)
        label = meta.get('label', varname) if meta else varname

        sort_item = create_sort_item(i + 1, varname, label, direction)
        active_sort_items.append(sort_item)

    # If no active sorts, show placeholder
    if not active_sort_items:
        active_sort_items = [
            html.Div(
                "No active sorts",
                className='text-muted text-center',
                style={'padding': '20px', 'fontSize': '13px'}
            )
        ]

    clear_disabled = len(active_sorts) == 0

    return active_sort_items, clear_disabled
