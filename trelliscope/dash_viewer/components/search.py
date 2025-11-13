"""
Global search component for searching across all metadata.
"""

from typing import List, Dict, Any
import dash_bootstrap_components as dbc
from dash import html, dcc


def create_search_panel() -> html.Div:
    """
    Create global search panel.

    Returns
    -------
    html.Div
        Search panel container with input and controls
    """
    return html.Div(
        [
            html.H6("Search", className='mb-3', style={'fontWeight': 'bold'}),

            # Search input
            html.Div(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("🔍", style={'fontSize': '14px'}),
                            dbc.Input(
                                id='global-search-input',
                                placeholder='Search all metadata...',
                                type='text',
                                debounce=True,  # Wait for user to stop typing
                                style={'fontSize': '13px'}
                            ),
                            dbc.Button(
                                "Clear",
                                id='clear-search-btn',
                                color='secondary',
                                size='sm',
                                outline=True,
                                style={'fontSize': '12px'}
                            )
                        ],
                        size='sm'
                    )
                ],
                className='mb-2'
            ),

            # Search results summary
            html.Div(
                id='search-results-summary',
                style={
                    'fontSize': '12px',
                    'color': '#6c757d',
                    'padding': '8px 0',
                    'fontStyle': 'italic'
                }
            ),

            # Search info
            html.Div(
                [
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.P(
                                        "Search searches across all text and factor columns.",
                                        style={'fontSize': '11px', 'margin': 0}
                                    ),
                                    html.P(
                                        "• Case-insensitive",
                                        style={'fontSize': '11px', 'margin': '4px 0 0 0'}
                                    ),
                                    html.P(
                                        "• Works with filters",
                                        style={'fontSize': '11px', 'margin': '2px 0 0 0'}
                                    )
                                ],
                                style={'padding': '8px'}
                            ),
                            style={'border': '1px solid #dee2e6', 'fontSize': '11px'}
                        ),
                        id='search-info-collapse',
                        is_open=False
                    ),
                    dbc.Button(
                        "ⓘ Info",
                        id='search-info-btn',
                        color='link',
                        size='sm',
                        style={'fontSize': '11px', 'padding': '2px 4px'}
                    )
                ],
                className='mt-2'
            )
        ],
        style={
            'padding': '15px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '4px',
            'marginBottom': '20px'
        }
    )


def search_dataframe(
    df,
    search_query: str,
    searchable_columns: List[str]
) -> tuple:
    """
    Search DataFrame for query string.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to search
    search_query : str
        Search query string
    searchable_columns : list
        List of column names to search in

    Returns
    -------
    tuple
        (filtered_df, match_count, total_count)
    """
    import pandas as pd

    if not search_query or not search_query.strip():
        # No search query - return all data
        return df, len(df), len(df)

    # Normalize search query (lowercase, strip whitespace)
    query = search_query.strip().lower()

    # Create boolean mask for matching rows
    matches = pd.Series([False] * len(df), index=df.index)

    # Search in each searchable column
    for col in searchable_columns:
        if col not in df.columns:
            continue

        # Convert column to string and search
        col_str = df[col].astype(str).str.lower()
        col_matches = col_str.str.contains(query, case=False, na=False, regex=False)
        matches = matches | col_matches

    # Filter DataFrame
    filtered_df = df[matches].copy()

    return filtered_df, len(filtered_df), len(df)


def get_searchable_columns(display_info: Dict[str, Any]) -> List[str]:
    """
    Get list of searchable column names from display metadata.

    Searchable types: factor, string, href, base

    Parameters
    ----------
    display_info : dict
        Display configuration

    Returns
    -------
    list
        List of searchable column names
    """
    searchable_types = {'factor', 'string', 'href', 'base'}
    searchable_cols = []

    for meta in display_info.get('metas', []):
        meta_type = meta.get('type')
        varname = meta.get('varname')

        # Include factor label columns (e.g., 'country_label')
        if meta_type in searchable_types and varname:
            searchable_cols.append(varname)

            # Also add label column for factors
            if meta_type == 'factor':
                label_col = f"{varname}_label"
                searchable_cols.append(label_col)

    return searchable_cols


def format_search_summary(match_count: int, total_count: int, search_query: str) -> str:
    """
    Format search results summary text.

    Parameters
    ----------
    match_count : int
        Number of matching panels
    total_count : int
        Total number of panels
    search_query : str
        Search query string

    Returns
    -------
    str
        Formatted summary text
    """
    if not search_query or not search_query.strip():
        return "No active search"

    if match_count == 0:
        return f"No matches for '{search_query}'"
    elif match_count == total_count:
        return f"All {total_count} panels match"
    else:
        return f"Found {match_count} of {total_count} panels"
