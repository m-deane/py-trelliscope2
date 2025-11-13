"""
Unit tests for validation utilities.

Tests cover all validation functions with valid inputs, invalid inputs,
edge cases, and error messages.
"""

import pandas as pd
import pytest

from trelliscope.utils.validation import (
    validate_choice,
    validate_column_exists,
    validate_columns_exist,
    validate_dataframe,
    validate_dataframe_not_empty,
    validate_list_of_strings,
    validate_numeric_positive,
    validate_positive_integer,
    validate_string_nonempty,
)


class TestValidateDataFrame:
    """Test validate_dataframe function."""

    def test_valid_dataframe(self):
        """Test that valid DataFrame is returned unchanged."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = validate_dataframe(df)
        assert result is df

    def test_invalid_type_list(self):
        """Test that list raises TypeError."""
        with pytest.raises(TypeError, match="data must be a pandas DataFrame"):
            validate_dataframe([1, 2, 3])

    def test_invalid_type_dict(self):
        """Test that dict raises TypeError."""
        with pytest.raises(TypeError, match="data must be a pandas DataFrame"):
            validate_dataframe({"a": [1, 2, 3]})

    def test_invalid_type_none(self):
        """Test that None raises TypeError."""
        with pytest.raises(TypeError, match="data must be a pandas DataFrame"):
            validate_dataframe(None)

    def test_custom_param_name(self):
        """Test that custom param_name appears in error."""
        with pytest.raises(TypeError, match="my_df must be a pandas DataFrame"):
            validate_dataframe([1, 2, 3], param_name="my_df")


class TestValidateColumnExists:
    """Test validate_column_exists function."""

    def test_valid_column(self):
        """Test that valid column is returned."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        result = validate_column_exists(df, "a")
        assert result == "a"

    def test_invalid_column(self):
        """Test that invalid column raises ValueError."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with pytest.raises(ValueError, match="column 'c' not found"):
            validate_column_exists(df, "c")

    def test_error_shows_available_columns(self):
        """Test that error message includes available columns."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with pytest.raises(ValueError, match="Available columns: \\['a', 'b'\\]"):
            validate_column_exists(df, "c")

    def test_custom_param_name(self):
        """Test that custom param_name appears in error."""
        df = pd.DataFrame({"a": [1, 2]})
        with pytest.raises(ValueError, match="panel_col 'b' not found"):
            validate_column_exists(df, "b", param_name="panel_col")


class TestValidateColumnsExist:
    """Test validate_columns_exist function."""

    def test_valid_columns(self):
        """Test that valid columns are returned."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
        result = validate_columns_exist(df, ["a", "b"])
        assert result == ["a", "b"]

    def test_all_columns_valid(self):
        """Test that all columns are validated."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        result = validate_columns_exist(df, ["a", "b"])
        assert result == ["a", "b"]

    def test_one_invalid_column(self):
        """Test that one invalid column raises ValueError."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with pytest.raises(ValueError, match="columns not found"):
            validate_columns_exist(df, ["a", "c"])

    def test_multiple_invalid_columns(self):
        """Test that multiple invalid columns are listed."""
        df = pd.DataFrame({"a": [1, 2]})
        with pytest.raises(ValueError, match="\\['b', 'c'\\]"):
            validate_columns_exist(df, ["b", "c"])

    def test_error_shows_available_columns(self):
        """Test that error includes available columns."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with pytest.raises(ValueError, match="Available columns: \\['a', 'b'\\]"):
            validate_columns_exist(df, ["c"])

    def test_empty_list(self):
        """Test that empty list is valid."""
        df = pd.DataFrame({"a": [1, 2]})
        result = validate_columns_exist(df, [])
        assert result == []


