"""
Unit tests for DisplayState class.
"""

import pytest
import pandas as pd
from trelliscope.dash_viewer.state import DisplayState


@pytest.fixture
def sample_display_info():
    """Sample display info for testing."""
    return {
        'name': 'test_display',
        'metas': [
            {'varname': 'category', 'type': 'factor', 'levels': ['A', 'B', 'C']},
            {'varname': 'value', 'type': 'number', 'digits': 1},
            {'varname': 'date', 'type': 'date'},
        ],
        'state': {
            'layout': {'ncol': 3, 'nrow': 2, 'page': 1, 'arrangement': 'row'},
            'labels': ['category', 'value'],
            'sorts': [],
            'filters': []
        }
    }


@pytest.fixture
def sample_data():
    """Sample cognostics data for testing."""
    return pd.DataFrame({
        'category': ['A', 'B', 'C', 'A', 'B'],
        'category_label': ['Alpha', 'Beta', 'Gamma', 'Alpha', 'Beta'],
        'value': [10, 20, 30, 15, 25],
        'date': pd.to_datetime(['2020-01-01', '2020-02-01', '2020-03-01',
                                 '2020-04-01', '2020-05-01']),
        'panelKey': ['0', '1', '2', '3', '4']
    })


class TestDisplayStateInitialization:
    """Test DisplayState initialization."""

    def test_init_with_defaults(self, sample_display_info):
        """Test initialization with default values."""
        state = DisplayState(display_info=sample_display_info)

        assert state.ncol == 3
        assert state.nrow == 2
        assert state.current_page == 1
        assert state.arrangement == 'row'
        assert state.active_labels == ['category', 'value']
        assert state.active_filters == {}
        assert state.active_sorts == []

    def test_panels_per_page(self, sample_display_info):
        """Test panels_per_page calculation."""
        state = DisplayState(display_info=sample_display_info)
        assert state.panels_per_page == 6  # 3 * 2

    def test_init_from_display_state(self):
        """Test initialization from display state."""
        display_info = {
            'name': 'test',
            'metas': [],
            'state': {
                'layout': {'ncol': 4, 'nrow': 3, 'page': 2, 'arrangement': 'col'},
                'labels': ['x', 'y'],
                'sorts': [{'varname': 'x', 'dir': 'desc'}],
                'filters': []
            }
        }

        state = DisplayState(display_info=display_info)

        assert state.ncol == 4
        assert state.nrow == 3
        assert state.current_page == 2
        assert state.arrangement == 'col'
        assert state.active_sorts == [('x', 'desc')]


class TestDisplayStateFiltering:
    """Test filtering functionality."""

    def test_filter_factor(self, sample_display_info, sample_data):
        """Test factor filtering."""
        state = DisplayState(display_info=sample_display_info)
        state.set_filter('category', ['Alpha', 'Gamma'])

        filtered = state.filter_data(sample_data)

        assert len(filtered) == 3  # 2 Alpha + 1 Gamma
        assert set(filtered['category_label']) == {'Alpha', 'Gamma'}

    def test_filter_number_range(self, sample_display_info, sample_data):
        """Test number range filtering."""
        state = DisplayState(display_info=sample_display_info)
        state.set_filter('value', [15, 25])

        filtered = state.filter_data(sample_data)

        assert len(filtered) == 3  # values 15, 20, 25
        assert filtered['value'].min() >= 15
        assert filtered['value'].max() <= 25

    def test_filter_date_range(self, sample_display_info, sample_data):
        """Test date range filtering."""
        state = DisplayState(display_info=sample_display_info)
        state.set_filter('date', ['2020-02-01', '2020-04-01'])

        filtered = state.filter_data(sample_data)

        assert len(filtered) == 3  # Feb, Mar, Apr
        assert filtered['date'].min() >= pd.to_datetime('2020-02-01')
        assert filtered['date'].max() <= pd.to_datetime('2020-04-01')

    def test_multiple_filters(self, sample_display_info, sample_data):
        """Test combining multiple filters."""
        state = DisplayState(display_info=sample_display_info)
        state.set_filter('category', ['Alpha', 'Beta'])
        state.set_filter('value', [10, 20])

        filtered = state.filter_data(sample_data)

        assert len(filtered) == 3  # Alpha(10), Beta(20), Alpha(15)

    def test_clear_filters(self, sample_display_info, sample_data):
        """Test clearing all filters."""
        state = DisplayState(display_info=sample_display_info)
        state.set_filter('category', ['Alpha'])
        state.set_filter('value', [10, 15])

        state.clear_filters()

        assert state.active_filters == {}
        filtered = state.filter_data(sample_data)
        assert len(filtered) == len(sample_data)

    def test_set_filter_none_clears(self, sample_display_info):
        """Test that setting filter to None clears it."""
        state = DisplayState(display_info=sample_display_info)
        state.set_filter('category', ['A'])
        assert 'category' in state.active_filters

        state.set_filter('category', None)
        assert 'category' not in state.active_filters


