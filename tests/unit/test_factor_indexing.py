"""
Unit tests for factor indexing conversion to 1-based (R-style).

These tests verify the critical fix that converts factor indices from Python's
0-based indexing to R-style 1-based indexing expected by trelliscopejs viewer.

See: .claude_plans/FACTOR_INDEXING_SOLUTION.md for detailed documentation.
"""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from trelliscope.display import Display
from trelliscope.meta import FactorMeta, NumberMeta
from trelliscope.serialization import (
    _serialize_cog_data,
    write_metadata_js,
    write_metadata_json,
)


class TestFactorIndexingConversion:
    """Test factor index conversion from 0-based to 1-based."""

    def test_numeric_categorical_converts_to_1based(self):
        """Test that numeric categorical indices (0,1,2) convert to 1-based (1,2,3)."""
        # Create DataFrame with categorical column (0-based indices)
        df = pd.DataFrame(
            {
                "country": pd.Categorical(["Algeria", "Denmark", "Germany"]),
                "value": [10.5, 20.3, 15.7],
            }
        )

        display = Display(df, name="test_1based")
        display.add_meta_variable(
            FactorMeta(
                varname="country",
                label="Country",
                levels=["Algeria", "Denmark", "Germany"],
            )
        )
        display.add_meta_variable(NumberMeta(varname="value", label="Value"))

        # Serialize cogData
        cog_data = _serialize_cog_data(display)

        # Verify conversion to 1-based
        assert cog_data[0]["country"] == 1, "Algeria (index 0) should convert to 1"
        assert cog_data[1]["country"] == 2, "Denmark (index 1) should convert to 2"
        assert cog_data[2]["country"] == 3, "Germany (index 2) should convert to 3"

        # Verify all are integers, not strings or floats
        for entry in cog_data:
            assert isinstance(entry["country"], int), "Country values must be integers"

    def test_string_factor_values_convert_to_1based(self):
        """Test that string factor values ('Algeria', 'Denmark') convert to 1-based indices."""
        # Create DataFrame with string column (not categorical)
        df = pd.DataFrame(
            {
                "country": ["Algeria", "Denmark", "Germany"],  # STRING values
                "value": [10.5, 20.3, 15.7],
            }
        )

        display = Display(df, name="test_string_to_1based")
        display.add_meta_variable(
            FactorMeta(
                varname="country",
                label="Country",
                levels=["Algeria", "Denmark", "Germany"],  # Levels define mapping
            )
        )
        display.add_meta_variable(NumberMeta(varname="value", label="Value"))

        # Serialize cogData
        cog_data = _serialize_cog_data(display)

        # Verify string-to-index conversion
        assert cog_data[0]["country"] == 1, "'Algeria' should convert to 1"
        assert cog_data[1]["country"] == 2, "'Denmark' should convert to 2"
        assert cog_data[2]["country"] == 3, "'Germany' should convert to 3"

        # Verify all are integers
        for entry in cog_data:
            assert isinstance(
                entry["country"], int
            ), "Converted values must be integers"

    def test_zero_index_converts_correctly(self):
        """Test that index 0 specifically converts to 1 (critical for '[missing]' bug fix)."""
        df = pd.DataFrame({"category": pd.Categorical(["first", "second", "third"])})

        display = Display(df, name="test_zero_index")
        display.add_meta_variable(
            FactorMeta(
                varname="category",
                label="Category",
                levels=["first", "second", "third"],
            )
        )

        cog_data = _serialize_cog_data(display)

        # This is the critical fix: 0 → 1, not 0 → undefined
        first_category = cog_data[0]["category"]
        assert (
            first_category == 1
        ), "Index 0 must convert to 1 to avoid viewer '[missing]' bug"
        assert first_category != 0, "Index 0 must NOT remain 0 (would show '[missing]')"

    def test_non_factor_values_unchanged(self):
        """Test that non-factor values are not affected by conversion."""
        df = pd.DataFrame(
            {
                "country": pd.Categorical(["Algeria", "Denmark"]),
                "value": [100.5, 200.3],  # Numeric, not factor
                "label": ["Label A", "Label B"],  # String, not factor
            }
        )

        display = Display(df, name="test_non_factors")
        display.add_meta_variable(
            FactorMeta(
                varname="country", label="Country", levels=["Algeria", "Denmark"]
            )
        )
        display.add_meta_variable(NumberMeta(varname="value", label="Value"))
        # Note: label column not added as meta, so treated as generic

        cog_data = _serialize_cog_data(display)

        # Factor converted
        assert cog_data[0]["country"] == 1

        # Non-factors unchanged
        assert cog_data[0]["value"] == 100.5
        assert cog_data[1]["value"] == 200.3

    def test_multiple_factor_columns(self):
        """Test conversion works correctly with multiple factor columns."""
        df = pd.DataFrame(
            {
                "country": pd.Categorical(["Algeria", "Denmark", "Germany"]),
                "status": pd.Categorical(["active", "inactive", "pending"]),
            }
        )

        display = Display(df, name="test_multiple_factors")
        display.add_meta_variable(
            FactorMeta(
                varname="country",
                label="Country",
                levels=["Algeria", "Denmark", "Germany"],
            )
        )
        display.add_meta_variable(
            FactorMeta(
                varname="status",
                label="Status",
                levels=["active", "inactive", "pending"],
            )
        )

        cog_data = _serialize_cog_data(display)

        # Both factors converted independently
        assert cog_data[0]["country"] == 1  # Algeria
        assert cog_data[0]["status"] == 1  # active

        assert cog_data[1]["country"] == 2  # Denmark
        assert cog_data[1]["status"] == 2  # inactive

        assert cog_data[2]["country"] == 3  # Germany
        assert cog_data[2]["status"] == 3  # pending

    def test_factor_with_none_values(self):
        """Test that None/NaN factor values are handled gracefully."""
        df = pd.DataFrame(
            {
                "country": pd.Categorical(["Algeria", None, "Denmark"]),
                "value": [10, 20, 30],
            }
        )

        display = Display(df, name="test_none_factors")
        display.add_meta_variable(
            FactorMeta(
                varname="country",
                label="Country",
                levels=["Algeria", "Denmark", "Germany"],
            )
        )

        cog_data = _serialize_cog_data(display)

        # Valid factors converted
        assert cog_data[0]["country"] == 1  # Algeria
        assert cog_data[2]["country"] == 2  # Denmark

        # NaN handled - remains as NaN (not converted)
        import math

        second_value = cog_data[1]["country"]
        # NaN is a float that doesn't equal itself
        assert (
            second_value != second_value or second_value is None
        ), "NaN/None values should be preserved"

    def test_string_not_in_levels_preserved(self):
        """Test that string values not in levels are preserved (not converted)."""
        df = pd.DataFrame(
            {
                "country": ["Algeria", "Unknown", "Denmark"],  # 'Unknown' not in levels
                "value": [10, 20, 30],
            }
        )

        display = Display(df, name="test_missing_level")
        display.add_meta_variable(
            FactorMeta(
                varname="country",
                label="Country",
                levels=["Algeria", "Denmark", "Germany"],
            )
        )

        cog_data = _serialize_cog_data(display)

        # Valid strings converted
        assert cog_data[0]["country"] == 1  # Algeria
        assert cog_data[2]["country"] == 2  # Denmark

        # Invalid string preserved as-is
        assert (
            cog_data[1]["country"] == "Unknown"
        ), "String not in levels should be preserved"