class TestValidatePositiveInteger:
    """Test validate_positive_integer function."""

    def test_valid_positive_integer(self):
        """Test that valid positive integer is returned."""
        result = validate_positive_integer(5, "width")
        assert result == 5

    def test_minimum_value_one(self):
        """Test that 1 is valid (default min_value)."""
        result = validate_positive_integer(1, "width")
        assert result == 1

    def test_zero_invalid_by_default(self):
        """Test that 0 raises ValueError by default."""
        with pytest.raises(ValueError, match="width must be >= 1"):
            validate_positive_integer(0, "width")

    def test_negative_invalid(self):
        """Test that negative integer raises ValueError."""
        with pytest.raises(ValueError, match="width must be >= 1"):
            validate_positive_integer(-5, "width")

    def test_custom_min_value(self):
        """Test that custom min_value is respected."""
        result = validate_positive_integer(10, "width", min_value=10)
        assert result == 10

        with pytest.raises(ValueError, match="width must be >= 10"):
            validate_positive_integer(9, "width", min_value=10)

    def test_min_value_zero(self):
        """Test that min_value=0 allows zero."""
        result = validate_positive_integer(0, "width", min_value=0)
        assert result == 0

    def test_none_not_allowed_by_default(self):
        """Test that None raises TypeError by default."""
        with pytest.raises(TypeError, match="width cannot be None"):
            validate_positive_integer(None, "width")

    def test_none_allowed(self):
        """Test that None is allowed when allow_none=True."""
        result = validate_positive_integer(None, "width", allow_none=True)
        assert result is None

    def test_float_raises_typeerror(self):
        """Test that float raises TypeError."""
        with pytest.raises(TypeError, match="width must be an integer"):
            validate_positive_integer(5.5, "width")

    def test_string_raises_typeerror(self):
        """Test that string raises TypeError."""
        with pytest.raises(TypeError, match="width must be an integer"):
            validate_positive_integer("5", "width")

    def test_bool_raises_typeerror(self):
        """Test that bool raises TypeError (bool is subclass of int)."""
        with pytest.raises(TypeError, match="width must be an integer"):
            validate_positive_integer(True, "width")


