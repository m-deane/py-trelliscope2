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
    import sys
    print(f"[DEBUG FILTERS] Total filterable_metas: {len(filterable_metas)}", file=sys.stderr)
    print(f"[DEBUG FILTERS] Meta varnames: {[m.get('varname') for m in filterable_metas]}", file=sys.stderr)
    print(f"[DEBUG FILTERS] Meta types: {[m.get('type') for m in filterable_metas]}", file=sys.stderr)
    print(f"[DEBUG FILTERS] cog_data columns: {list(cog_data.columns)}", file=sys.stderr)
    
    filter_components = []

    for meta in filterable_metas:
        varname = meta['varname']
        meta_type = meta.get('type', 'string')

        # For factors, prefer label column if available (created by loader)
        if meta_type == 'factor':
            label_col = f"{varname}_label"
            if label_col in cog_data.columns:
                # Use label column which has the actual string values
                data = cog_data[label_col]
                import sys
                print(f"[DEBUG FILTERS] Factor {varname}: using label column {label_col}", file=sys.stderr)
            elif varname in cog_data.columns:
                # Fall back to index column
                data = cog_data[varname]
                import sys
                print(f"[DEBUG FILTERS] Factor {varname}: using index column", file=sys.stderr)
            else:
                import sys
                print(f"[DEBUG FILTERS] Factor {varname}: SKIPPING - no label or index column found", file=sys.stderr)
                continue
        elif varname not in cog_data.columns:
            import sys
            print(f"[DEBUG FILTERS] Skipping {varname} (type: {meta_type}): not in cog_data.columns", file=sys.stderr)
            continue
        else:
            # Get data for this variable
            data = cog_data[varname]
            import sys
            print(f"[DEBUG FILTERS] Processing {varname} (type: {meta_type}): found in cog_data", file=sys.stderr)

        # Create filter component based on type
        import sys
        print(f"[DEBUG FILTERS] >>> About to call create_filter_component for {varname} (type: {meta_type})", file=sys.stderr)
        try:
            filter_comp = create_filter_component(meta, data)
            print(f"[DEBUG FILTERS] >>> create_filter_component returned for {varname}: {type(filter_comp)}", file=sys.stderr)
        except Exception as e:
            print(f"[DEBUG FILTERS] >>> ERROR creating filter component for {varname}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            filter_comp = None
        
        if filter_comp is None:
            print(f"[DEBUG FILTERS] create_filter_component returned None for {varname} (type: {meta_type})", file=sys.stderr)
        else:
            print(f"[DEBUG FILTERS] Created filter component for {varname} (type: {meta_type})", file=sys.stderr)
            # Debug: check if it's a dropdown and has options
            if hasattr(filter_comp, 'options'):
                print(f"[DEBUG FILTERS] {varname} dropdown has {len(filter_comp.options) if filter_comp.options else 0} options", file=sys.stderr)
            if hasattr(filter_comp, 'id'):
                print(f"[DEBUG FILTERS] {varname} component id: {filter_comp.id}", file=sys.stderr)

        print(f"[DEBUG FILTERS] >>> About to check if filter_comp for {varname}: filter_comp={filter_comp}, is not None={filter_comp is not None}", file=sys.stderr)
        
        # Dash components (like dcc.Dropdown) are falsy in boolean context, so check is not None instead
        if filter_comp is not None:
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
            print(f"[DEBUG FILTERS] ✓ Added card for {varname} (type: {meta_type}). Total cards now: {len(filter_components)}", file=sys.stderr)
        else:
            print(f"[DEBUG FILTERS] ✗ SKIPPED adding card for {varname} (type: {meta_type}) - filter_comp is falsy!", file=sys.stderr)

    # Add clear filters button
    clear_button = dbc.Button(
        "Clear All Filters",
        id='clear-filters-btn',
        color='secondary',
        size='sm',
        className='w-100 mb-3'
    )

    import sys
    print(f"[DEBUG FILTERS] ✓✓✓ FINAL: Returning filter panel with {len(filter_components)} filter cards", file=sys.stderr)
    # Extract varnames from cards by checking card headers
    card_varnames = []
    for card in filter_components:
        if hasattr(card, 'children') and len(card.children) > 0:
            header = card.children[0]
            if hasattr(header, 'children') and len(header.children) > 0:
                card_varnames.append(str(header.children[0]))
    print(f"[DEBUG FILTERS] ✓✓✓ FINAL: Card headers: {card_varnames}", file=sys.stderr)
    
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
        Factor data (can be indices or labels)

    Returns
    -------
    dcc.Dropdown
        Multi-select dropdown component
    """
    varname = meta['varname']
    
    # Get value counts from the data
    # Note: If data comes from label column, it already has string values
    # If data comes from index column, it has 0-based numeric indices
    value_counts = data.value_counts()
    
    # If data contains numeric indices (0-based), map them to level strings
    levels = meta.get('levels', [])
    if levels and len(value_counts) > 0:
        sample_val = value_counts.index[0]
        # Check if values are numeric indices (not already strings)
        if isinstance(sample_val, (int, float)) and pd.notna(sample_val):
            # Map 0-based indices to level strings
            mapped_counts = {}
            for idx, count in value_counts.items():
                if isinstance(idx, (int, float)) and pd.notna(idx):
                    py_idx = int(idx)
                    if 0 <= py_idx < len(levels):
                        mapped_counts[levels[py_idx]] = count
                    else:
                        # Index out of range, keep as-is
                        mapped_counts[idx] = count
                else:
                    mapped_counts[idx] = count
            value_counts = pd.Series(mapped_counts)

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


def create_string_filter(meta: Dict[str, Any], data: pd.Series) -> dcc.Dropdown:
    """
    Create multi-select dropdown for string filtering.

    Parameters
    ----------
    meta : dict
        Meta configuration
    data : pd.Series
        String data

    Returns
    -------
    dcc.Dropdown
        Multi-select dropdown component
    """
    import sys
    varname = meta['varname']
    
    print(f"[DEBUG STRING FILTER] Creating string filter for {varname}", file=sys.stderr)
    print(f"[DEBUG STRING FILTER] Data type: {type(data)}, length: {len(data)}", file=sys.stderr)
    print(f"[DEBUG STRING FILTER] Sample values: {data.head().tolist()}", file=sys.stderr)
    print(f"[DEBUG STRING FILTER] Unique values: {data.unique()}", file=sys.stderr)

    # Get unique values with counts
    value_counts = data.value_counts()
    print(f"[DEBUG STRING FILTER] Value counts: {value_counts.to_dict()}", file=sys.stderr)
    
    # Create options with counts (limit to reasonable number for dropdown)
    # If too many unique values, show top N
    max_options = 100
    if len(value_counts) > max_options:
        # Show top N most common values
        value_counts = value_counts.head(max_options)
    
    options = [
        {
            'label': f"{value} ({count})",
            'value': str(value)
        }
        for value, count in value_counts.items()
        if pd.notna(value)
    ]
    
    print(f"[DEBUG STRING FILTER] Created {len(options)} options: {options}", file=sys.stderr)
    
    # Sort by label
    options.sort(key=lambda x: x['label'])

    dropdown = dcc.Dropdown(
        id={'type': 'filter', 'varname': varname},
        options=options,
        multi=True,
        placeholder=f"Select {meta.get('label', varname)}...",
        style={'fontSize': '13px'}
    )
    
    print(f"[DEBUG STRING FILTER] Dropdown created with id: {dropdown.id}, options count: {len(dropdown.options)}", file=sys.stderr)
    
    return dropdown
