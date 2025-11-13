"""
Tests for metadata file generation (metaData.json and metaData.js).

These files are REQUIRED by trelliscopejs-lib viewer for file-based panels.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from trelliscope import Display
from trelliscope.meta import FactorMeta, NumberMeta
from trelliscope.serialization import (
    _serialize_cog_data,
    write_metadata_js,
    write_metadata_json,
)


class TestMetadataGeneration:
    """Test metadata file generation for file-based panels."""

    @pytest.fixture
    def sample_display(self):
        """Create a sample Display for testing."""
        df = pd.DataFrame(
            {
                "category": ["A", "B", "C", "D", "E"],
                "value": [10, 25, 15, 30, 20],
                "panel": [
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # Panel objects (will be rendered)
            }
        )

        display = Display(df, name="test_display", description="Test Display")
        display.set_panel_column("panel")

        # Add meta variables
        display.add_meta_variable(
            FactorMeta(
                varname="category", label="Category", levels=["A", "B", "C", "D", "E"]
            )
        )
        display.add_meta_variable(NumberMeta(varname="value", label="Value"))

        return display

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    def test_serialize_cog_data_structure(self, sample_display):
        """Test that _serialize_cog_data generates correct structure."""
        cog_data = _serialize_cog_data(sample_display)

        # Should have 5 entries
        assert len(cog_data) == 5

        # Check first entry structure
        first_entry = cog_data[0]
        assert "category" in first_entry
        assert "value" in first_entry
        assert "panelKey" in first_entry
        assert "panel" in first_entry

        # Check values
        assert first_entry["category"] == "A"
        assert first_entry["value"] == 10
        assert first_entry["panelKey"] == "0"
        assert first_entry["panel"] == "0.png"

    def test_serialize_cog_data_panel_paths(self, sample_display):
        """Test that panel paths are in correct format for file-based panels."""
        cog_data = _serialize_cog_data(sample_display)

        # All panel values should be in format "X.png" (not "panels/X.png")
        for i, entry in enumerate(cog_data):
            assert entry["panel"] == f"{i}.png"
            assert not entry["panel"].startswith("panels/")

    def test_write_metadata_json_creates_file(self, sample_display, temp_output_dir):
        """Test that write_metadata_json creates metaData.json file."""
        json_path = write_metadata_json(sample_display, temp_output_dir)

        # File should exist
        assert json_path.exists()
        assert json_path.name == "metaData.json"

    def test_write_metadata_json_content(self, sample_display, temp_output_dir):
        """Test that metaData.json has correct content structure."""
        json_path = write_metadata_json(sample_display, temp_output_dir)

        # Load and check content
        with open(json_path, "r") as f:
            metadata = json.load(f)

        # Should be an array
        assert isinstance(metadata, list)
        assert len(metadata) == 5

        # Check first entry
        first_entry = metadata[0]
        assert first_entry["category"] == "A"
        assert first_entry["value"] == 10
        assert first_entry["panelKey"] == "0"
        # CRITICAL: Panel path should be RELATIVE with "panels/" prefix
        assert first_entry["panel"] == "panels/0.png"

    def test_write_metadata_json_relative_paths(self, sample_display, temp_output_dir):
        """Test that metaData.json uses relative panel paths."""
        json_path = write_metadata_json(sample_display, temp_output_dir)

        with open(json_path, "r") as f:
            metadata = json.load(f)

        # All panel values should start with "panels/"
        for i, entry in enumerate(metadata):
            assert entry["panel"] == f"panels/{i}.png"
            # Should NOT be full URLs
            assert not entry["panel"].startswith("http://")
            assert not entry["panel"].startswith("https://")

    def test_write_metadata_js_creates_file(self, sample_display, temp_output_dir):
        """Test that write_metadata_js creates metaData.js file."""
        js_path = write_metadata_js(sample_display, temp_output_dir)

        # File should exist
        assert js_path.exists()
        assert js_path.name == "metaData.js"

    def test_write_metadata_js_content(self, sample_display, temp_output_dir):
        """Test that metaData.js has correct JavaScript wrapper."""
        js_path = write_metadata_js(sample_display, temp_output_dir)

        # Read JavaScript content
        with open(js_path, "r") as f:
            content = f.read()

        # Should start with window.metaData =
        assert content.startswith("window.metaData = ")

        # Should end with semicolon
        assert content.strip().endswith(";")

        # Should contain valid JSON
        # Extract JSON part (between = and ;)
        json_str = content.split("window.metaData = ")[1].rstrip(";\n")
        metadata = json.loads(json_str)

        # Check structure
        assert isinstance(metadata, list)
        assert len(metadata) == 5
        assert metadata[0]["category"] == "A"
        assert metadata[0]["panel"] == "panels/0.png"

    def test_metadata_files_have_same_data(self, sample_display, temp_output_dir):
        """Test that metaData.json and metaData.js contain same data."""
        json_path = write_metadata_json(sample_display, temp_output_dir)
        js_path = write_metadata_js(sample_display, temp_output_dir)

        # Load JSON file
        with open(json_path, "r") as f:
            json_data = json.load(f)

        # Parse JS file
        with open(js_path, "r") as f:
            js_content = f.read()
        js_json_str = js_content.split("window.metaData = ")[1].rstrip(";\n")
        js_data = json.loads(js_json_str)

        # Data should be identical
        assert json_data == js_data

    def test_metadata_panel_key_increments(self, sample_display, temp_output_dir):
        """Test that panelKey values increment correctly."""
        json_path = write_metadata_json(sample_display, temp_output_dir)

        with open(json_path, "r") as f:
            metadata = json.load(f)

        # Panel keys should be "0", "1", "2", "3", "4"
        for i, entry in enumerate(metadata):
            assert entry["panelKey"] == str(i)

    def test_metadata_preserves_data_types(self, sample_display, temp_output_dir):
        """Test that metadata preserves correct data types."""
        json_path = write_metadata_json(sample_display, temp_output_dir)

        with open(json_path, "r") as f:
            metadata = json.load(f)

        first_entry = metadata[0]

        # String values should be strings
        assert isinstance(first_entry["category"], str)
        assert isinstance(first_entry["panelKey"], str)
        assert isinstance(first_entry["panel"], str)

        # Numeric values should be numbers
        assert isinstance(first_entry["value"], (int, float))


class TestMetadataWithDisplay:
    """Integration tests for metadata generation through Display.write()."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    def test_display_write_creates_metadata_files(self, temp_output_dir):
        """Test that Display.write() creates both metadata files."""
        # Note: This test uses render_panels=False to avoid needing actual panel objects
        df = pd.DataFrame(
            {
                "category": ["A", "B", "C"],
                "value": [10, 20, 30],
                "panel": ["panel1", "panel2", "panel3"],  # Dummy panel values
            }
        )

        display = Display(df, name="test_metadata", description="Test")
        display.set_panel_column("panel")
        display.add_meta_variable(FactorMeta("category", levels=["A", "B", "C"]))
        display.add_meta_variable(NumberMeta("value"))

        # Write display (without rendering panels)
        output_path = display.write(
            output_path=temp_output_dir / "test_metadata",
            force=True,
            render_panels=False,
        )

        # Check that all required files were created
        assert (output_path / "displayInfo.json").exists()
        assert (output_path / "metaData.json").exists()
        assert (output_path / "metaData.js").exists()
        assert (output_path / "metadata.csv").exists()

    def test_display_write_metadata_consistency(self, temp_output_dir):
        """Test that metadata files are consistent with displayInfo.json."""
        df = pd.DataFrame(
            {
                "category": ["A", "B"],
                "value": [10, 20],
                "panel": ["p1", "p2"],
            }
        )

        display = Display(df, name="test_consistency", description="Test")
        display.set_panel_column("panel")
        display.add_meta_variable(FactorMeta("category", levels=["A", "B"]))
        display.add_meta_variable(NumberMeta("value"))

        output_path = display.write(
            output_path=temp_output_dir / "test_consistency",
            force=True,
            render_panels=False,
        )

        # Load all three files
        with open(output_path / "displayInfo.json", "r") as f:
            display_info = json.load(f)

        with open(output_path / "metaData.json", "r") as f:
            metadata_json = json.load(f)

        with open(output_path / "metaData.js", "r") as f:
            js_content = f.read()
        js_json_str = js_content.split("window.metaData = ")[1].rstrip(";\n")
        metadata_js = json.loads(js_json_str)

        # displayInfo should have embedded cogData
        assert "cogData" in display_info
        assert len(display_info["cogData"]) == 2

        # All three should have same number of entries
        assert (
            len(display_info["cogData"]) == len(metadata_json) == len(metadata_js) == 2
        )

        # First entry should have same values (except panel paths differ)
        assert (
            display_info["cogData"][0]["category"]
            == metadata_json[0]["category"]
            == "A"
        )
        assert display_info["cogData"][0]["value"] == metadata_json[0]["value"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
