"""
Unit tests for DisplayLoader class.
"""

import pytest
import json
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from trelliscope.dash_viewer.loader import DisplayLoader


@pytest.fixture
def temp_display_dir():
    """Create temporary display directory."""
    temp_dir = tempfile.mkdtemp()
    display_dir = Path(temp_dir) / "test_display"
    display_dir.mkdir(parents=True)

    # Create panels directory
    panels_dir = display_dir / "panels"
    panels_dir.mkdir()

    # Create dummy panel files
    for i in range(3):
        (panels_dir / f"{i}.png").touch()

    yield display_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_display_info():
    """Sample displayInfo.json structure."""
    return {
        "name": "test_display",
        "description": "Test display",
        "n": 3,
        "primarypanel": "panel",
        "metas": [
            {
                "varname": "country",
                "label": "Country",
                "type": "factor",
                "levels": ["USA", "UK", "France"]
            },
            {
                "varname": "gdp",
                "label": "GDP",
                "type": "number",
                "digits": 2
            },
            {
                "varname": "date",
                "label": "Date",
                "type": "date"
            },
            {
                "varname": "panel",
                "label": "Panel",
                "type": "panel_src"
            }
        ],
        "cogData": [
            {"panelKey": "0", "country": 1, "gdp": 21.4, "date": "2020-01-01", "panel": "panels/0.png"},
            {"panelKey": "1", "country": 2, "gdp": 2.8, "date": "2020-02-01", "panel": "panels/1.png"},
            {"panelKey": "2", "country": 3, "gdp": 2.7, "date": "2020-03-01", "panel": "panels/2.png"}
        ],
        "state": {
            "layout": {"ncol": 2, "nrow": 2, "page": 1, "arrangement": "row"},
            "labels": ["country", "gdp"],
            "sorts": [],
            "filters": []
        },
        "panelInterface": {
            "type": "file",
            "base": "panels"
        }
    }


class TestDisplayLoaderInitialization:
    """Test DisplayLoader initialization."""

    def test_init_with_valid_path(self, temp_display_dir, sample_display_info):
        """Test initialization with valid display path."""
        # Write displayInfo.json
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)

        assert loader.display_path == temp_display_dir
        assert loader._display_info is None
        assert loader._cog_data is None

    def test_init_with_nonexistent_path(self):
        """Test initialization with nonexistent path."""
        with pytest.raises(FileNotFoundError):
            loader = DisplayLoader(Path("/nonexistent/path"))
            loader.load()


