"""
Display state management for Dash viewer.

Manages filters, sorts, pagination, layout, and views.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
from copy import deepcopy


@dataclass
class DisplayState:
    """
    Manages current display state (filters, sorts, layout, etc.).

    Attributes
    ----------
    display_info : dict
        Display configuration from displayInfo.json
    active_filters : dict
        Active filters by variable name: {varname: filter_value}
    active_sorts : list
        Active sorts as [(varname, direction), ...]
    current_page : int
        Current page number (1-indexed)
    ncol : int
        Number of columns in grid layout
    nrow : int
        Number of rows in grid layout
    arrangement : str
        Panel arrangement: "row" or "col"
    active_labels : list
        List of variable names to display as labels
    panels_per_page : int
        Number of panels per page (ncol * nrow)
    """

    display_info: Dict[str, Any]
    active_filters: Dict[str, Any] = field(default_factory=dict)
    active_sorts: List[Tuple[str, str]] = field(default_factory=list)
    current_page: int = 1
    ncol: int = 3
    nrow: int = 2
    arrangement: str = "row"
    active_labels: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize state from display info."""
        # Set initial layout from display state
        if 'state' in self.display_info:
            state = self.display_info['state']

            if 'layout' in state:
                layout = state['layout']
                self.ncol = layout.get('ncol', self.ncol)
                self.nrow = layout.get('nrow', self.nrow)
                self.arrangement = layout.get('arrangement', self.arrangement)
                self.current_page = layout.get('page', self.current_page)

            if 'labels' in state:
                self.active_labels = state['labels']

            if 'sorts' in state:
                # Convert from display format to tuple format
                self.active_sorts = [
                    (s['varname'], s.get('dir', 'asc'))
                    for s in state['sorts']
                ]

    @property
    def panels_per_page(self) -> int:
        """Calculate panels per page from layout."""
        return self.ncol * self.nrow

    def filter_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply current filters to data.

        Parameters
        ----------
        data : pd.DataFrame
            Input cognostics data

        Returns
        -------
        pd.DataFrame
            Filtered data
        """
        if not self.active_filters:
            return data.copy()

        filtered = data.copy()

        for varname, filter_value in self.active_filters.items():
            if filter_value is None or varname not in filtered.columns:
                continue

            # Get meta for this variable
            meta = self._get_meta(varname)
            if not meta:
                continue

            meta_type = meta.get('type')

            # Apply filter based on type
            if meta_type == 'factor':
                # Multi-select filter
                if isinstance(filter_value, list) and filter_value:
                    # Use label column if available
                    label_col = f"{varname}_label"
                    col = label_col if label_col in filtered.columns else varname
                    filtered = filtered[filtered[col].isin(filter_value)]

            elif meta_type in ['number', 'currency']:
                # Range filter [min, max]
                if isinstance(filter_value, (list, tuple)) and len(filter_value) == 2:
                    min_val, max_val = filter_value
                    filtered = filtered[
                        (filtered[varname] >= min_val) &
                        (filtered[varname] <= max_val)
                    ]

            elif meta_type in ['date', 'time']:
                # Date range filter
                if isinstance(filter_value, (list, tuple)) and len(filter_value) == 2:
                    start_date, end_date = filter_value
                    if start_date and end_date:
                        filtered = filtered[
                            (pd.to_datetime(filtered[varname]) >= pd.to_datetime(start_date)) &
                            (pd.to_datetime(filtered[varname]) <= pd.to_datetime(end_date))
                        ]

            elif meta_type == 'string':
                # Text search filter
                if isinstance(filter_value, str) and filter_value:
                    filtered = filtered[
                        filtered[varname].astype(str).str.contains(
                            filter_value, case=False, na=False
                        )
                    ]

        return filtered

    def sort_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply current sorts to data.

        Parameters
        ----------
        data : pd.DataFrame
            Input data (possibly filtered)

        Returns
        -------
        pd.DataFrame
            Sorted data
        """
        if not self.active_sorts:
            return data

        sorted_data = data.copy()

        # Apply sorts in order (first sort has highest priority)
        sort_cols = []
        sort_ascending = []

        for varname, direction in self.active_sorts:
            if varname in sorted_data.columns:
                sort_cols.append(varname)
                sort_ascending.append(direction == 'asc')

        if sort_cols:
            sorted_data = sorted_data.sort_values(
                by=sort_cols,
                ascending=sort_ascending
            )

        return sorted_data

    def get_page_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Get current page of panels from data.

        Parameters
        ----------
        data : pd.DataFrame
            Input data (filtered and sorted)

        Returns
        -------
        pd.DataFrame
            Data for current page only
        """
        start_idx = (self.current_page - 1) * self.panels_per_page
        end_idx = start_idx + self.panels_per_page

        return data.iloc[start_idx:end_idx]

    def get_total_pages(self, total_panels: int) -> int:
        """
        Calculate total number of pages.

        Parameters
        ----------
        total_panels : int
            Total number of panels (after filtering)

        Returns
        -------
        int
            Total number of pages
        """
        if total_panels == 0:
            return 0

        return (total_panels + self.panels_per_page - 1) // self.panels_per_page

    def set_filter(self, varname: str, value: Any):
        """
        Set filter for a variable.

        Parameters
        ----------
        varname : str
            Variable name
        value : any
            Filter value (format depends on meta type)
        """
        if value is None or value == [] or value == '':
            # Clear filter
            self.active_filters.pop(varname, None)
        else:
            self.active_filters[varname] = value

        # Reset to page 1 when filter changes
        self.current_page = 1

    def set_sort(self, varname: str, direction: str = 'asc'):
        """
        Set or toggle sort for a variable.

        Parameters
        ----------
        varname : str
            Variable name
        direction : str
            Sort direction: "asc" or "desc"
        """
        # Remove existing sort for this variable
        self.active_sorts = [
            (v, d) for v, d in self.active_sorts if v != varname
        ]

        # Add new sort (at beginning for highest priority)
        self.active_sorts.insert(0, (varname, direction))

    def remove_sort(self, varname: str):
        """
        Remove sort for a variable.

        Parameters
        ----------
        varname : str
            Variable name
        """
        self.active_sorts = [
            (v, d) for v, d in self.active_sorts if v != varname
        ]

    def clear_filters(self):
        """Clear all active filters."""
        self.active_filters = {}
        self.current_page = 1

    def clear_sorts(self):
        """Clear all active sorts."""
        self.active_sorts = []

    def set_layout(self, ncol: Optional[int] = None, nrow: Optional[int] = None,
                   arrangement: Optional[str] = None):
        """
        Update layout settings.

        Parameters
        ----------
        ncol : int, optional
            Number of columns
        nrow : int, optional
            Number of rows
        arrangement : str, optional
            Arrangement: "row" or "col"
        """
        if ncol is not None:
            self.ncol = max(1, ncol)
        if nrow is not None:
            self.nrow = max(1, nrow)
        if arrangement is not None:
            self.arrangement = arrangement

        # Reset to page 1 when layout changes
        self.current_page = 1

    def set_page(self, page: int):
        """
        Set current page.

        Parameters
        ----------
        page : int
            Page number (1-indexed)
        """
        self.current_page = max(1, page)

    def next_page(self, total_pages: int):
        """Go to next page."""
        self.current_page = min(self.current_page + 1, total_pages)

    def prev_page(self):
        """Go to previous page."""
        self.current_page = max(1, self.current_page - 1)

    def save_view(self, name: str) -> Dict[str, Any]:
        """
        Save current state as a named view.

        Parameters
        ----------
        name : str
            View name

        Returns
        -------
        dict
            View configuration
        """
        return {
            'name': name,
            'state': {
                'layout': {
                    'ncol': self.ncol,
                    'nrow': self.nrow,
                    'page': self.current_page,
                    'arrangement': self.arrangement
                },
                'labels': self.active_labels,
                'sorts': [
                    {'varname': v, 'dir': d}
                    for v, d in self.active_sorts
                ],
                'filters': [
                    {'varname': v, 'value': val}
                    for v, val in self.active_filters.items()
                ]
            }
        }

    def load_view(self, view: Dict[str, Any]):
        """
        Restore state from a saved view.

        Parameters
        ----------
        view : dict
            View configuration
        """
        state = view.get('state', {})

        # Restore layout
        if 'layout' in state:
            layout = state['layout']
            self.ncol = layout.get('ncol', self.ncol)
            self.nrow = layout.get('nrow', self.nrow)
            self.current_page = layout.get('page', 1)
            self.arrangement = layout.get('arrangement', self.arrangement)

        # Restore labels
        if 'labels' in state:
            self.active_labels = state['labels']

        # Restore sorts
        if 'sorts' in state:
            self.active_sorts = [
                (s['varname'], s.get('dir', 'asc'))
                for s in state['sorts']
            ]

        # Restore filters
        if 'filters' in state:
            self.active_filters = {
                f['varname']: f['value']
                for f in state['filters']
            }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state to dictionary.

        Returns
        -------
        dict
            State as dictionary
        """
        return {
            'active_filters': self.active_filters,
            'active_sorts': self.active_sorts,
            'current_page': self.current_page,
            'ncol': self.ncol,
            'nrow': self.nrow,
            'arrangement': self.arrangement,
            'active_labels': self.active_labels
        }

    def _get_meta(self, varname: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a variable."""
        for meta in self.display_info.get('metas', []):
            if meta.get('varname') == varname:
                return meta
        return None
