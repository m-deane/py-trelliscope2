"""
Unit tests for meta variable type inference.

Tests cover automatic type detection from pandas Series dtypes,
including edge cases and fallback behavior.
"""

from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from trelliscope.inference import infer_meta_dict, infer_meta_from_series
from trelliscope.meta import (
    DateMeta,
    FactorMeta,
    NumberMeta,
    TimeMeta,
)


class TestInferNumericTypes:
    """Test inference of numeric types."""

    def test_integer_series_infers_number(self):
        """Test that integer series infers as NumberMeta."""
        series = pd.Series([1, 2, 3], name="count")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, NumberMeta)
        assert meta.type == "number"
        assert meta.varname == "count"

    def test_float_series_infers_number(self):
        """Test that float series infers as NumberMeta."""
        series = pd.Series([1.5, 2.7, 3.9], name="value")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, NumberMeta)
        assert meta.type == "number"

    def test_mixed_int_float_infers_number(self):
        """Test that mixed int/float infers as NumberMeta."""
        series = pd.Series([1, 2.5, 3], name="mixed")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, NumberMeta)

    def test_numeric_with_nan_infers_number(self):
        """Test that numeric series with NaN still infers as number."""
        series = pd.Series([1.0, np.nan, 3.0], name="value")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, NumberMeta)

    def test_all_nan_numeric_infers_number(self):
        """Test that all-NaN numeric series infers as number."""
        series = pd.Series([np.nan, np.nan], dtype=float, name="value")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, NumberMeta)


class TestInferCategoricalTypes:
    """Test inference of categorical/factor types."""

    def test_string_series_infers_factor(self):
        """Test that string series infers as FactorMeta."""
        series = pd.Series(["A", "B", "C"], name="category")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, FactorMeta)
        assert meta.type == "factor"
        assert set(meta.levels) == {"A", "B", "C"}

    def test_object_series_infers_factor(self):
        """Test that object dtype series infers as FactorMeta."""
        series = pd.Series(["A", "B", "C"], dtype=object, name="category")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, FactorMeta)

    def test_categorical_dtype_infers_factor(self):
        """Test that categorical dtype infers as FactorMeta."""
        series = pd.Series(pd.Categorical(["A", "B", "C"]), name="category")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, FactorMeta)
        assert set(meta.levels) == {"A", "B", "C"}

    def test_boolean_infers_factor_with_true_false(self):
        """Test that boolean series infers as FactorMeta with False/True."""
        series = pd.Series([True, False, True], name="flag")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, FactorMeta)
        assert meta.levels == ["False", "True"]

    def test_string_with_nan_infers_factor(self):
        """Test that string series with NaN infers as factor."""
        series = pd.Series(["A", None, "C"], name="category")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, FactorMeta)
        assert set(meta.levels) == {"A", "C"}


class TestInferDatetimeTypes:
    """Test inference of date and time types."""

    def test_date_only_infers_date(self):
        """Test that date-only datetime infers as DateMeta."""
        series = pd.Series(
            pd.date_range("2024-01-01", periods=3, freq="D"), name="date"
        )
        meta = infer_meta_from_series(series)

        assert isinstance(meta, DateMeta)
        assert meta.type == "date"

    def test_datetime_with_time_infers_time(self):
        """Test that datetime with time component infers as TimeMeta."""
        series = pd.Series(
            pd.date_range("2024-01-01", periods=3, freq="h"), name="timestamp"
        )
        meta = infer_meta_from_series(series)

        assert isinstance(meta, TimeMeta)
        assert meta.type == "time"

    def test_timezone_aware_infers_time(self):
        """Test that timezone-aware datetime infers as TimeMeta."""
        series = pd.Series(
            pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC"), name="timestamp"
        )
        meta = infer_meta_from_series(series)

        assert isinstance(meta, TimeMeta)
        assert meta.timezone == "UTC"

    def test_datetime_with_microseconds_infers_time(self):
        """Test that datetime with microseconds infers as TimeMeta."""
        dates = pd.to_datetime(
            [
                "2024-01-01 00:00:00.123456",
                "2024-01-02 00:00:00.654321",
            ]
        )
        series = pd.Series(dates, name="timestamp")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, TimeMeta)

    def test_datetime_with_seconds_infers_time(self):
        """Test that datetime with seconds infers as TimeMeta."""
        dates = pd.to_datetime(
            [
                "2024-01-01 00:00:01",
                "2024-01-01 00:00:02",
            ]
        )
        series = pd.Series(dates, name="timestamp")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, TimeMeta)

    def test_datetime_midnight_only_infers_date(self):
        """Test that datetime at midnight with no time infers as DateMeta."""
        dates = pd.to_datetime(
            [
                "2024-01-01 00:00:00",
                "2024-01-02 00:00:00",
                "2024-01-03 00:00:00",
            ]
        )
        series = pd.Series(dates, name="date")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, DateMeta)

    def test_datetime_with_nat_infers_date(self):
        """Test that datetime with NaT values still infers correctly."""
        dates = pd.to_datetime(
            [
                "2024-01-01",
                pd.NaT,
                "2024-01-03",
            ]
        )
        series = pd.Series(dates, name="date")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, DateMeta)