class TestDisplayLoaderLoading:
    """Test display info loading."""

    def test_load_single_display(self, temp_display_dir, sample_display_info):
        """Test loading single display."""
        # Write displayInfo.json
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        result = loader.load()

        assert result is not None
        assert 'display_info' in result
        assert 'cog_data' in result
        assert result["display_info"]["name"] == "test_display"
        assert len(result["cog_data"]) == 3

    def test_load_multi_display(self, temp_display_dir, sample_display_info):
        """Test loading multi-display structure."""
        # Create nested structure
        displays_dir = temp_display_dir / "displays"
        displays_dir.mkdir()

        display1_dir = displays_dir / "display1"
        display1_dir.mkdir()
        (display1_dir / "panels").mkdir()

        # Write displayInfo.json
        info_path = display1_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(display1_dir)
        result = loader.load()

        assert result is not None
        assert loader.display_info["name"] == "test_display"

    def test_load_returns_display_data(self, temp_display_dir, sample_display_info):
        """Test that load() returns all required data."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)

        result = loader.load()

        # Check all required keys present
        assert 'display_info' in result
        assert 'cog_data' in result
        assert 'panel_base_path' in result
        assert 'display_name' in result


class TestFactorIndexConversion:
    """Test factor index conversion (1-based to 0-based)."""

    def test_convert_factor_indices(self, temp_display_dir, sample_display_info):
        """Test factor index conversion from 1-based to 0-based."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        # Check that factor indices are converted
        assert loader.cog_data.loc[0, 'country'] == 0  # Was 1
        assert loader.cog_data.loc[1, 'country'] == 1  # Was 2
        assert loader.cog_data.loc[2, 'country'] == 2  # Was 3

    def test_non_factor_values_unchanged(self, temp_display_dir, sample_display_info):
        """Test that non-factor values are not changed."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        # Check that number values are unchanged
        assert loader.cog_data.loc[0, 'gdp'] == 21.4
        assert loader.cog_data.loc[1, 'gdp'] == 2.8
        assert loader.cog_data.loc[2, 'gdp'] == 2.7


class TestPanelPathHandling:
    """Test panel path addition and type detection."""

    def test_add_panel_paths(self, temp_display_dir, sample_display_info):
        """Test panel path addition to DataFrame."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        result = loader.load()

        # Check panel paths added
        assert '_panel_full_path' in result['cog_data'].columns
        assert all(result['cog_data']['_panel_full_path'].notna())

        # Check paths are correct
        for i in range(3):
            expected_path = temp_display_dir / "panels" / f"{i}.png"
            assert str(result['cog_data'].loc[i, '_panel_full_path']) == str(expected_path)

    def test_detect_panel_type_image(self, temp_display_dir, sample_display_info):
        """Test detection of image panel types."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        result = loader.load()

        # Check panel types
        assert '_panel_type' in result['cog_data'].columns
        assert all(result['cog_data']['_panel_type'] == 'image')

    def test_detect_panel_type_html(self, temp_display_dir, sample_display_info):
        """Test detection of HTML panel types."""
        # Create HTML panel files
        panels_dir = temp_display_dir / "panels"
        for i in range(3):
            (panels_dir / f"{i}.html").write_text("<html></html>")

        # Update cogData to reference HTML files
        for cog in sample_display_info["cogData"]:
            cog["panel"] = f"panels/{cog['panelKey']}.html"

        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        # Check panel types
        assert all(loader.cog_data['_panel_type'] == 'plotly')


class TestMetaFiltering:
    """Test meta variable filtering."""

    def test_get_filterable_metas(self, temp_display_dir, sample_display_info):
        """Test filterable metas extraction."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        filterable = loader.get_filterable_metas()

        assert len(filterable) == 3
        varnames = [m['varname'] for m in filterable]
        assert 'country' in varnames
        assert 'gdp' in varnames
        assert 'date' in varnames

    def test_get_sortable_metas(self, temp_display_dir, sample_display_info):
        """Test sortable metas extraction."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        sortable = loader.get_sortable_metas()

        assert len(sortable) == 3
        varnames = [m['varname'] for m in sortable]
        assert 'country' in varnames
        assert 'gdp' in varnames
        assert 'date' in varnames

    def test_exclude_panel_metas(self, temp_display_dir, sample_display_info):
        """Test that panel metas are excluded from filtering."""
        # Add panel meta
        sample_display_info["metas"].append({
            "varname": "panel",
            "label": "Panel",
            "type": "panel_src"
        })

        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        filterable = loader.get_filterable_metas()

        # Panel meta should be excluded
        varnames = [m['varname'] for m in filterable]
        assert 'panel' not in varnames


class TestFactorLabelHandling:
    """Test factor label column handling."""

    def test_add_factor_label_columns(self, temp_display_dir, sample_display_info):
        """Test adding factor label columns."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        # Check label column added
        assert 'country_label' in loader.cog_data.columns

        # Check labels are correct
        assert loader.cog_data.loc[0, 'country_label'] == 'USA'
        assert loader.cog_data.loc[1, 'country_label'] == 'UK'
        assert loader.cog_data.loc[2, 'country_label'] == 'France'

    def test_factor_values_are_indices(self, temp_display_dir, sample_display_info):
        """Test that factor values are 0-based indices."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        # Factor values should be 0-based indices
        assert loader.cog_data['country'].dtype in [int, 'int64', 'Int64']
        assert loader.cog_data.loc[0, 'country'] == 0
        assert loader.cog_data.loc[1, 'country'] == 1
        assert loader.cog_data.loc[2, 'country'] == 2


class TestDisplayNameExtraction:
    """Test display name extraction."""

    def test_display_name_in_result(self, temp_display_dir, sample_display_info):
        """Test that display name is included in result."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        result = loader.load()

        assert 'display_name' in result
        assert result['display_name'] == "test_display"

    def test_display_info_property(self, temp_display_dir, sample_display_info):
        """Test display_info property."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        assert loader.display_info is not None
        assert loader.display_info['name'] == "test_display"

    def test_cog_data_property(self, temp_display_dir, sample_display_info):
        """Test cog_data property."""
        info_path = temp_display_dir / "displayInfo.json"
        with open(info_path, 'w') as f:
            json.dump(sample_display_info, f)

        loader = DisplayLoader(temp_display_dir)
        loader.load()

        assert loader.cog_data is not None
        assert len(loader.cog_data) == 3