class TestDisplayStateSorting:
    """Test sorting functionality."""

    def test_sort_single_column_asc(self, sample_display_info, sample_data):
        """Test single column ascending sort."""
        state = DisplayState(display_info=sample_display_info)
        state.set_sort('value', 'asc')

        sorted_data = state.sort_data(sample_data)

        assert sorted_data['value'].tolist() == [10, 15, 20, 25, 30]

    def test_sort_single_column_desc(self, sample_display_info, sample_data):
        """Test single column descending sort."""
        state = DisplayState(display_info=sample_display_info)
        state.set_sort('value', 'desc')

        sorted_data = state.sort_data(sample_data)

        assert sorted_data['value'].tolist() == [30, 25, 20, 15, 10]

    def test_sort_multiple_columns(self, sample_display_info, sample_data):
        """Test multi-column sorting."""
        state = DisplayState(display_info=sample_display_info)
        state.set_sort('category', 'asc')  # Primary
        state.set_sort('value', 'desc')     # Secondary (added first, so has priority)

        sorted_data = state.sort_data(sample_data)

        # Should sort by value desc first, then category asc
        values = sorted_data['value'].tolist()
        assert values[0] > values[-1]  # Descending by value

    def test_sort_priority(self, sample_display_info, sample_data):
        """Test sort priority (first added = highest priority)."""
        state = DisplayState(display_info=sample_display_info)
        state.set_sort('value', 'asc')
        state.set_sort('category', 'desc')

        # category is added second but should be first in priority
        assert state.active_sorts == [('category', 'desc'), ('value', 'asc')]

    def test_remove_sort(self, sample_display_info):
        """Test removing a sort."""
        state = DisplayState(display_info=sample_display_info)
        state.set_sort('value', 'asc')
        state.set_sort('category', 'desc')

        state.remove_sort('value')

        assert state.active_sorts == [('category', 'desc')]

    def test_clear_sorts(self, sample_display_info):
        """Test clearing all sorts."""
        state = DisplayState(display_info=sample_display_info)
        state.set_sort('value', 'asc')
        state.set_sort('category', 'desc')

        state.clear_sorts()

        assert state.active_sorts == []

    def test_sort_with_no_sorts(self, sample_display_info, sample_data):
        """Test that sort_data returns unchanged data when no sorts."""
        state = DisplayState(display_info=sample_display_info)

        sorted_data = state.sort_data(sample_data)

        # Should return same order (may be copy)
        assert len(sorted_data) == len(sample_data)


class TestDisplayStatePagination:
    """Test pagination functionality."""

    def test_get_page_data_first_page(self, sample_display_info, sample_data):
        """Test getting first page of data."""
        state = DisplayState(display_info=sample_display_info)
        state.set_layout(ncol=2, nrow=1)  # 2 panels per page

        page_data = state.get_page_data(sample_data)

        assert len(page_data) == 2
        assert page_data.index.tolist() == [0, 1]

    def test_get_page_data_second_page(self, sample_display_info, sample_data):
        """Test getting second page of data."""
        state = DisplayState(display_info=sample_display_info)
        state.set_layout(ncol=2, nrow=1)  # 2 panels per page
        state.set_page(2)

        page_data = state.get_page_data(sample_data)

        assert len(page_data) == 2
        assert page_data.index.tolist() == [2, 3]

    def test_get_page_data_last_partial_page(self, sample_display_info, sample_data):
        """Test getting last page when it's partial."""
        state = DisplayState(display_info=sample_display_info)
        state.set_layout(ncol=2, nrow=1)  # 2 panels per page
        state.set_page(3)  # Last page (5 total panels)

        page_data = state.get_page_data(sample_data)

        assert len(page_data) == 1  # Only 1 panel left
        assert page_data.index.tolist() == [4]

    def test_get_total_pages(self, sample_display_info):
        """Test total pages calculation."""
        state = DisplayState(display_info=sample_display_info)
        state.set_layout(ncol=2, nrow=1)  # 2 per page

        # 5 panels = 3 pages (2 + 2 + 1)
        assert state.get_total_pages(5) == 3

        # 4 panels = 2 pages (2 + 2)
        assert state.get_total_pages(4) == 2

        # 0 panels = 0 pages
        assert state.get_total_pages(0) == 0

    def test_next_page(self, sample_display_info):
        """Test next page navigation."""
        state = DisplayState(display_info=sample_display_info)
        assert state.current_page == 1

        state.next_page(total_pages=3)
        assert state.current_page == 2

        state.next_page(total_pages=3)
        assert state.current_page == 3

        # Should not go beyond total pages
        state.next_page(total_pages=3)
        assert state.current_page == 3

    def test_prev_page(self, sample_display_info):
        """Test previous page navigation."""
        state = DisplayState(display_info=sample_display_info)
        state.set_page(3)

        state.prev_page()
        assert state.current_page == 2

        state.prev_page()
        assert state.current_page == 1

        # Should not go below 1
        state.prev_page()
        assert state.current_page == 1


