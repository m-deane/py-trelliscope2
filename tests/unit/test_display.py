"""
Unit tests for Display class.

Tests cover initialization, validation, configuration methods, and error handling.
"""

from pathlib import Path

import pandas as pd
import pytest

from trelliscope.display import Display


class TestDisplayInitialization:
    """Test Display.__init__ and basic initialization."""

    def test_display_creation_minimal(self):
        """Test creating display with minimal required parameters."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test_display")

        assert display.name == "test_display"
        assert display.description == ""
        assert len(display.data) == 3
        assert display.panel_column is None
        assert isinstance(display.keysig, str)
        assert len(display.keysig) == 32  # MD5 hex length

    def test_display_creation_full(self):
        """Test creating display with all parameters."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(
            df,
            name="test_display",
            description="Test description",
            keysig="abc123",
            path="/custom/path",
        )

        assert display.name == "test_display"
        assert display.description == "Test description"
        assert display.keysig == "abc123"
        assert display.path == Path("/custom/path")

    def test_display_default_path(self):
        """Test default path is ./trelliscope_output."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        assert display.path == Path("./trelliscope_output")

    def test_display_initializes_empty_config(self):
        """Test display initializes with empty configuration structures."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        assert display._meta_vars == {}
        assert isinstance(display.state, dict)
        assert "layout" in display.state
        assert "labels" in display.state
        assert "filters" in display.state
        assert "sorts" in display.state
        assert display.views == []
        assert isinstance(display.panel_options, dict)

    def test_display_copies_dataframe(self):
        """Test that display copies input DataFrame (no mutation)."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test")

        # Modify original
        df.loc[0, "value"] = 999

        # Display data should be unchanged
        assert display.data.loc[0, "value"] == 10

    def test_display_strips_whitespace_from_name(self):
        """Test that name whitespace is stripped."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="  test_display  ")

        assert display.name == "test_display"


class TestDisplayValidation:
    """Test Display input validation and error handling."""

    def test_invalid_data_type_raises_typeerror(self):
        """Test that non-DataFrame data raises TypeError."""
        with pytest.raises(TypeError, match="data must be a pandas DataFrame"):
            Display([1, 2, 3], name="test")

        with pytest.raises(TypeError, match="data must be a pandas DataFrame"):
            Display({"a": [1, 2, 3]}, name="test")

        with pytest.raises(TypeError, match="data must be a pandas DataFrame"):
            Display(None, name="test")

    def test_invalid_name_type_raises_valueerror(self):
        """Test that non-string name raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3]})

        with pytest.raises(ValueError, match="name must be a string"):
            Display(df, name=123)

        with pytest.raises(ValueError, match="name must be a string"):
            Display(df, name=None)

    def test_empty_name_raises_valueerror(self):
        """Test that empty name raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3]})

        with pytest.raises(ValueError, match="name cannot be empty"):
            Display(df, name="")

        with pytest.raises(ValueError, match="name cannot be empty"):
            Display(df, name="   ")


