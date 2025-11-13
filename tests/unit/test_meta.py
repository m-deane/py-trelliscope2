"""
Unit tests for Meta variable classes.

Tests cover all meta variable types, initialization, serialization,
and inference from pandas Series.
"""

from datetime import datetime

import pandas as pd
import pytest

from trelliscope.meta import (
    CurrencyMeta,
    DateMeta,
    FactorMeta,
    GraphMeta,
    HrefMeta,
    MetaVariable,
    NumberMeta,
    TimeMeta,
)


class TestMetaVariable:
    """Test MetaVariable base class."""

    def test_initialization_minimal(self):
        """Test creating meta variable with minimal parameters."""
        meta = MetaVariable(varname="test")

        assert meta.varname == "test"
        assert meta.label == "test"  # Defaults to varname
        assert meta.desc is None
        assert meta.type == ""

    def test_initialization_with_label(self):
        """Test that custom label is used."""
        meta = MetaVariable(varname="test", label="Test Label")

        assert meta.label == "Test Label"

    def test_initialization_with_desc(self):
        """Test that description is stored."""
        meta = MetaVariable(varname="test", desc="Test description")

        assert meta.desc == "Test description"

    def test_to_dict_minimal(self):
        """Test to_dict with minimal parameters."""
        meta = MetaVariable(varname="test")
        result = meta.to_dict()

        assert result == {
            "varname": "test",
            "label": "test",
            "type": "",
        }

    def test_to_dict_with_desc(self):
        """Test to_dict includes description if provided."""
        meta = MetaVariable(varname="test", desc="Test desc")
        result = meta.to_dict()

        assert result["desc"] == "Test desc"

    def test_from_series_with_name(self):
        """Test creating from series with name."""
        series = pd.Series([1, 2, 3], name="test_col")
        meta = MetaVariable.from_series(series)

        assert meta.varname == "test_col"

    def test_from_series_with_explicit_varname(self):
        """Test that explicit varname overrides series.name."""
        series = pd.Series([1, 2, 3], name="series_name")
        meta = MetaVariable.from_series(series, varname="explicit_name")

        assert meta.varname == "explicit_name"

    def test_from_series_without_name_raises_error(self):
        """Test that series without name and no varname param raises error."""
        series = pd.Series([1, 2, 3])  # No name

        with pytest.raises(ValueError, match="varname must be provided"):
            MetaVariable.from_series(series)


class TestFactorMeta:
    """Test FactorMeta class."""

    def test_initialization_minimal(self):
        """Test creating FactorMeta with minimal parameters."""
        meta = FactorMeta(varname="category")

        assert meta.varname == "category"
        assert meta.type == "factor"
        assert meta.levels is None

    def test_initialization_with_levels(self):
        """Test creating with explicit levels."""
        meta = FactorMeta(varname="category", levels=["A", "B", "C"])

        assert meta.levels == ["A", "B", "C"]

    def test_to_dict_without_levels(self):
        """Test to_dict when levels not provided."""
        meta = FactorMeta(varname="category")
        result = meta.to_dict()

        assert result["type"] == "factor"
        assert "levels" not in result

    def test_to_dict_with_levels(self):
        """Test to_dict includes levels when provided."""
        meta = FactorMeta(varname="category", levels=["A", "B", "C"])
        result = meta.to_dict()

        assert result["levels"] == ["A", "B", "C"]

    def test_from_series_infers_levels(self):
        """Test that levels are inferred from series unique values."""
        series = pd.Series(["B", "A", "C", "A", "B"], name="category")
        meta = FactorMeta.from_series(series)

        assert meta.varname == "category"
        assert set(meta.levels) == {"A", "B", "C"}
        assert meta.levels == sorted(meta.levels)  # Should be sorted

    def test_from_series_excludes_nan(self):
        """Test that NaN values are excluded from levels."""
        series = pd.Series(["A", "B", None, "C", pd.NA], name="category")
        meta = FactorMeta.from_series(series)

        # Verify only actual string values are in levels (NA values excluded)
        assert set(meta.levels) == {"A", "B", "C"}
        assert "None" not in meta.levels

    def test_from_series_with_explicit_levels(self):
        """Test that explicit levels override inference."""
        series = pd.Series(["A", "B"], name="category")
        meta = FactorMeta.from_series(series, levels=["A", "B", "C", "D"])

        assert meta.levels == ["A", "B", "C", "D"]


