"""
Integration tests for basic trelliscope workflow.

Tests the complete workflow from DataFrame to written display output,
verifying all components work together correctly.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from trelliscope import Display


class TestBasicWorkflow:
    """Test complete workflow from DataFrame to output."""

    def test_minimal_workflow(self):
        """Test minimal workflow: create display and write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create simple DataFrame
            df = pd.DataFrame(
                {
                    "plot": ["p1", "p2", "p3"],
                    "category": ["A", "B", "C"],
                    "value": [10.5, 20.7, 30.9],
                }
            )

            # Create and write display
            output = (
                Display(df, name="test_display")
                .set_panel_column("plot")
                .infer_metas()
                .write(output_path=Path(tmpdir) / "output")
            )

            # Verify multi-display output structure
            assert output.exists()
            assert (output / "config.json").exists()
            assert (output / "index.html").exists()
            assert (output / "displays" / "displayList.json").exists()

            # Display files are in displays/test_display/
            display_dir = output / "displays" / "test_display"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            # Verify displayInfo.json content
            with open(display_dir / "displayInfo.json") as f:
                info = json.load(f)

            assert info["name"] == "test_display"
            assert len(info["metas"]) == 3  # category, value, and panel
            # Verify panel meta exists
            panel_metas = [m for m in info["metas"] if m["type"] == "panel"]
            assert len(panel_metas) == 1
            assert panel_metas[0]["varname"] == "plot"
            assert info["state"]["layout"]["ncol"] == 4  # Default

            # Verify metadata.csv content
            metadata = pd.read_csv(display_dir / "metadata.csv")
            assert len(metadata) == 3
            assert "category" in metadata.columns
            assert "value" in metadata.columns
            assert "plot" not in metadata.columns

    def test_full_workflow_with_all_configuration(self):
        """Test complete workflow with all configuration options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create DataFrame with multiple types
            df = pd.DataFrame(
                {
                    "panel": ["p1", "p2", "p3", "p4"],
                    "category": ["A", "B", "A", "B"],
                    "value": [10.5, 20.7, 30.9, 40.2],
                    "date": pd.date_range("2024-01-01", periods=4),
                    "flag": [True, False, True, False],
                }
            )

            # Create display with full configuration
            display = (
                Display(
                    df,
                    name="full_display",
                    description="A comprehensive test display",
                    path=tmpdir,
                )
                .set_panel_column("panel")
                .infer_metas()
                .set_default_layout(ncol=2, nrow=2, arrangement="row")
                .set_panel_options(width=800, height=600)
                .set_default_labels(["category", "value"])
            )

            output = display.write()

            # Verify output
            assert output.exists()
            expected_path = Path(tmpdir) / "full_display"
            assert output == expected_path

            # Verify multi-display structure
            assert (output / "config.json").exists()
            assert (output / "index.html").exists()
            assert (output / "displays" / "displayList.json").exists()

            # Display files are in displays/full_display/
            display_dir = output / "displays" / "full_display"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            # Read and verify JSON
            with open(display_dir / "displayInfo.json") as f:
                info = json.load(f)

            assert info["name"] == "full_display"
            assert info["description"] == "A comprehensive test display"
            assert len(info["metas"]) == 5  # category, value, date, flag, panel

            # Verify layout
            assert info["state"]["layout"]["ncol"] == 2
            assert info["state"]["layout"]["nrow"] == 2
            assert info["state"]["layout"]["arrangement"] == "row"

            # Verify labels
            assert info["state"]["labels"] == ["category", "value"]

            # Verify panel interface
            assert info["panelInterface"]["panelCol"] == "panel"
            assert info["width"] == 800
            assert info["height"] == 600

            # Verify metadata CSV
            metadata = pd.read_csv(display_dir / "metadata.csv")
            assert len(metadata) == 4
            assert list(metadata.columns) == ["category", "value", "date", "flag"]

    def test_workflow_with_explicit_metas(self):
        """Test workflow with explicitly defined meta variables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame(
                {
                    "plot": ["p1", "p2", "p3"],
                    "category": ["A", "B", "C"],
                    "score": [85.5, 92.3, 78.9],
                    "grade": ["B", "A", "C"],
                }
            )

            # Create display with explicit metas
            output = (
                Display(df, name="explicit_metas")
                .set_panel_column("plot")
                .add_meta_def("category", "factor", levels=["A", "B", "C", "D"])
                .add_meta_def("score", "number", digits=1, log=False)
                .add_meta_def("grade", "factor", levels=["A", "B", "C", "D", "F"])
                .write(output_path=Path(tmpdir) / "output")
            )

            # Verify multi-display structure
            assert (output / "config.json").exists()
            assert (output / "index.html").exists()
            assert (output / "displays" / "displayList.json").exists()

            # Display files are in displays/explicit_metas/
            display_dir = output / "displays" / "explicit_metas"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            # Verify metas in JSON
            with open(display_dir / "displayInfo.json") as f:
                info = json.load(f)

            metas_by_name = {m["varname"]: m for m in info["metas"]}

            # Verify category meta
            assert metas_by_name["category"]["type"] == "factor"
            assert metas_by_name["category"]["levels"] == ["A", "B", "C", "D"]

            # Verify score meta
            assert metas_by_name["score"]["type"] == "number"
            assert metas_by_name["score"]["digits"] == 1

            # Verify grade meta
            assert metas_by_name["grade"]["type"] == "factor"
            assert "F" in metas_by_name["grade"]["levels"]

    def test_workflow_with_mixed_meta_definition(self):
        """Test workflow mixing inferred and explicit metas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame(
                {
                    "plot": ["p1", "p2", "p3"],
                    "auto_category": ["X", "Y", "Z"],
                    "auto_value": [1.5, 2.7, 3.9],
                    "manual_score": [10, 20, 30],
                    "manual_label": ["low", "med", "high"],
                }
            )

            # Infer some, define others
            output = (
                Display(df, name="mixed_metas")
                .set_panel_column("plot")
                .infer_metas(columns=["auto_category", "auto_value"])
                .add_meta_def("manual_score", "number", digits=0)
                .add_meta_def("manual_label", "factor")
                .write(output_path=Path(tmpdir) / "output")
            )

            # Verify multi-display structure
            assert (output / "config.json").exists()
            assert (output / "index.html").exists()
            assert (output / "displays" / "displayList.json").exists()

            # Display files are in displays/mixed_metas/
            display_dir = output / "displays" / "mixed_metas"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            # Verify all metas present
            with open(display_dir / "displayInfo.json") as f:
                info = json.load(f)

            assert len(info["metas"]) == 5  # 4 data metas + 1 panel meta
            meta_names = {m["varname"] for m in info["metas"]}
            assert meta_names == {
                "auto_category",
                "auto_value",
                "manual_score",
                "manual_label",
                "plot",  # panel column
            }

    def test_workflow_with_datetime_columns(self):
        """Test workflow with date and datetime columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame(
                {
                    "plot": ["p1", "p2", "p3"],
                    "date_only": pd.date_range("2024-01-01", periods=3, freq="D"),
                    "datetime_with_time": pd.date_range(
                        "2024-01-01 12:30:00", periods=3, freq="h"
                    ),
                    "datetime_with_tz": pd.date_range(
                        "2024-01-01", periods=3, freq="D", tz="UTC"
                    ),
                }
            )

            output = (
                Display(df, name="datetime_test")
                .set_panel_column("plot")
                .infer_metas()
                .write(output_path=Path(tmpdir) / "output")
            )

            # Verify multi-display structure
            assert (output / "config.json").exists()
            assert (output / "index.html").exists()
            assert (output / "displays" / "displayList.json").exists()

            # Display files are in displays/datetime_test/
            display_dir = output / "displays" / "datetime_test"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            # Verify meta types
            with open(display_dir / "displayInfo.json") as f:
                info = json.load(f)

            metas_by_name = {m["varname"]: m for m in info["metas"]}

            # Date-only should be DateMeta
            assert metas_by_name["date_only"]["type"] == "date"

            # Datetime with time should be TimeMeta
            assert metas_by_name["datetime_with_time"]["type"] == "time"

            # Datetime with timezone should be TimeMeta with timezone
            assert metas_by_name["datetime_with_tz"]["type"] == "time"
            assert metas_by_name["datetime_with_tz"]["timezone"] == "UTC"

    def test_workflow_overwrite_with_force(self):
        """Test writing to same location with force=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output"

            df = pd.DataFrame({"plot": ["p1", "p2"], "value": [1, 2]})

            # First write
            Display(df, name="test1").set_panel_column("plot").write(
                output_path=output_path
            )

            # Verify multi-display structure exists
            assert (output_path / "config.json").exists()
            assert (output_path / "index.html").exists()
            assert (output_path / "displays" / "displayList.json").exists()

            # Second write with different data (force=True)
            df2 = pd.DataFrame({"plot": ["p1", "p2", "p3"], "value": [10, 20, 30]})

            Display(df2, name="test2").set_panel_column("plot").infer_metas().write(
                output_path=output_path, force=True
            )

            # Verify second display overwrote first
            display_dir = output_path / "displays" / "test2"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            with open(display_dir / "displayInfo.json") as f:
                info = json.load(f)

            assert info["name"] == "test2"

            metadata = pd.read_csv(display_dir / "metadata.csv")
            assert len(metadata) == 3  # Updated data

    def test_workflow_with_empty_dataframe_columns(self):
        """Test workflow with DataFrame containing some empty values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame(
                {
                    "plot": ["p1", "p2", "p3"],
                    "category": ["A", None, "C"],
                    "value": [10.5, None, 30.9],
                    "flag": [True, False, None],
                }
            )

            output = (
                Display(df, name="with_nulls")
                .set_panel_column("plot")
                .infer_metas()
                .write(output_path=Path(tmpdir) / "output")
            )

            # Should succeed and handle nulls appropriately
            assert output.exists()

            # Verify multi-display structure
            assert (output / "config.json").exists()
            assert (output / "index.html").exists()
            assert (output / "displays" / "displayList.json").exists()

            # Display files are in displays/with_nulls/
            display_dir = output / "displays" / "with_nulls"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            # Verify metadata CSV preserves structure
            metadata = pd.read_csv(display_dir / "metadata.csv")
            assert len(metadata) == 3
            assert metadata["category"].isna().sum() == 1
            assert metadata["value"].isna().sum() == 1