class TestSetPanelColumn:
    """Test Display.set_panel_column method."""

    def test_set_panel_column_valid(self):
        """Test setting valid panel column."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test")

        result = display.set_panel_column("plot")

        assert display.panel_column == "plot"
        assert result is display  # Returns self for chaining

    def test_set_panel_column_invalid_raises_valueerror(self):
        """Test that invalid column name raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="Column 'nonexistent' not found"):
            display.set_panel_column("nonexistent")

    def test_set_panel_column_shows_available_columns(self):
        """Test error message includes available columns."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test")

        with pytest.raises(
            ValueError, match="Available columns: \\['plot', 'value'\\]"
        ):
            display.set_panel_column("missing")


class TestSetDefaultLayout:
    """Test Display.set_default_layout method."""

    def test_set_layout_defaults(self):
        """Test setting layout with default values."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        result = display.set_default_layout()

        assert display.state["layout"]["ncol"] == 4
        assert display.state["layout"]["nrow"] is None
        assert display.state["layout"]["page"] == 1
        assert display.state["layout"]["arrangement"] == "row"
        assert result is display

    def test_set_layout_custom(self):
        """Test setting layout with custom values."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        display.set_default_layout(ncol=3, nrow=2, page=2, arrangement="col")

        assert display.state["layout"]["ncol"] == 3
        assert display.state["layout"]["nrow"] == 2
        assert display.state["layout"]["page"] == 2
        assert display.state["layout"]["arrangement"] == "col"

    def test_set_layout_invalid_ncol_raises_valueerror(self):
        """Test that ncol < 1 raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="ncol must be >= 1"):
            display.set_default_layout(ncol=0)

        with pytest.raises(ValueError, match="ncol must be >= 1"):
            display.set_default_layout(ncol=-1)

    def test_set_layout_invalid_page_raises_valueerror(self):
        """Test that page < 1 raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="page must be >= 1"):
            display.set_default_layout(page=0)

    def test_set_layout_invalid_arrangement_raises_valueerror(self):
        """Test that invalid arrangement raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="arrangement must be 'row' or 'col'"):
            display.set_default_layout(arrangement="invalid")

    def test_set_layout_invalid_nrow_raises_valueerror(self):
        """Test that nrow < 1 raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="nrow must be >= 1 or None"):
            display.set_default_layout(nrow=0)


class TestSetPanelOptions:
    """Test Display.set_panel_options method."""

    def test_set_panel_options_defaults(self):
        """Test panel options with defaults."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        result = display.set_panel_options()

        assert display.panel_options["width"] is None
        assert display.panel_options["height"] is None
        assert display.panel_options["aspect"] is None
        assert display.panel_options["forceSize"] is False
        assert result is display

    def test_set_panel_options_custom(self):
        """Test panel options with custom values."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        display.set_panel_options(width=800, height=600, force_size=True)

        assert display.panel_options["width"] == 800
        assert display.panel_options["height"] == 600
        assert display.panel_options["forceSize"] is True

    def test_set_panel_options_with_aspect(self):
        """Test panel options with aspect ratio."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        display.set_panel_options(width=800, aspect=1.5)

        assert display.panel_options["width"] == 800
        assert display.panel_options["aspect"] == 1.5

    def test_set_panel_options_invalid_width_raises_valueerror(self):
        """Test that width < 1 raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="width must be >= 1"):
            display.set_panel_options(width=0)

    def test_set_panel_options_invalid_height_raises_valueerror(self):
        """Test that height < 1 raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="height must be >= 1"):
            display.set_panel_options(height=0)

    def test_set_panel_options_invalid_aspect_raises_valueerror(self):
        """Test that aspect <= 0 raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="aspect must be > 0"):
            display.set_panel_options(aspect=0)

        with pytest.raises(ValueError, match="aspect must be > 0"):
            display.set_panel_options(aspect=-1.5)


class TestSetDefaultLabels:
    """Test Display.set_default_labels method."""

    def test_set_labels_valid(self):
        """Test setting valid labels."""
        df = pd.DataFrame(
            {"plot": [1, 2, 3], "cat": ["A", "B", "C"], "val": [10, 20, 30]}
        )
        display = Display(df, name="test")

        result = display.set_default_labels(["cat", "val"])

        assert display.state["labels"] == ["cat", "val"]
        assert result is display

    def test_set_labels_empty_list(self):
        """Test setting empty labels list."""
        df = pd.DataFrame({"plot": [1, 2, 3]})
        display = Display(df, name="test")

        display.set_default_labels([])

        assert display.state["labels"] == []

    def test_set_labels_invalid_column_raises_valueerror(self):
        """Test that invalid label column raises ValueError."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="Label columns not found"):
            display.set_default_labels(["nonexistent"])

    def test_set_labels_shows_available_columns(self):
        """Test error message includes available columns."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test")

        with pytest.raises(
            ValueError, match="Available columns: \\['plot', 'value'\\]"
        ):
            display.set_default_labels(["missing", "also_missing"])


class TestKeysigGeneration:
    """Test Display._generate_keysig method."""

    def test_keysig_is_md5_hash(self):
        """Test that generated keysig is valid MD5 hash."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test")

        assert isinstance(display.keysig, str)
        assert len(display.keysig) == 32
        assert all(c in "0123456789abcdef" for c in display.keysig)

    def test_keysig_different_for_different_data(self):
        """Test that different data produces different keysigs."""
        df1 = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        df2 = pd.DataFrame({"plot": [4, 5, 6], "value": [40, 50, 60]})

        display1 = Display(df1, name="test")
        display2 = Display(df2, name="test")

        assert display1.keysig != display2.keysig

    def test_keysig_different_for_different_names(self):
        """Test that different names produce different keysigs."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})

        display1 = Display(df, name="test1")
        display2 = Display(df, name="test2")

        assert display1.keysig != display2.keysig

    def test_keysig_same_for_same_data(self):
        """Test that same data produces same keysig."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})

        display1 = Display(df, name="test")
        display2 = Display(df, name="test")

        assert display1.keysig == display2.keysig


