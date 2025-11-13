"""
Control components for pagination, layout, etc.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_control_bar(
    display_name: str,
    total_panels: int,
    current_page: int,
    total_pages: int,
    ncol: int,
    nrow: int
) -> html.Div:
    """
    Create control bar with pagination and layout controls.

    Parameters
    ----------
    display_name : str
        Display name
    total_panels : int
        Total number of panels (after filtering)
    current_page : int
        Current page number
    total_pages : int
        Total number of pages
    ncol : int
        Number of columns
    nrow : int
        Number of rows

    Returns
    -------
    html.Div
        Control bar container
    """
    # Calculate panel range for current page
    panels_per_page = ncol * nrow
    start_panel = (current_page - 1) * panels_per_page + 1
    end_panel = min(current_page * panels_per_page, total_panels)

    return html.Div(
        [
            dbc.Row(
                [
                    # Left section: Display info
                    dbc.Col(
                        [
                            html.H4(
                                display_name,
                                className='mb-0',
                                style={'fontWeight': 'bold'}
                            ),
                            html.Small(
                                f"Showing {start_panel}-{end_panel} of {total_panels} panels",
                                id='panel-count',
                                className='text-muted'
                            )
                        ],
                        width=4,
                        style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}
                    ),

                    # Middle section: Pagination
                    dbc.Col(
                        [
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "◀ Previous",
                                        id='prev-page-btn',
                                        size='sm',
                                        color='primary',
                                        outline=True,
                                        disabled=current_page <= 1
                                    ),
                                    dbc.Button(
                                        f"Page {current_page} of {total_pages}",
                                        id='page-info',
                                        size='sm',
                                        color='light',
                                        disabled=True,
                                        style={'minWidth': '150px'}
                                    ),
                                    dbc.Button(
                                        "Next ▶",
                                        id='next-page-btn',
                                        size='sm',
                                        color='primary',
                                        outline=True,
                                        disabled=current_page >= total_pages
                                    )
                                ],
                                className='me-2'
                            ),
                        ],
                        width=4,
                        style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}
                    ),

                    # Right section: Layout controls
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Label("Columns:", className='me-2', style={'fontSize': '13px'}),
                                    dcc.Dropdown(
                                        id='ncol-select',
                                        options=[{'label': str(i), 'value': i} for i in range(1, 7)],
                                        value=ncol,
                                        clearable=False,
                                        style={'width': '70px', 'fontSize': '13px'},
                                        className='d-inline-block me-3'
                                    ),
                                    html.Label("Rows:", className='me-2', style={'fontSize': '13px'}),
                                    dcc.Dropdown(
                                        id='nrow-select',
                                        options=[{'label': str(i), 'value': i} for i in range(1, 7)],
                                        value=nrow,
                                        clearable=False,
                                        style={'width': '70px', 'fontSize': '13px'},
                                        className='d-inline-block'
                                    )
                                ],
                                style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'flex-end'}
                            )
                        ],
                        width=4
                    )
                ],
                className='g-0',
                align='center'
            )
        ],
        style={
            'padding': '15px 20px',
            'backgroundColor': '#f8f9fa',
            'borderBottom': '1px solid #dee2e6'
        }
    )


def create_header(display_info: dict) -> html.Div:
    """
    Create display header with title and description.

    Parameters
    ----------
    display_info : dict
        Display configuration

    Returns
    -------
    html.Div
        Header container
    """
    name = display_info.get('name', 'Trelliscope Display')
    description = display_info.get('description', '')

    return html.Div(
        [
            html.H3(
                name,
                style={
                    'margin': 0,
                    'fontWeight': 'bold',
                    'color': '#212529'
                }
            ),
            html.P(
                description,
                style={
                    'margin': '5px 0 0 0',
                    'color': '#6c757d',
                    'fontSize': '14px'
                }
            ) if description else html.Div()
        ],
        style={
            'padding': '20px',
            'backgroundColor': 'white',
            'borderBottom': '2px solid #007bff'
        }
    )