class TestNumberMeta:
    """Test NumberMeta class."""

    def test_initialization_defaults(self):
        """Test NumberMeta default values."""
        meta = NumberMeta(varname="value")

        assert meta.type == "number"
        assert meta.digits == 2
        assert meta.locale is False
        assert meta.log is False

    def test_initialization_custom(self):
        """Test NumberMeta with custom values."""
        meta = NumberMeta(varname="value", digits=4, locale=True, log=True)

        assert meta.digits == 4
        assert meta.locale is True
        assert meta.log is True

    def test_to_dict(self):
        """Test to_dict includes all numeric options."""
        meta = NumberMeta(varname="value", digits=3, locale=True, log=False)
        result = meta.to_dict()

        assert result["type"] == "number"
        assert result["digits"] == 3
        assert result["locale"] is True
        assert result["log"] is False

    def test_from_series(self):
        """Test creating from numeric series."""
        series = pd.Series([1.5, 2.7, 3.9], name="values")
        meta = NumberMeta.from_series(series)

        assert meta.varname == "values"
        assert meta.type == "number"


class TestDateMeta:
    """Test DateMeta class."""

    def test_initialization_minimal(self):
        """Test DateMeta with minimal parameters."""
        meta = DateMeta(varname="date")

        assert meta.type == "date"
        assert meta.format is None

    def test_initialization_with_format(self):
        """Test DateMeta with format string."""
        meta = DateMeta(varname="date", format="%Y-%m-%d")

        assert meta.format == "%Y-%m-%d"

    def test_to_dict_without_format(self):
        """Test to_dict when format not provided."""
        meta = DateMeta(varname="date")
        result = meta.to_dict()

        assert result["type"] == "date"
        assert "format" not in result

    def test_to_dict_with_format(self):
        """Test to_dict includes format when provided."""
        meta = DateMeta(varname="date", format="%Y-%m-%d")
        result = meta.to_dict()

        assert result["format"] == "%Y-%m-%d"

    def test_from_series(self):
        """Test creating from datetime series."""
        series = pd.Series(pd.date_range("2024-01-01", periods=3), name="dates")
        meta = DateMeta.from_series(series)

        assert meta.varname == "dates"
        assert meta.type == "date"


class TestTimeMeta:
    """Test TimeMeta class."""

    def test_initialization_minimal(self):
        """Test TimeMeta with minimal parameters."""
        meta = TimeMeta(varname="timestamp")

        assert meta.type == "time"
        assert meta.timezone is None
        assert meta.format is None

    def test_initialization_with_timezone(self):
        """Test TimeMeta with timezone."""
        meta = TimeMeta(varname="timestamp", timezone="UTC")

        assert meta.timezone == "UTC"

    def test_initialization_with_format(self):
        """Test TimeMeta with format string."""
        meta = TimeMeta(varname="timestamp", format="%Y-%m-%d %H:%M:%S")

        assert meta.format == "%Y-%m-%d %H:%M:%S"

    def test_to_dict_minimal(self):
        """Test to_dict without optional fields."""
        meta = TimeMeta(varname="timestamp")
        result = meta.to_dict()

        assert result["type"] == "time"
        assert "timezone" not in result
        assert "format" not in result

    def test_to_dict_with_all_fields(self):
        """Test to_dict with all fields."""
        meta = TimeMeta(
            varname="timestamp", timezone="America/New_York", format="%Y-%m-%d %H:%M:%S"
        )
        result = meta.to_dict()

        assert result["timezone"] == "America/New_York"
        assert result["format"] == "%Y-%m-%d %H:%M:%S"

    def test_from_series_without_tz(self):
        """Test creating from datetime series without timezone."""
        series = pd.Series(
            pd.date_range("2024-01-01", periods=3, freq="h"), name="timestamps"
        )
        meta = TimeMeta.from_series(series)

        assert meta.varname == "timestamps"
        assert meta.timezone is None

    def test_from_series_with_tz(self):
        """Test creating from timezone-aware datetime series."""
        series = pd.Series(
            pd.date_range("2024-01-01", periods=3, freq="h", tz="UTC"),
            name="timestamps",
        )
        meta = TimeMeta.from_series(series)

        assert meta.timezone == "UTC"

    def test_from_series_explicit_timezone_overrides(self):
        """Test that explicit timezone overrides inferred timezone."""
        series = pd.Series(
            pd.date_range("2024-01-01", periods=3, freq="h", tz="UTC"),
            name="timestamps",
        )
        meta = TimeMeta.from_series(series, timezone="America/New_York")

        assert meta.timezone == "America/New_York"