class TestDisplayStateLayout:
    """Test layout management."""

    def test_set_layout(self, sample_display_info):
        """Test changing layout."""
        state = DisplayState(display_info=sample_display_info)

        state.set_layout(ncol=4, nrow=3, arrangement='col')

        assert state.ncol == 4
        assert state.nrow == 3
        assert state.arrangement == 'col'
        assert state.panels_per_page == 12

    def test_set_layout_resets_page(self, sample_display_info):
        """Test that layout change resets to page 1."""
        state = DisplayState(display_info=sample_display_info)
        state.set_page(3)

        state.set_layout(ncol=4)

        assert state.current_page == 1

    def test_set_layout_minimum_values(self, sample_display_info):
        """Test that layout enforces minimum values."""
        state = DisplayState(display_info=sample_display_info)

        state.set_layout(ncol=0, nrow=0)

        assert state.ncol == 1
        assert state.nrow == 1


class TestDisplayStateViews:
    """Test view save/load functionality."""

    def test_save_view(self, sample_display_info):
        """Test saving current state as view."""
        state = DisplayState(display_info=sample_display_info)
        state.set_filter('category', ['A', 'B'])
        state.set_sort('value', 'desc')
        state.set_layout(ncol=4, nrow=2)

        view = state.save_view('my_view')

        assert view['name'] == 'my_view'
        assert 'state' in view
        assert view['state']['layout']['ncol'] == 4
        assert view['state']['layout']['nrow'] == 2
        assert len(view['state']['sorts']) == 1
        assert len(view['state']['filters']) == 1

    def test_load_view(self, sample_display_info):
        """Test loading a saved view."""
        state = DisplayState(display_info=sample_display_info)

        # Create a view
        view = {
            'name': 'test_view',
            'state': {
                'layout': {'ncol': 5, 'nrow': 3, 'page': 1, 'arrangement': 'col'},
                'labels': ['value'],
                'sorts': [{'varname': 'value', 'dir': 'asc'}],
                'filters': [{'varname': 'category', 'value': ['A']}]
            }
        }

        state.load_view(view)

        assert state.ncol == 5
        assert state.nrow == 3
        assert state.arrangement == 'col'
        assert state.active_labels == ['value']
        assert state.active_sorts == [('value', 'asc')]
        assert state.active_filters == {'category': ['A']}

    def test_to_dict(self, sample_display_info):
        """Test converting state to dictionary."""
        state = DisplayState(display_info=sample_display_info)
        state.set_filter('category', ['A'])
        state.set_sort('value', 'desc')

        state_dict = state.to_dict()

        assert 'active_filters' in state_dict
        assert 'active_sorts' in state_dict
        assert 'current_page' in state_dict
        assert 'ncol' in state_dict
        assert 'nrow' in state_dict
        assert state_dict['active_filters'] == {'category': ['A']}
        assert state_dict['active_sorts'] == [('value', 'desc')]


class TestDisplayStateCombined:
    """Test combined filter+sort+paginate workflows."""

    def test_filter_sort_paginate(self, sample_display_info, sample_data):
        """Test complete workflow: filter → sort → paginate."""
        state = DisplayState(display_info=sample_display_info)

        # Filter
        state.set_filter('value', [15, 30])  # Gets 15, 20, 25, 30
        filtered = state.filter_data(sample_data)
        assert len(filtered) == 4

        # Sort
        state.set_sort('value', 'desc')
        sorted_data = state.sort_data(filtered)
        assert sorted_data['value'].tolist() == [30, 25, 20, 15]

        # Paginate (2 per page)
        state.set_layout(ncol=2, nrow=1)
        page1 = state.get_page_data(sorted_data)
        assert len(page1) == 2
        assert page1['value'].tolist() == [30, 25]

        state.set_page(2)
        page2 = state.get_page_data(sorted_data)
        assert len(page2) == 2
        assert page2['value'].tolist() == [20, 15]
