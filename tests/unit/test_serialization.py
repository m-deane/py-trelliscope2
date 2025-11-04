"""
Unit tests for JSON serialization.

Tests cover serialization of Display objects to displayInfo.json format.
"""

import pytest
import pandas as pd
import json
from pathlib import Path
import tempfile
import shutil

from trelliscope.display import Display
from trelliscope.serialization import (
    serialize_display_info,
    write_display_info,
    serialize_to_json_string,
    validate_display_info,
)


class TestSerializeDisplayInfo:
    """Test serialize_display_info function."""

    def test_serialize_minimal_display(self):
        """Test serializing display with minimal configuration."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        display = Display(df, name="test_display", description="Test description")

        info = serialize_display_info(display)

        assert info["name"] == "test_display"
        assert info["description"] == "Test description"
        assert isinstance(info["keysig"], str)
        assert len(info["keysig"]) == 32
        assert "metas" in info
        assert "state" in info
        assert "views" in info

    def test_serialize_includes_all_metas(self):
        """Test that all meta variables are serialized."""
        df = pd.DataFrame({
            "category": ["A", "B", "C"],
            "value": [1.5, 2.7, 3.9]
        })
        display = Display(df, name="test")
        display.infer_metas()

        info = serialize_display_info(display)

        assert len(info["metas"]) == 2
        meta_names = {m["varname"] for m in info["metas"]}
        assert meta_names == {"category", "value"}

    def test_serialize_metas_are_sorted(self):
        """Test that metas are sorted by varname."""
        df = pd.DataFrame({
            "z_col": [1],
            "a_col": [2],
            "m_col": [3]
        })
        display = Display(df, name="test")
        display.infer_metas()

        info = serialize_display_info(display)

        varnames = [m["varname"] for m in info["metas"]]
        assert varnames == ["a_col", "m_col", "z_col"]

    def test_serialize_includes_state(self):
        """Test that state is properly serialized."""
        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")
        display.set_default_layout(ncol=3, nrow=2, arrangement="col")
        display.set_default_labels(["value"])

        info = serialize_display_info(display)

        assert "state" in info
        assert info["state"]["layout"]["ncol"] == 3
        assert info["state"]["layout"]["nrow"] == 2
        assert info["state"]["layout"]["arrangement"] == "col"
        assert info["state"]["labels"] == ["value"]
        assert isinstance(info["state"]["sort"], list)
        assert isinstance(info["state"]["filter"], list)

    def test_serialize_includes_empty_views(self):
        """Test that empty views list is included."""
        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")

        info = serialize_display_info(display)

        assert "views" in info
        assert info["views"] == []

    def test_serialize_without_panel_column(self):
        """Test serialization when no panel column is set."""
        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")

        info = serialize_display_info(display)

        assert "panelInterface" not in info

    def test_serialize_with_panel_column(self):
        """Test serialization when panel column is set."""
        df = pd.DataFrame({"plot": ["p1", "p2"], "value": [1, 2]})
        display = Display(df, name="test")
        display.set_panel_column("plot")

        info = serialize_display_info(display)

        assert "panelInterface" in info
        assert info["panelInterface"]["type"] == "panel_local"
        assert info["panelInterface"]["panelCol"] == "plot"
        assert info["panelInterface"]["format"] == "png"
        assert info["panelInterface"]["base"] == "./panels"

    def test_serialize_with_panel_options(self):
        """Test serialization includes panel options."""
        df = pd.DataFrame({"plot": ["p1", "p2"]})
        display = Display(df, name="test")
        display.set_panel_column("plot")
        display.set_panel_options(width=800, height=600, force_size=True)

        info = serialize_display_info(display)

        panel_interface = info["panelInterface"]
        assert panel_interface["width"] == 800
        assert panel_interface["height"] == 600
        assert panel_interface["forceSize"] is True

    def test_serialize_with_aspect_ratio(self):
        """Test serialization includes aspect ratio."""
        df = pd.DataFrame({"plot": ["p1", "p2"]})
        display = Display(df, name="test")
        display.set_panel_column("plot")
        display.set_panel_options(width=800, aspect=1.5)

        info = serialize_display_info(display)

        panel_interface = info["panelInterface"]
        assert panel_interface["width"] == 800
        assert panel_interface["aspect"] == 1.5

    def test_serialize_state_is_copy(self):
        """Test that state is copied, not referenced."""
        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")

        info = serialize_display_info(display)

        # Modify returned state
        info["state"]["layout"]["ncol"] = 999

        # Original should be unchanged
        assert display.state["layout"]["ncol"] == 4


class TestWriteDisplayInfo:
    """Test write_display_info function."""

    def test_write_creates_directory(self):
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "new_dir" / "subdir"

            df = pd.DataFrame({"value": [1, 2]})
            display = Display(df, name="test")

            json_path = write_display_info(display, output_path)

            assert output_path.exists()
            assert output_path.is_dir()
            assert json_path.exists()

    def test_write_creates_displayinfo_json(self):
        """Test that displayInfo.json file is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            df = pd.DataFrame({"value": [1, 2]})
            display = Display(df, name="test")

            json_path = write_display_info(display, output_path)

            assert json_path.name == "displayInfo.json"
            assert json_path.exists()

    def test_write_produces_valid_json(self):
        """Test that written file is valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            df = pd.DataFrame({"value": [1, 2]})
            display = Display(df, name="test")
            display.infer_metas()

            json_path = write_display_info(display, output_path)

            # Read and parse JSON
            with open(json_path, "r") as f:
                data = json.load(f)

            assert data["name"] == "test"
            assert "metas" in data

    def test_write_returns_json_path(self):
        """Test that function returns path to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            df = pd.DataFrame({"value": [1, 2]})
            display = Display(df, name="test")

            json_path = write_display_info(display, output_path)

            assert json_path == output_path / "displayInfo.json"

    def test_write_overwrites_existing_file(self):
        """Test that existing file is overwritten."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            # Write first display
            df1 = pd.DataFrame({"value": [1, 2]})
            display1 = Display(df1, name="display1")
            write_display_info(display1, output_path)

            # Write second display (overwrites)
            df2 = pd.DataFrame({"value": [3, 4]})
            display2 = Display(df2, name="display2")
            write_display_info(display2, output_path)

            # Read file
            json_path = output_path / "displayInfo.json"
            with open(json_path, "r") as f:
                data = json.load(f)

            assert data["name"] == "display2"


class TestSerializeToJsonString:
    """Test serialize_to_json_string function."""

    def test_returns_json_string(self):
        """Test that function returns valid JSON string."""
        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")

        json_str = serialize_to_json_string(display)

        # Should be parseable
        data = json.loads(json_str)
        assert data["name"] == "test"

    def test_respects_indent_parameter(self):
        """Test that indent parameter controls formatting."""
        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")

        # With indent
        json_with_indent = serialize_to_json_string(display, indent=2)
        assert "\n" in json_with_indent
        assert "  " in json_with_indent

        # Without indent
        json_no_indent = serialize_to_json_string(display, indent=None)
        assert len(json_no_indent) < len(json_with_indent)

    def test_handles_unicode(self):
        """Test that unicode characters are preserved."""
        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test", description="Unicode: café ñ 中文")

        json_str = serialize_to_json_string(display)

        data = json.loads(json_str)
        assert "café" in data["description"]
        assert "中文" in data["description"]


class TestValidateDisplayInfo:
    """Test validate_display_info function."""

    def test_valid_display_info(self):
        """Test that valid display info has no errors."""
        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")
        display.infer_metas()

        info = serialize_display_info(display)
        errors = validate_display_info(info)

        assert errors == []

    def test_missing_name(self):
        """Test validation catches missing name."""
        info = {
            "description": "test",
            "keysig": "abc123",
            "metas": [],
            "state": {"layout": {}, "labels": [], "sort": [], "filter": []}
        }
        errors = validate_display_info(info)

        assert len(errors) > 0
        assert any("name" in err for err in errors)

    def test_missing_metas(self):
        """Test validation catches missing metas."""
        info = {
            "name": "test",
            "description": "test",
            "keysig": "abc123",
            "state": {"layout": {}, "labels": [], "sort": [], "filter": []}
        }
        errors = validate_display_info(info)

        assert len(errors) > 0
        assert any("metas" in err for err in errors)

    def test_invalid_name_type(self):
        """Test validation catches invalid name type."""
        info = {
            "name": 123,  # Should be string
            "description": "test",
            "keysig": "abc123",
            "metas": [],
            "state": {"layout": {}, "labels": [], "sort": [], "filter": []}
        }
        errors = validate_display_info(info)

        assert len(errors) > 0
        assert any("name" in err and "string" in err for err in errors)

    def test_empty_name(self):
        """Test validation catches empty name."""
        info = {
            "name": "   ",
            "description": "test",
            "keysig": "abc123",
            "metas": [],
            "state": {"layout": {}, "labels": [], "sort": [], "filter": []}
        }
        errors = validate_display_info(info)

        assert len(errors) > 0
        assert any("empty" in err for err in errors)

    def test_invalid_metas_type(self):
        """Test validation catches non-list metas."""
        info = {
            "name": "test",
            "description": "test",
            "keysig": "abc123",
            "metas": "not a list",
            "state": {"layout": {}, "labels": [], "sort": [], "filter": []}
        }
        errors = validate_display_info(info)

        assert len(errors) > 0
        assert any("metas" in err and "list" in err for err in errors)

    def test_meta_missing_varname(self):
        """Test validation catches meta without varname."""
        info = {
            "name": "test",
            "description": "test",
            "keysig": "abc123",
            "metas": [{"type": "number"}],  # Missing varname
            "state": {"layout": {}, "labels": [], "sort": [], "filter": []}
        }
        errors = validate_display_info(info)

        assert len(errors) > 0
        assert any("varname" in err for err in errors)

    def test_meta_missing_type(self):
        """Test validation catches meta without type."""
        info = {
            "name": "test",
            "description": "test",
            "keysig": "abc123",
            "metas": [{"varname": "value"}],  # Missing type
            "state": {"layout": {}, "labels": [], "sort": [], "filter": []}
        }
        errors = validate_display_info(info)

        assert len(errors) > 0
        assert any("type" in err for err in errors)

    def test_missing_state_fields(self):
        """Test validation catches missing state fields."""
        info = {
            "name": "test",
            "description": "test",
            "keysig": "abc123",
            "metas": [],
            "state": {"layout": {}}  # Missing labels, sort, filter
        }
        errors = validate_display_info(info)

        assert len(errors) >= 3
        assert any("labels" in err for err in errors)
        assert any("sort" in err for err in errors)
        assert any("filter" in err for err in errors)

    def test_multiple_errors(self):
        """Test validation returns all errors."""
        info = {
            "name": 123,  # Wrong type
            "metas": "not a list",  # Wrong type
        }
        errors = validate_display_info(info)

        assert len(errors) >= 3  # Multiple issues