class TestMetadataJsonFactorIndexing:
    """Test factor indexing in metaData.json generation."""

    def test_metadata_json_has_1based_factors(self):
        """Test that metaData.json file contains 1-based factor indices."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            df = pd.DataFrame(
                {"country": ["Algeria", "Denmark", "Germany"], "value": [100, 200, 300]}
            )

            display = Display(df, name="test_metadata_json")
            display.add_meta_variable(
                FactorMeta(
                    varname="country",
                    label="Country",
                    levels=["Algeria", "Denmark", "Germany"],
                )
            )
            display.set_panel_column("value")

            # Write metaData.json
            json_path = write_metadata_json(display, output_path)

            # Read and verify
            with open(json_path) as f:
                metadata = json.load(f)

            assert metadata[0]["country"] == 1, "Algeria should be 1"
            assert metadata[1]["country"] == 2, "Denmark should be 2"
            assert metadata[2]["country"] == 3, "Germany should be 3"

    def test_metadata_json_preserves_other_values(self):
        """Test that non-factor values in metaData.json are unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            df = pd.DataFrame(
                {
                    "country": pd.Categorical(["Algeria", "Denmark"]),
                    "avg_value": [100.5, 200.7],
                    "count": [5, 10],
                    "panel_id": ["A", "B"],  # Separate panel column
                }
            )

            display = Display(df, name="test_mixed_types")
            display.add_meta_variable(
                FactorMeta(
                    varname="country", label="Country", levels=["Algeria", "Denmark"]
                )
            )
            display.add_meta_variable(NumberMeta(varname="avg_value", label="Average"))
            display.add_meta_variable(
                NumberMeta(varname="count", label="Count", digits=0)
            )
            display.set_panel_column("panel_id")  # Use separate column for panels

            json_path = write_metadata_json(display, output_path)

            with open(json_path) as f:
                metadata = json.load(f)

            # Factor converted
            assert metadata[0]["country"] == 1

            # Numbers unchanged (not panel column)
            assert metadata[0]["avg_value"] == 100.5
            assert metadata[0]["count"] == 5