class TestInferEdgeCases:
    """Test inference edge cases."""

    def test_empty_series_infers_factor_with_empty_levels(self):
        """Test that empty series infers as FactorMeta with empty levels."""
        series = pd.Series([], dtype=object, name="empty")
        meta = infer_meta_from_series(series)

        assert isinstance(meta, FactorMeta)
        assert meta.levels == []

    def test_series_without_name_requires_varname(self):
        """Test that series without name requires varname parameter."""
        series = pd.Series([1, 2, 3])

        with pytest.raises(ValueError, match="varname must be provided"):
            infer_meta_from_series(series)

    def test_explicit_varname_overrides_series_name(self):
        """Test that explicit varname overrides series.name."""
        series = pd.Series([1, 2, 3], name="old_name")
        meta = infer_meta_from_series(series, varname="new_name")

        assert meta.varname == "new_name"

    def test_additional_kwargs_passed_to_meta_constructor(self):
        """Test that additional kwargs are passed to meta constructor."""
        series = pd.Series([1.5, 2.7], name="value")
        meta = infer_meta_from_series(series, digits=4, log=True)

        assert isinstance(meta, NumberMeta)
        assert meta.digits == 4
        assert meta.log is True

    def test_explicit_levels_override_inference(self):
        """Test that explicit levels override inferred levels."""
        series = pd.Series(["A", "B"], name="category")
        meta = infer_meta_from_series(series, levels=["A", "B", "C", "D"])

        assert isinstance(meta, FactorMeta)
        assert meta.levels == ["A", "B", "C", "D"]


class TestInferMetaDict:
    """Test infer_meta_dict function for multiple columns."""

    def test_infer_all_columns(self):
        """Test inferring meta for all DataFrame columns."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "category": ["A", "B", "C"],
                "value": [1.5, 2.7, 3.9],
                "date": pd.date_range("2024-01-01", periods=3),
            }
        )
        metas = infer_meta_dict(df)

        assert len(metas) == 4
        assert isinstance(metas["id"], NumberMeta)
        assert isinstance(metas["category"], FactorMeta)
        assert isinstance(metas["value"], NumberMeta)
        assert isinstance(metas["date"], DateMeta)

    def test_infer_specific_columns(self):
        """Test inferring meta for specific columns only."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "category": ["A", "B", "C"],
                "value": [1.5, 2.7, 3.9],
            }
        )
        metas = infer_meta_dict(df, columns=["category", "value"])

        assert len(metas) == 2
        assert "category" in metas
        assert "value" in metas
        assert "id" not in metas

    def test_infer_empty_dataframe(self):
        """Test inferring from empty DataFrame."""
        df = pd.DataFrame()
        metas = infer_meta_dict(df)

        assert metas == {}

    def test_infer_single_column(self):
        """Test inferring single column."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        metas = infer_meta_dict(df)

        assert len(metas) == 1
        assert isinstance(metas["value"], NumberMeta)

    def test_column_names_as_varnames(self):
        """Test that column names are used as varnames."""
        df = pd.DataFrame(
            {
                "col_a": [1, 2],
                "col_b": ["X", "Y"],
            }
        )
        metas = infer_meta_dict(df)

        assert metas["col_a"].varname == "col_a"
        assert metas["col_b"].varname == "col_b"


class TestInferFallbackBehavior:
    """Test fallback behavior for unknown types."""

    def test_complex_dtype_infers_as_number(self):
        """Test that complex numbers infer as NumberMeta (are numeric)."""
        # Complex dtype is numeric in pandas
        series = pd.Series([1 + 2j, 3 + 4j], name="complex")
        meta = infer_meta_from_series(series)

        # Complex numbers are numeric, so should infer as NumberMeta
        assert isinstance(meta, NumberMeta)

    def test_timedelta_infers_as_factor(self):
        """Test that timedelta infers as FactorMeta (fallback behavior)."""
        series = pd.Series(
            pd.to_timedelta(["1 days", "2 days", "3 days"]), name="duration"
        )
        meta = infer_meta_from_series(series)

        # Timedelta is not considered numeric by pandas, falls back to FactorMeta
        assert isinstance(meta, FactorMeta)
        assert len(meta.levels) == 3