class TestMethodChaining:
    """Test that methods return self for chaining."""

    def test_method_chaining(self):
        """Test that multiple methods can be chained."""
        df = pd.DataFrame(
            {"plot": [1, 2, 3], "category": ["A", "B", "C"], "value": [10, 20, 30]}
        )

        display = (
            Display(df, name="test")
            .set_panel_column("plot")
            .set_default_layout(ncol=3, nrow=2)
            .set_panel_options(width=800, height=600)
            .set_default_labels(["category", "value"])
        )

        assert display.panel_column == "plot"
        assert display.state["layout"]["ncol"] == 3
        assert display.panel_options["width"] == 800
        assert display.state["labels"] == ["category", "value"]


class TestDisplayRepr:
    """Test Display.__repr__ method."""

    def test_repr_without_panel_column(self):
        """Test repr when panel column not set."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test_display")

        repr_str = repr(display)

        assert "name='test_display'" in repr_str
        assert "n_panels=3" in repr_str
        assert "n_columns=2" in repr_str
        assert "panel_column=not set" in repr_str

    def test_repr_with_panel_column(self):
        """Test repr when panel column is set."""
        df = pd.DataFrame({"plot": [1, 2, 3], "value": [10, 20, 30]})
        display = Display(df, name="test_display")
        display.set_panel_column("plot")

        repr_str = repr(display)

        assert "name='test_display'" in repr_str
        assert "n_panels=3" in repr_str
        assert "panel_column=set" in repr_str


class TestAddMetaVariable:
    """Test add_meta_variable method."""

    def test_add_meta_variable_valid(self):
        """Test adding valid meta variable."""
        from trelliscope.meta import FactorMeta

        df = pd.DataFrame({"category": ["A", "B", "C"]})
        display = Display(df, name="test")

        meta = FactorMeta("category", levels=["A", "B", "C"])
        result = display.add_meta_variable(meta)

        assert result is display  # Method chaining
        assert "category" in display._meta_vars
        assert display._meta_vars["category"] == meta

    def test_add_meta_variable_invalid_type(self):
        """Test that non-MetaVariable raises TypeError."""
        df = pd.DataFrame({"col": [1, 2]})
        display = Display(df, name="test")

        with pytest.raises(TypeError, match="meta must be a MetaVariable"):
            display.add_meta_variable("not a meta")

    def test_add_meta_variable_invalid_column(self):
        """Test that meta for non-existent column raises ValueError."""
        from trelliscope.meta import NumberMeta

        df = pd.DataFrame({"col": [1, 2]})
        display = Display(df, name="test")

        meta = NumberMeta("nonexistent")
        with pytest.raises(ValueError, match="not found in DataFrame"):
            display.add_meta_variable(meta)

    def test_add_meta_variable_duplicate_without_replace(self):
        """Test that duplicate meta without replace raises ValueError."""
        from trelliscope.meta import NumberMeta

        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")

        meta1 = NumberMeta("value", digits=2)
        meta2 = NumberMeta("value", digits=4)

        display.add_meta_variable(meta1)
        with pytest.raises(ValueError, match="already exists"):
            display.add_meta_variable(meta2)

    def test_add_meta_variable_duplicate_with_replace(self):
        """Test that replace=True allows overwriting meta."""
        from trelliscope.meta import NumberMeta

        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")

        meta1 = NumberMeta("value", digits=2)
        meta2 = NumberMeta("value", digits=4)

        display.add_meta_variable(meta1)
        display.add_meta_variable(meta2, replace=True)

        assert display._meta_vars["value"].digits == 4


class TestAddMetaDef:
    """Test add_meta_def method."""

    def test_add_meta_def_factor(self):
        """Test defining factor meta inline."""
        df = pd.DataFrame({"category": ["A", "B"]})
        display = Display(df, name="test")

        result = display.add_meta_def("category", "factor", levels=["A", "B", "C"])

        assert result is display
        assert "category" in display._meta_vars
        assert display._meta_vars["category"].type == "factor"
        assert display._meta_vars["category"].levels == ["A", "B", "C"]

    def test_add_meta_def_number(self):
        """Test defining number meta inline."""
        df = pd.DataFrame({"value": [1.5, 2.7]})
        display = Display(df, name="test")

        display.add_meta_def("value", "number", digits=4, log=True)

        meta = display._meta_vars["value"]
        assert meta.type == "number"
        assert meta.digits == 4
        assert meta.log is True

    def test_add_meta_def_all_types(self):
        """Test defining all meta types."""
        df = pd.DataFrame(
            {
                "cat": ["A"],
                "num": [1.0],
                "dt": [pd.Timestamp("2024-01-01")],
                "time": [pd.Timestamp("2024-01-01 12:00")],
                "price": [10.50],
                "link": ["http://example.com"],
                "graph": ["plot_data"],
            }
        )
        display = Display(df, name="test")

        display.add_meta_def("cat", "factor")
        display.add_meta_def("num", "number")
        display.add_meta_def("dt", "date")
        display.add_meta_def("time", "time")
        display.add_meta_def("price", "currency")
        display.add_meta_def("link", "href")
        display.add_meta_def("graph", "graph")

        assert len(display._meta_vars) == 7

    def test_add_meta_def_unknown_type(self):
        """Test that unknown meta_type raises ValueError."""
        df = pd.DataFrame({"col": [1, 2]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="Unknown meta_type"):
            display.add_meta_def("col", "unknown_type")


class TestInferMetas:
    """Test infer_metas method."""

    def test_infer_metas_all_columns(self):
        """Test inferring all columns."""
        df = pd.DataFrame(
            {"id": [1, 2, 3], "category": ["A", "B", "C"], "value": [1.5, 2.7, 3.9]}
        )
        display = Display(df, name="test")

        result = display.infer_metas()

        assert result is display
        assert len(display._meta_vars) == 3
        assert display._meta_vars["id"].type == "number"
        assert display._meta_vars["category"].type == "factor"
        assert display._meta_vars["value"].type == "number"

    def test_infer_metas_specific_columns(self):
        """Test inferring specific columns only."""
        df = pd.DataFrame({"id": [1, 2], "category": ["A", "B"], "value": [1.5, 2.7]})
        display = Display(df, name="test")

        display.infer_metas(columns=["category", "value"])

        assert len(display._meta_vars) == 2
        assert "category" in display._meta_vars
        assert "value" in display._meta_vars
        assert "id" not in display._meta_vars

    def test_infer_metas_invalid_column(self):
        """Test that invalid column raises ValueError."""
        df = pd.DataFrame({"col": [1, 2]})
        display = Display(df, name="test")

        with pytest.raises(ValueError, match="not found in DataFrame"):
            display.infer_metas(columns=["nonexistent"])

    def test_infer_metas_skip_existing(self):
        """Test that existing metas are skipped without replace."""
        from trelliscope.meta import NumberMeta

        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")

        # Add explicit meta with custom settings
        custom_meta = NumberMeta("value", digits=5)
        display.add_meta_variable(custom_meta)

        # Infer without replace - should skip
        display.infer_metas()

        # Custom settings should be preserved
        assert display._meta_vars["value"].digits == 5

    def test_infer_metas_replace_existing(self):
        """Test that existing metas are replaced with replace=True."""
        from trelliscope.meta import NumberMeta

        df = pd.DataFrame({"value": [1, 2]})
        display = Display(df, name="test")

        # Add explicit meta with custom settings
        custom_meta = NumberMeta("value", digits=5)
        display.add_meta_variable(custom_meta)

        # Infer with replace - should replace
        display.infer_metas(replace=True)

        # Should be replaced with default settings
        assert display._meta_vars["value"].digits == 2

    def test_infer_metas_skips_panel_column(self):
        """Test that panel column is automatically skipped during inference."""
        # Create DataFrame with unhashable objects in panel column
        df = pd.DataFrame(
            {
                "panel": [{"a": 1}, {"b": 2}],  # Unhashable dicts
                "category": ["A", "B"],
                "value": [10, 20],
            }
        )
        display = Display(df, name="test").set_panel_column("panel")

        # Should not raise TypeError when trying to infer panel column
        display.infer_metas()

        # Panel column should not be in meta variables
        assert "panel" not in display._meta_vars
        assert "category" in display._meta_vars
        assert "value" in display._meta_vars
        assert len(display._meta_vars) == 2


class TestGetMetaVariable:
    """Test get_meta_variable method."""

    def test_get_meta_variable_exists(self):
        """Test getting existing meta variable."""
        from trelliscope.meta import FactorMeta

        df = pd.DataFrame({"category": ["A", "B"]})
        display = Display(df, name="test")

        meta = FactorMeta("category", levels=["A", "B"])
        display.add_meta_variable(meta)

        retrieved = display.get_meta_variable("category")
        assert retrieved == meta

    def test_get_meta_variable_not_found(self):
        """Test that non-existent meta raises KeyError."""
        df = pd.DataFrame({"col": [1, 2]})
        display = Display(df, name="test")

        with pytest.raises(KeyError, match="not found"):
            display.get_meta_variable("nonexistent")


class TestGetAllMetaVariables:
    """Test get_all_meta_variables method."""

    def test_get_all_meta_variables_empty(self):
        """Test getting all metas when none exist."""
        df = pd.DataFrame({"col": [1, 2]})
        display = Display(df, name="test")

        metas = display.get_all_meta_variables()
        assert metas == {}

    def test_get_all_meta_variables_populated(self):
        """Test getting all metas when some exist."""
        df = pd.DataFrame({"cat": ["A", "B"], "val": [1, 2]})
        display = Display(df, name="test")
        display.infer_metas()

        metas = display.get_all_meta_variables()

        assert len(metas) == 2
        assert "cat" in metas
        assert "val" in metas

    def test_get_all_meta_variables_is_copy(self):
        """Test that returned dict is a copy."""
        df = pd.DataFrame({"col": [1, 2]})
        display = Display(df, name="test")
        display.infer_metas()

        metas = display.get_all_meta_variables()
        metas["new_key"] = "should not affect display"

        assert "new_key" not in display._meta_vars


class TestListMetaVariables:
    """Test list_meta_variables method."""

    def test_list_meta_variables_empty(self):
        """Test listing when no metas exist."""
        df = pd.DataFrame({"col": [1, 2]})
        display = Display(df, name="test")

        names = display.list_meta_variables()
        assert names == []

    def test_list_meta_variables_sorted(self):
        """Test that meta names are sorted."""
        df = pd.DataFrame({"z_col": [1], "a_col": [2], "m_col": [3]})
        display = Display(df, name="test")
        display.infer_metas()

        names = display.list_meta_variables()
        assert names == ["a_col", "m_col", "z_col"]


class TestMetaMethodChaining:
    """Test method chaining with meta methods."""

    def test_meta_method_chaining(self):
        """Test chaining multiple meta methods."""
        df = pd.DataFrame({"category": ["A", "B"], "value": [1.5, 2.7]})
        display = Display(df, name="test")

        result = (
            display.infer_metas(columns=["category"])
            .add_meta_def("value", "number", digits=3)
            .set_panel_column("category")
        )

        assert result is display
        assert len(display._meta_vars) == 2
        assert display.panel_column == "category"


class TestDisplayWrite:
    """Test Display.write() method."""

    def test_write_creates_output_directory(self):
        """Test that write() creates output directory."""
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output"

            df = pd.DataFrame({"plot": ["p1", "p2"], "value": [1, 2]})
            display = Display(df, name="test")
            display.set_panel_column("plot")
            display.infer_metas()

            result_path = display.write(output_path=output_path)

            assert result_path.exists()
            assert result_path.is_dir()

    def test_write_creates_displayinfo_json(self):
        """Test that write() creates displayInfo.json."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output"

            df = pd.DataFrame({"plot": ["p1", "p2"], "value": [1, 2]})
            display = Display(df, name="test")
            display.set_panel_column("plot")
            display.infer_metas()

            display.write(output_path=output_path)

            json_path = output_path / "displays" / "test" / "displayInfo.json"
            assert json_path.exists()

    def test_write_creates_metadata_csv(self):
        """Test that write() creates metadata.csv."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output"

            df = pd.DataFrame(
                {"plot": ["p1", "p2"], "category": ["A", "B"], "value": [1, 2]}
            )
            display = Display(df, name="test")
            display.set_panel_column("plot")
            display.infer_metas()

            display.write(output_path=output_path)

            csv_path = output_path / "displays" / "test" / "metadata.csv"
            assert csv_path.exists()

            # Read and verify CSV
            metadata = pd.read_csv(csv_path)
            assert "category" in metadata.columns
            assert "value" in metadata.columns
            assert "plot" not in metadata.columns  # Panel col excluded

    def test_write_uses_display_path_by_default(self):
        """Test that write() uses display.path / display.name by default."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({"plot": ["p1", "p2"], "value": [1, 2]})
            display = Display(df, name="test_display", path=tmpdir)
            display.set_panel_column("plot")
            display.infer_metas()

            result_path = display.write()

            expected_path = Path(tmpdir) / "test_display"
            assert result_path == expected_path
            assert result_path.exists()

    def test_write_without_panel_column_raises_error(self):
        """Test that write() raises error if panel_column not set."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({"value": [1, 2]})
            display = Display(df, name="test")

            with pytest.raises(ValueError, match="panel_column must be set"):
                display.write(output_path=tmpdir)

    def test_write_existing_directory_without_force_raises_error(self):
        """Test that write() raises error if directory exists and force=False."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output"
            output_path.mkdir()  # Create directory

            df = pd.DataFrame({"plot": ["p1", "p2"], "value": [1, 2]})
            display = Display(df, name="test")
            display.set_panel_column("plot")

            with pytest.raises(ValueError, match="already exists"):
                display.write(output_path=output_path, force=False)

    def test_write_existing_directory_with_force_succeeds(self):
        """Test that write() succeeds if directory exists and force=True."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output"
            output_path.mkdir()  # Create directory

            df = pd.DataFrame({"plot": ["p1", "p2"], "value": [1, 2]})
            display = Display(df, name="test")
            display.set_panel_column("plot")
            display.infer_metas()

            # Should not raise
            result_path = display.write(output_path=output_path, force=True)
            assert result_path.exists()

    def test_write_returns_output_path(self):
        """Test that write() returns the output path."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output"

            df = pd.DataFrame({"plot": ["p1", "p2"], "value": [1, 2]})
            display = Display(df, name="test")
            display.set_panel_column("plot")

            result = display.write(output_path=output_path)

            assert isinstance(result, Path)
            assert result == output_path

    def test_write_with_method_chaining(self):
        """Test write() can be used in method chain."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output"

            df = pd.DataFrame(
                {"plot": ["p1", "p2"], "category": ["A", "B"], "value": [1.5, 2.7]}
            )

            output = (
                Display(df, name="test")
                .set_panel_column("plot")
                .infer_metas()
                .set_default_layout(ncol=2)
                .write(output_path=output_path)
            )

            assert output.exists()
            assert (output / "displays" / "test" / "displayInfo.json").exists()