class TestMetadataJsFactorIndexing:
    """Test factor indexing in metaData.js generation."""

    def test_metadata_js_has_1based_factors(self):
        """Test that metaData.js file contains 1-based factor indices."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            df = pd.DataFrame({"country": ["Algeria", "Denmark"], "value": [100, 200]})

            display = Display(df, name="test_metadata_js")
            display.add_meta_variable(
                FactorMeta(
                    varname="country", label="Country", levels=["Algeria", "Denmark"]
                )
            )
            display.set_panel_column("value")

            # Write metaData.js
            js_path = write_metadata_js(display, output_path)

            # Read and parse (strip window.metaData = and trailing ;)
            with open(js_path) as f:
                content = f.read()

            assert content.startswith(
                "window.metaData = "
            ), "Should have window.metaData wrapper"
            assert content.endswith(";\n"), "Should end with semicolon"

            # Extract JSON part
            json_str = content.replace("window.metaData = ", "").rstrip(";\n")
            metadata = json.loads(json_str)

            assert metadata[0]["country"] == 1, "Algeria should be 1"
            assert metadata[1]["country"] == 2, "Denmark should be 2"

    def test_metadata_js_is_valid_javascript(self):
        """Test that generated metaData.js is syntactically valid JavaScript."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            df = pd.DataFrame(
                {"category": pd.Categorical(["A", "B", "C"]), "value": [1, 2, 3]}
            )

            display = Display(df, name="test_js_validity")
            display.add_meta_variable(
                FactorMeta(varname="category", label="Category", levels=["A", "B", "C"])
            )
            display.set_panel_column("value")

            js_path = write_metadata_js(display, output_path)

            with open(js_path) as f:
                content = f.read()

            # Basic JS syntax validation
            assert "window.metaData = [" in content
            assert content.count("{") == content.count("}"), "Balanced braces"
            assert content.count("[") == content.count("]"), "Balanced brackets"

            # Should be parseable as JSON after stripping wrapper
            json_str = content.replace("window.metaData = ", "").rstrip(";\n")
            metadata = json.loads(json_str)  # Will raise if invalid

            assert len(metadata) == 3