class TestWorkflowEdgeCases:
    """Test edge cases in the workflow."""

    def test_single_row_dataframe(self):
        """Test workflow with single-row DataFrame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({"plot": ["p1"], "value": [42]})

            output = (
                Display(df, name="single_row")
                .set_panel_column("plot")
                .infer_metas()
                .write(output_path=Path(tmpdir) / "output")
            )

            assert output.exists()

            # Verify multi-display structure
            assert (output / "config.json").exists()
            assert (output / "index.html").exists()
            assert (output / "displays" / "displayList.json").exists()

            # Display files are in displays/single_row/
            display_dir = output / "displays" / "single_row"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            metadata = pd.read_csv(display_dir / "metadata.csv")
            assert len(metadata) == 1

    def test_many_columns_dataframe(self):
        """Test workflow with DataFrame with many columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create DataFrame with 20 columns
            data = {"plot": [f"p{i}" for i in range(5)]}
            for i in range(20):
                data[f"col_{i}"] = list(range(i, i + 5))

            df = pd.DataFrame(data)

            output = (
                Display(df, name="many_columns")
                .set_panel_column("plot")
                .infer_metas()
                .write(output_path=Path(tmpdir) / "output")
            )

            # Verify multi-display structure
            assert (output / "config.json").exists()
            assert (output / "index.html").exists()
            assert (output / "displays" / "displayList.json").exists()

            # Display files are in displays/many_columns/
            display_dir = output / "displays" / "many_columns"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            # Verify all metas created
            with open(display_dir / "displayInfo.json") as f:
                info = json.load(f)

            assert len(info["metas"]) == 21  # 20 col_ columns + 1 panel meta

    def test_unicode_in_data(self):
        """Test workflow with Unicode characters in data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame(
                {
                    "plot": ["p1", "p2", "p3"],
                    "text": ["café", "naïve", "日本語"],
                    "emoji": ["😀", "🎉", "🚀"],
                }
            )

            output = (
                Display(df, name="unicode_test", description="Unicode: café 中文")
                .set_panel_column("plot")
                .infer_metas()
                .write(output_path=Path(tmpdir) / "output")
            )

            # Verify multi-display structure
            assert (output / "config.json").exists()
            assert (output / "index.html").exists()
            assert (output / "displays" / "displayList.json").exists()

            # Display files are in displays/unicode_test/
            display_dir = output / "displays" / "unicode_test"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()

            # Verify Unicode preserved
            with open(display_dir / "displayInfo.json", encoding="utf-8") as f:
                info = json.load(f)

            assert "café" in info["description"]
            assert "中文" in info["description"]

            # Verify in metadata
            metadata = pd.read_csv(display_dir / "metadata.csv")
            assert metadata["text"][0] == "café"
            assert metadata["emoji"][2] == "🚀"


class TestWorkflowErrors:
    """Test error handling in workflow."""

    def test_write_without_panel_column(self):
        """Test that write fails if panel column not set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({"value": [1, 2, 3]})
            display = Display(df, name="test")

            with pytest.raises(ValueError, match="panel_column must be set"):
                display.write(output_path=tmpdir)

    def test_write_to_existing_without_force(self):
        """Test that write fails if directory exists and force=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output"
            output_path.mkdir()

            df = pd.DataFrame({"plot": ["p1"], "value": [1]})
            display = Display(df, name="test").set_panel_column("plot")

            with pytest.raises(ValueError, match="already exists"):
                display.write(output_path=output_path, force=False)

    def test_invalid_panel_column(self):
        """Test that invalid panel column raises error."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="not found in DataFrame"):
            display.set_panel_column("nonexistent")