class TestCurrencyMeta:
    """Test CurrencyMeta class."""

    def test_initialization_defaults(self):
        """Test CurrencyMeta default values."""
        meta = CurrencyMeta(varname="price")

        assert meta.type == "currency"
        assert meta.code == "USD"
        assert meta.digits == 2
        assert meta.locale is True

    def test_initialization_custom(self):
        """Test CurrencyMeta with custom values."""
        meta = CurrencyMeta(varname="price", code="EUR", digits=3, locale=False)

        assert meta.code == "EUR"
        assert meta.digits == 3
        assert meta.locale is False

    def test_to_dict(self):
        """Test to_dict includes all currency options."""
        meta = CurrencyMeta(varname="price", code="GBP", digits=2, locale=True)
        result = meta.to_dict()

        assert result["type"] == "currency"
        assert result["code"] == "GBP"
        assert result["digits"] == 2
        assert result["locale"] is True


class TestHrefMeta:
    """Test HrefMeta class."""

    def test_initialization_minimal(self):
        """Test HrefMeta with minimal parameters."""
        meta = HrefMeta(varname="link")

        assert meta.type == "href"
        assert meta.label_col is None

    def test_initialization_with_label_col(self):
        """Test HrefMeta with label column."""
        meta = HrefMeta(varname="link", label_col="link_text")

        assert meta.label_col == "link_text"

    def test_to_dict_without_label_col(self):
        """Test to_dict when label_col not provided."""
        meta = HrefMeta(varname="link")
        result = meta.to_dict()

        assert result["type"] == "href"
        assert "label_col" not in result

    def test_to_dict_with_label_col(self):
        """Test to_dict includes label_col when provided."""
        meta = HrefMeta(varname="link", label_col="link_text")
        result = meta.to_dict()

        assert result["label_col"] == "link_text"


class TestGraphMeta:
    """Test GraphMeta class."""

    def test_initialization_minimal(self):
        """Test GraphMeta with minimal parameters."""
        meta = GraphMeta(varname="trend")

        assert meta.type == "graph"
        assert meta.direction is None
        assert meta.idvarname is None

    def test_initialization_with_direction(self):
        """Test GraphMeta with direction."""
        meta = GraphMeta(varname="trend", direction="up")

        assert meta.direction == "up"

    def test_initialization_with_idvarname(self):
        """Test GraphMeta with ID variable."""
        meta = GraphMeta(varname="trend", idvarname="id")

        assert meta.idvarname == "id"

    def test_to_dict_minimal(self):
        """Test to_dict without optional fields."""
        meta = GraphMeta(varname="trend")
        result = meta.to_dict()

        assert result["type"] == "graph"
        assert "direction" not in result
        assert "idvarname" not in result

    def test_to_dict_with_all_fields(self):
        """Test to_dict with all fields."""
        meta = GraphMeta(varname="trend", direction="down", idvarname="id")
        result = meta.to_dict()

        assert result["direction"] == "down"
        assert result["idvarname"] == "id"


class TestMetaVariableEquality:
    """Test meta variable equality and comparison."""

    def test_same_attributes_equal(self):
        """Test that meta variables with same attributes are equal."""
        meta1 = NumberMeta(varname="value", digits=3)
        meta2 = NumberMeta(varname="value", digits=3)

        assert meta1 == meta2

    def test_different_attributes_not_equal(self):
        """Test that meta variables with different attributes are not equal."""
        meta1 = NumberMeta(varname="value", digits=3)
        meta2 = NumberMeta(varname="value", digits=2)

        assert meta1 != meta2

    def test_different_types_not_equal(self):
        """Test that different meta variable types are not equal."""
        meta1 = NumberMeta(varname="value")
        meta2 = FactorMeta(varname="value")

        assert meta1 != meta2