class TestEndToEndFactorIndexing:
    """Test complete workflow with factor indexing."""

    def test_full_display_write_with_factors(self):
        """Test end-to-end display generation with factor conversion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            # Create display with string country values
            df = pd.DataFrame(
                {
                    "country": ["Algeria", "Denmark", "Germany"],
                    "avg_capacity": [497.7, 312.5, 2180.4],
                    "panel_id": ["A", "B", "C"],
                }
            )

            display = Display(df, name="refinery_test", path=output_path)
            display.add_meta_variable(
                FactorMeta(
                    varname="country",
                    label="Country",
                    levels=sorted(df["country"].unique()),
                )
            )
            display.add_meta_variable(
                NumberMeta(varname="avg_capacity", label="Avg Capacity", digits=1)
            )
            display.set_panel_column("panel_id")

            # Write display
            display_path = display.write()

            # Verify displayInfo.json has 1-based factors
            displayinfo_path = (
                display_path / "displays" / "refinery_test" / "displayInfo.json"
            )
            with open(displayinfo_path) as f:
                info = json.load(f)

            assert (
                info["cogData"][0]["country"] == 1
            ), "Algeria should be 1 in displayInfo"

            # Verify metaData.json has 1-based factors
            metadata_json_path = (
                display_path / "displays" / "refinery_test" / "metaData.json"
            )
            with open(metadata_json_path) as f:
                metadata_json = json.load(f)

            assert (
                metadata_json[0]["country"] == 1
            ), "Algeria should be 1 in metaData.json"

            # Verify metaData.js has 1-based factors
            metadata_js_path = (
                display_path / "displays" / "refinery_test" / "metaData.js"
            )
            with open(metadata_js_path) as f:
                content = f.read()

            json_str = content.replace("window.metaData = ", "").rstrip(";\n")
            metadata_js = json.loads(json_str)

            assert metadata_js[0]["country"] == 1, "Algeria should be 1 in metaData.js"

    def test_viewer_compatibility(self):
        """Test that generated JSON matches viewer expectations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)

            df = pd.DataFrame(
                {
                    "status": pd.Categorical(["active", "inactive", "pending"]),
                    "value": [10, 20, 30],
                }
            )

            display = Display(df, name="viewer_compat_test", path=output_path)
            display.add_meta_variable(
                FactorMeta(
                    varname="status",
                    label="Status",
                    levels=["active", "inactive", "pending"],
                )
            )
            display.set_panel_column("value")

            display_path = display.write()

            # Load displayInfo
            displayinfo_path = (
                display_path / "displays" / "viewer_compat_test" / "displayInfo.json"
            )
            with open(displayinfo_path) as f:
                info = json.load(f)

            # Viewer expectations:
            # 1. cogData has integer indices (not strings)
            for entry in info["cogData"]:
                assert isinstance(
                    entry["status"], int
                ), "Viewer expects integer indices"

            # 2. Indices are 1-based (for levels[factor - 1] calculation)
            assert info["cogData"][0]["status"] == 1  # active
            assert info["cogData"][1]["status"] == 2  # inactive
            assert info["cogData"][2]["status"] == 3  # pending

            # 3. Levels array is 0-indexed
            status_meta = [m for m in info["metas"] if m["varname"] == "status"][0]
            assert status_meta["levels"][0] == "active"  # levels[0]
            assert status_meta["levels"][1] == "inactive"  # levels[1]
            assert status_meta["levels"][2] == "pending"  # levels[2]

            # Verify viewer calculation: levels[factor - 1]
            # For first entry: factor=1, levels[1-1]=levels[0]='active' ✓
            factor_idx = info["cogData"][0]["status"]  # 1
            expected_level = status_meta["levels"][factor_idx - 1]  # levels[0]
            assert (
                expected_level == "active"
            ), "Viewer calculation should work correctly"


class TestFactorIndexingEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_dataframe(self):
        """Test factor indexing with empty DataFrame."""
        df = pd.DataFrame(
            {"country": pd.Categorical([], categories=["Algeria", "Denmark"])}
        )

        display = Display(df, name="test_empty")
        display.add_meta_variable(
            FactorMeta(
                varname="country", label="Country", levels=["Algeria", "Denmark"]
            )
        )

        cog_data = _serialize_cog_data(display)

        assert cog_data == [], "Empty DataFrame should produce empty cogData"

    def test_single_row(self):
        """Test factor indexing with single row."""
        df = pd.DataFrame({"country": pd.Categorical(["Algeria"])})

        display = Display(df, name="test_single")
        display.add_meta_variable(
            FactorMeta(
                varname="country",
                label="Country",
                levels=["Algeria", "Denmark", "Germany"],
            )
        )

        cog_data = _serialize_cog_data(display)

        assert len(cog_data) == 1
        assert cog_data[0]["country"] == 1

    def test_large_number_of_levels(self):
        """Test factor indexing with many levels."""
        # 100 levels
        levels = [f"level_{i:03d}" for i in range(100)]
        categories = [levels[i % 100] for i in range(10)]

        df = pd.DataFrame({"category": pd.Categorical(categories, categories=levels)})

        display = Display(df, name="test_many_levels")
        display.add_meta_variable(
            FactorMeta(varname="category", label="Category", levels=levels)
        )

        cog_data = _serialize_cog_data(display)

        # First entry is level_000 (index 0 → 1)
        assert cog_data[0]["category"] == 1

        # Last level used would be level_099 (index 99 → 100) if present
        # But we only use first 10 levels in rotation

    def test_unicode_factor_levels(self):
        """Test factor indexing with unicode characters in levels."""
        df = pd.DataFrame({"country": ["中国", "Россия", "العربية"]})

        display = Display(df, name="test_unicode")
        display.add_meta_variable(
            FactorMeta(
                varname="country", label="Country", levels=["中国", "Россия", "العربية"]
            )
        )

        cog_data = _serialize_cog_data(display)

        assert cog_data[0]["country"] == 1  # 中国
        assert cog_data[1]["country"] == 2  # Россия
        assert cog_data[2]["country"] == 3  # العربية
