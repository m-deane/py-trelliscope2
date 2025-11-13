"""
Filter components for different meta types.
"""

from typing import Dict, Any, List
import pandas as pd

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_filter_panel(
    filterable_metas: List[Dict[str, Any]],
    cog_data: pd.DataFrame
) -> html.Div:
    """
    Create filter panel with all filter controls.

    Parameters
    ----------
    filterable_metas : list
        List of meta dictionaries for filterable variables
    cog_data : pd.DataFrame
        Cognostics data for determining filter ranges

    Returns
    -------
    html.Div
        Filter panel container
    """
    filter_components = []

    for meta in filterable_metas:
        varname = meta['varname']

        if varname not in cog_data.columns:
            continue

        # Get data for this variable
        data = cog_data[varname]

        # Create filter component based on type
        filter_comp = create_filter_component(meta, data)

        if filter_comp:
            # Wrap in card
            card = dbc.Card(
                [
                    dbc.CardHeader(
                        meta.get('label', varname),
                        style={'fontSize': '14px', 'fontWeight': 'bold'}
                    ),
                    dbc.CardBody(
                        filter_comp,
                        style={'padding': '10px'}
                    )
                ],
                className='mb-3',
                style={'border': '1px solid #dee2e6'}
            )

            filter_components.append(card)

    # Add clear filters button
    clear_button = dbc.Button(
        "Clear All Filters",
        id='clear-filters-btn',
        color='secondary',
        size='sm',
        className='w-100 mb-3'
    )

    return html.Div(
        [
            html.H5("Filters", className='mb-3', style={'fontWeight': 'bold'}),
            clear_button
        ] + filter_components,
        id='filter-panel',
        style={
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRight': '1px solid #dee2e6',
            'height': '100vh',
            'overflowY': 'auto'
        }
    )


def create_filter_component(
    meta: Dict[str, Any],
    data: pd.Series
) -> Any:
    """
    Create filter component based on meta type.

    Parameters
    ----------
    meta : dict
        Meta configuration
    data : pd.Series
        Data for this variable

    Returns
    -------
    component
        Dash component for filtering
    """
    varname = meta['varname']
    meta_type = meta.get('type', 'string')

    if meta_type == 'factor':
        return create_factor_filter(meta, data)

    elif meta_type in ['number', 'currency']:
        return create_number_filter(meta, data)

    elif meta_type == 'date':
        return create_date_filter(meta, data)

    elif meta_type == 'time':
        return create_datetime_filter(meta, data)

    elif meta_type == 'string':
        return create_string_filter(meta, data)

    else:
        return None


def create_factor_filter(meta: Dict[str, Any], data: pd.Series) -> dcc.Dropdown:
    """
    Create multi-select dropdown for factor filtering.

    Parameters
    ----------
    meta : dict
        Meta configuration
    data : pd.Series
        Factor data

    Returns
    -------
    dcc.Dropdown
        Multi-select dropdown component
    """
    varname = meta['varname']

    # Check if we have label column
    if f"{varname}_label" in data.index:
        # Use labels
        value_counts = data.value_counts()
    else:
        value_counts = data.value_counts()

    # Create options with counts
    options = [
        {
            'label': f"{level} ({count})",
            'value': str(level)
        }
        for level, count in value_counts.items()
        if pd.notna(level)
    ]

    # Sort by label
    options.sort(key=lambda x: x['label'])

    return dcc.Dropdown(
        id={'type': 'filter', 'varname': varname},
        options=options,
        multi=True,
        placeholder=f"Select {meta.get('label', varname)}...",
        style={'fontSize': '13px'}
    )


def create_number_filter(meta: Dict[str, Any], data: pd.Series) -> dcc.RangeSlider:
    """
    Create range slider for number/currency filtering.

    Parameters
    ----------
    meta : dict
        Meta configuration
    data : pd.Series
        Numeric data

    Returns
    -------
    dcc.RangeSlider
        Range slider component
    """
    varname = meta['varname']

    # Remove NaN values
    clean_data = data.dropna()

    if clean_data.empty:
        return html.Div("No data available")

    min_val = float(clean_data.min())
    max_val = float(clean_data.max())

    if min_val == max_val:
        return html.Div(f"Value: {min_val}")

    digits = meta.get('digits', 1)

    # Create marks (min, max, maybe middle)
    marks = {
        min_val: f"{min_val:.{digits}f}",
        max_val: f"{max_val:.{digits}f}"
    }

    # Add middle mark if range is large enough
    if (max_val - min_val) > 0.01:
        mid_val = (min_val + max_val) / 2
        marks[mid_val] = f"{mid_val:.{digits}f}"

    return html.Div([
        dcc.RangeSlider(
            id={'type': 'filter', 'varname': varname},
            min=min_val,
            max=max_val,
            value=[min_val, max_val],
            marks=marks,
            tooltip={
                'placement': 'bottom',
                'always_visible': False
            },
            allowCross=False
        )
    ])


def create_date_filter(meta: Dict[str, Any], data: pd.Series) -> dcc.DatePickerRange:
    """
    Create date range picker for date filtering.

    Parameters
    ----------
    meta : dict
        Meta configuration
    data : pd.Series
        Date data

    Returns
    -------
    dcc.DatePickerRange
        Date picker component
    """
    varname = meta['varname']

    # Convert to datetime
    date_data = pd.to_datetime(data, errors='coerce').dropna()

    if date_data.empty:
        return html.Div("No date data available")

    min_date = date_data.min()
    max_date = date_data.max()

    return dcc.DatePickerRange(
        id={'type': 'filter', 'varname': varname},
        start_date=min_date,
        end_date=max_date,
        min_date_allowed=min_date,
        max_date_allowed=max_date,
        display_format='YYYY-MM-DD',
        style={'fontSize': '13px'}
    )


def create_datetime_filter(meta: Dict[str, Any], data: pd.Series) -> dcc.DatePickerRange:
    """
    Create datetime range picker for time filtering.

    Parameters
    ----------
    meta : dict
        Meta configuration
    data : pd.Series
        Datetime data

    Returns
    -------
    dcc.DatePickerRange
        Date picker component (note: time component handled separately)
    """
    # For now, use same as date filter
    # TODO: Add time selection component
    return create_date_filter(meta, data)


def create_string_filter(meta: Dict[str, Any], data: pd.Series) -> dcc.Input:
    """
    Create text input for string filtering.

    Parameters
    ----------
    meta : dict
        Meta configuration
    data : pd.Series
        String data

    Returns
    -------
    dcc.Input
        Text input component
    """
    varname = meta['varname']

    return dcc.Input(
        id={'type': 'filter', 'varname': varname},
        type='text',
        placeholder=f"Search {meta.get('label', varname)}...",
        debounce=True,
        style={
            'width': '100%',
            'fontSize': '13px',
            'padding': '5px'
        }
    )