class TestValidateStringNonempty:
    """Test validate_string_nonempty function."""

    def test_valid_string(self):
        """Test that valid string is returned."""
        result = validate_string_nonempty("test", "name")
        assert result == "test"

    def test_string_with_whitespace_stripped(self):
        """Test that whitespace is stripped by default."""
        result = validate_string_nonempty("  test  ", "name")
        assert result == "test"

    def test_string_with_whitespace_not_stripped(self):
        """Test that whitespace is preserved when strip=False."""
        result = validate_string_nonempty("  test  ", "name", strip=False)
        assert result == "  test  "

    def test_empty_string_raises_valueerror(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            validate_string_nonempty("", "name")

    def test_whitespace_only_string_raises_valueerror(self):
        """Test that whitespace-only string raises ValueError after strip."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            validate_string_nonempty("   ", "name")

    def test_integer_raises_typeerror(self):
        """Test that integer raises TypeError."""
        with pytest.raises(TypeError, match="name must be a string"):
            validate_string_nonempty(123, "name")

    def test_none_raises_typeerror(self):
        """Test that None raises TypeError."""
        with pytest.raises(TypeError, match="name must be a string"):
            validate_string_nonempty(None, "name")


class TestValidateChoice:
    """Test validate_choice function."""

    def test_valid_choice_list(self):
        """Test that valid choice from list is returned."""
        result = validate_choice("row", ["row", "col"], "arrangement")
        assert result == "row"

    def test_valid_choice_set(self):
        """Test that valid choice from set is returned."""
        result = validate_choice("row", {"row", "col"}, "arrangement")
        assert result == "row"

    def test_valid_choice_tuple(self):
        """Test that valid choice from tuple is returned."""
        result = validate_choice("row", ("row", "col"), "arrangement")
        assert result == "row"

    def test_invalid_choice(self):
        """Test that invalid choice raises ValueError."""
        with pytest.raises(ValueError, match="arrangement must be one of"):
            validate_choice("invalid", ["row", "col"], "arrangement")

    def test_error_shows_choices(self):
        """Test that error message shows allowed choices."""
        with pytest.raises(ValueError, match="\\['col', 'row'\\]"):
            validate_choice("invalid", ["row", "col"], "arrangement")

    def test_case_sensitive_by_default(self):
        """Test that comparison is case-sensitive by default."""
        with pytest.raises(ValueError):
            validate_choice("ROW", ["row", "col"], "arrangement")

    def test_case_insensitive(self):
        """Test that case-insensitive comparison works."""
        result = validate_choice(
            "ROW", ["row", "col"], "arrangement", case_sensitive=False
        )
        assert result == "ROW"

    def test_numeric_choices(self):
        """Test that numeric choices work."""
        result = validate_choice(1, [1, 2, 3], "option")
        assert result == 1


class TestValidateNumericPositive:
    """Test validate_numeric_positive function."""

    def test_valid_integer(self):
        """Test that valid positive integer is returned."""
        result = validate_numeric_positive(5, "aspect")
        assert result == 5

    def test_valid_float(self):
        """Test that valid positive float is returned."""
        result = validate_numeric_positive(1.5, "aspect")
        assert result == 1.5

    def test_zero_not_allowed_by_default(self):
        """Test that zero raises ValueError by default."""
        with pytest.raises(ValueError, match="aspect must be > 0"):
            validate_numeric_positive(0, "aspect")

    def test_zero_allowed(self):
        """Test that zero is allowed when allow_zero=True."""
        result = validate_numeric_positive(0, "aspect", allow_zero=True)
        assert result == 0

    def test_negative_invalid(self):
        """Test that negative number raises ValueError."""
        with pytest.raises(ValueError, match="aspect must be > 0"):
            validate_numeric_positive(-1.5, "aspect")

    def test_negative_invalid_with_allow_zero(self):
        """Test that negative is still invalid with allow_zero=True."""
        with pytest.raises(ValueError, match="aspect must be >= 0"):
            validate_numeric_positive(-1, "aspect", allow_zero=True)

    def test_none_not_allowed_by_default(self):
        """Test that None raises TypeError by default."""
        with pytest.raises(TypeError, match="aspect cannot be None"):
            validate_numeric_positive(None, "aspect")

    def test_none_allowed(self):
        """Test that None is allowed when allow_none=True."""
        result = validate_numeric_positive(None, "aspect", allow_none=True)
        assert result is None

    def test_string_raises_typeerror(self):
        """Test that string raises TypeError."""
        with pytest.raises(TypeError, match="aspect must be numeric"):
            validate_numeric_positive("1.5", "aspect")

    def test_bool_raises_typeerror(self):
        """Test that bool raises TypeError."""
        with pytest.raises(TypeError, match="aspect must be numeric"):
            validate_numeric_positive(True, "aspect")


class TestValidateDataFrameNotEmpty:
    """Test validate_dataframe_not_empty function."""

    def test_valid_dataframe(self):
        """Test that non-empty DataFrame is returned."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = validate_dataframe_not_empty(df)
        assert result is df

    def test_empty_rows_raises_valueerror(self):
        """Test that DataFrame with 0 rows raises ValueError."""
        df = pd.DataFrame({"a": []})
        with pytest.raises(ValueError, match="data cannot be empty.*0 rows"):
            validate_dataframe_not_empty(df)

    def test_empty_columns_raises_valueerror(self):
        """Test that DataFrame with 0 columns raises ValueError."""
        df = pd.DataFrame()
        with pytest.raises(ValueError, match="must have at least one column"):
            validate_dataframe_not_empty(df)

    def test_custom_param_name(self):
        """Test that custom param_name appears in error."""
        df = pd.DataFrame()
        with pytest.raises(ValueError, match="my_data must have at least one column"):
            validate_dataframe_not_empty(df, param_name="my_data")


class TestValidateListOfStrings:
    """Test validate_list_of_strings function."""

    def test_valid_list(self):
        """Test that valid list of strings is returned."""
        result = validate_list_of_strings(["a", "b", "c"], "labels")
        assert result == ["a", "b", "c"]

    def test_empty_list_allowed_by_default(self):
        """Test that empty list is allowed by default."""
        result = validate_list_of_strings([], "labels")
        assert result == []

    def test_empty_list_not_allowed(self):
        """Test that empty list raises ValueError when allow_empty=False."""
        with pytest.raises(ValueError, match="labels cannot be empty"):
            validate_list_of_strings([], "labels", allow_empty=False)

    def test_single_element_list(self):
        """Test that single-element list is valid."""
        result = validate_list_of_strings(["a"], "labels")
        assert result == ["a"]

    def test_not_a_list_raises_typeerror(self):
        """Test that non-list raises TypeError."""
        with pytest.raises(TypeError, match="labels must be a list"):
            validate_list_of_strings("a", "labels")

        with pytest.raises(TypeError, match="labels must be a list"):
            validate_list_of_strings(("a", "b"), "labels")

    def test_list_with_non_string_raises_typeerror(self):
        """Test that list with non-string raises TypeError."""
        with pytest.raises(TypeError, match="labels\\[1\\] must be a string"):
            validate_list_of_strings(["a", 123, "c"], "labels")

    def test_error_shows_index(self):
        """Test that error message shows index of invalid element."""
        with pytest.raises(TypeError, match="labels\\[0\\] must be a string"):
            validate_list_of_strings([123, "b"], "labels")

    def test_list_with_none_raises_typeerror(self):
        """Test that list with None raises TypeError."""
        with pytest.raises(TypeError, match="labels\\[1\\] must be a string"):
            validate_list_of_strings(["a", None, "c"], "labels")
