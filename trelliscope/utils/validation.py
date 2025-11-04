"""
Validation utilities for input checking and error handling.

This module provides reusable validation functions for common input checks
throughout the trelliscope package. All functions raise descriptive errors
with actionable messages.
"""

from typing import Any, List, Optional, Union, Set
import pandas as pd


def validate_dataframe(data: Any, param_name: str = "data") -> pd.DataFrame:
    """
    Validate that input is a pandas DataFrame.

    Parameters
    ----------
    data : Any
        Input to validate.
    param_name : str, default="data"
        Parameter name for error messages.

    Returns
    -------
    pd.DataFrame
        The validated DataFrame.

    Raises
    ------
    TypeError
        If data is not a pandas DataFrame.

    Examples
    --------
    >>> df = pd.DataFrame({'a': [1, 2, 3]})
    >>> validate_dataframe(df)
    # Returns df

    >>> validate_dataframe([1, 2, 3])
    # Raises TypeError
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            f"{param_name} must be a pandas DataFrame, "
            f"got {type(data).__name__}"
        )
    return data


def validate_column_exists(
    data: pd.DataFrame,
    column: str,
    param_name: str = "column",
) -> str:
    """
    Validate that a column exists in DataFrame.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to check.
    column : str
        Column name to validate.
    param_name : str, default="column"
        Parameter name for error messages.

    Returns
    -------
    str
        The validated column name.

    Raises
    ------
    ValueError
        If column does not exist in DataFrame.

    Examples
    --------
    >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    >>> validate_column_exists(df, 'a')
    'a'

    >>> validate_column_exists(df, 'c')
    # Raises ValueError with available columns listed
    """
    if column not in data.columns:
        available = list(data.columns)
        raise ValueError(
            f"{param_name} '{column}' not found in DataFrame. "
            f"Available columns: {available}"
        )
    return column


def validate_columns_exist(
    data: pd.DataFrame,
    columns: List[str],
    param_name: str = "columns",
) -> List[str]:
    """
    Validate that multiple columns exist in DataFrame.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to check.
    columns : list of str
        Column names to validate.
    param_name : str, default="columns"
        Parameter name for error messages.

    Returns
    -------
    list of str
        The validated column names.

    Raises
    ------
    ValueError
        If any column does not exist in DataFrame.

    Examples
    --------
    >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
    >>> validate_columns_exist(df, ['a', 'b'])
    ['a', 'b']

    >>> validate_columns_exist(df, ['a', 'd'])
    # Raises ValueError listing missing columns
    """
    missing = [col for col in columns if col not in data.columns]
    if missing:
        available = list(data.columns)
        raise ValueError(
            f"{param_name} not found in DataFrame: {missing}. "
            f"Available columns: {available}"
        )
    return columns


def validate_positive_integer(
    value: Any,
    param_name: str,
    allow_none: bool = False,
    min_value: int = 1,
) -> Optional[int]:
    """
    Validate that value is a positive integer.

    Parameters
    ----------
    value : Any
        Value to validate.
    param_name : str
        Parameter name for error messages.
    allow_none : bool, default=False
        Whether None is allowed.
    min_value : int, default=1
        Minimum allowed value (inclusive).

    Returns
    -------
    int or None
        The validated integer, or None if allowed and value is None.

    Raises
    ------
    TypeError
        If value is not an integer (and not None if allowed).
    ValueError
        If value is less than min_value.

    Examples
    --------
    >>> validate_positive_integer(5, "width")
    5

    >>> validate_positive_integer(0, "width")
    # Raises ValueError

    >>> validate_positive_integer(None, "width", allow_none=True)
    None
    """
    if value is None:
        if allow_none:
            return None
        raise TypeError(f"{param_name} cannot be None")

    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(
            f"{param_name} must be an integer, got {type(value).__name__}"
        )

    if value < min_value:
        raise ValueError(
            f"{param_name} must be >= {min_value}, got {value}"
        )

    return value


def validate_string_nonempty(
    value: Any,
    param_name: str,
    strip: bool = True,
) -> str:
    """
    Validate that value is a non-empty string.

    Parameters
    ----------
    value : Any
        Value to validate.
    param_name : str
        Parameter name for error messages.
    strip : bool, default=True
        Whether to strip whitespace before checking.

    Returns
    -------
    str
        The validated string (stripped if strip=True).

    Raises
    ------
    TypeError
        If value is not a string.
    ValueError
        If value is empty after optional stripping.

    Examples
    --------
    >>> validate_string_nonempty("test", "name")
    'test'

    >>> validate_string_nonempty("  test  ", "name", strip=True)
    'test'

    >>> validate_string_nonempty("", "name")
    # Raises ValueError

    >>> validate_string_nonempty(123, "name")
    # Raises TypeError
    """
    if not isinstance(value, str):
        raise TypeError(
            f"{param_name} must be a string, got {type(value).__name__}"
        )

    if strip:
        value = value.strip()

    if not value:
        raise ValueError(f"{param_name} cannot be empty")

    return value


def validate_choice(
    value: Any,
    choices: Union[List, Set, tuple],
    param_name: str,
    case_sensitive: bool = True,
) -> Any:
    """
    Validate that value is one of allowed choices.

    Parameters
    ----------
    value : Any
        Value to validate.
    choices : list, set, or tuple
        Allowed values.
    param_name : str
        Parameter name for error messages.
    case_sensitive : bool, default=True
        Whether string comparison is case-sensitive.

    Returns
    -------
    Any
        The validated value.

    Raises
    ------
    ValueError
        If value is not in choices.

    Examples
    --------
    >>> validate_choice("row", ["row", "col"], "arrangement")
    'row'

    >>> validate_choice("ROW", ["row", "col"], "arrangement", case_sensitive=False)
    'ROW'

    >>> validate_choice("invalid", ["row", "col"], "arrangement")
    # Raises ValueError with allowed choices listed
    """
    # Convert to set for efficient lookup
    choices_set = set(choices)

    # Handle case-insensitive string comparison
    if not case_sensitive and isinstance(value, str):
        choices_lower = {str(c).lower() for c in choices_set}
        if value.lower() not in choices_lower:
            raise ValueError(
                f"{param_name} must be one of {sorted(choices_set)}, "
                f"got '{value}'"
            )
    else:
        if value not in choices_set:
            raise ValueError(
                f"{param_name} must be one of {sorted(choices_set)}, "
                f"got '{value}'"
            )

    return value


def validate_numeric_positive(
    value: Any,
    param_name: str,
    allow_none: bool = False,
    allow_zero: bool = False,
) -> Optional[Union[int, float]]:
    """
    Validate that value is a positive number (int or float).

    Parameters
    ----------
    value : Any
        Value to validate.
    param_name : str
        Parameter name for error messages.
    allow_none : bool, default=False
        Whether None is allowed.
    allow_zero : bool, default=False
        Whether zero is allowed.

    Returns
    -------
    int, float, or None
        The validated number, or None if allowed and value is None.

    Raises
    ------
    TypeError
        If value is not numeric (and not None if allowed).
    ValueError
        If value is not positive (or non-negative if allow_zero=True).

    Examples
    --------
    >>> validate_numeric_positive(5.5, "aspect")
    5.5

    >>> validate_numeric_positive(0, "aspect", allow_zero=True)
    0

    >>> validate_numeric_positive(-1, "aspect")
    # Raises ValueError

    >>> validate_numeric_positive(None, "aspect", allow_none=True)
    None
    """
    if value is None:
        if allow_none:
            return None
        raise TypeError(f"{param_name} cannot be None")

    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(
            f"{param_name} must be numeric (int or float), "
            f"got {type(value).__name__}"
        )

    min_value = 0 if allow_zero else 0
    comparison = ">=" if allow_zero else ">"

    if allow_zero and value < 0:
        raise ValueError(
            f"{param_name} must be >= 0, got {value}"
        )
    elif not allow_zero and value <= 0:
        raise ValueError(
            f"{param_name} must be > 0, got {value}"
        )

    return value


def validate_dataframe_not_empty(
    data: pd.DataFrame,
    param_name: str = "data",
) -> pd.DataFrame:
    """
    Validate that DataFrame is not empty.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to validate.
    param_name : str, default="data"
        Parameter name for error messages.

    Returns
    -------
    pd.DataFrame
        The validated DataFrame.

    Raises
    ------
    ValueError
        If DataFrame has no rows or no columns.

    Examples
    --------
    >>> df = pd.DataFrame({'a': [1, 2, 3]})
    >>> validate_dataframe_not_empty(df)
    # Returns df

    >>> empty_df = pd.DataFrame()
    >>> validate_dataframe_not_empty(empty_df)
    # Raises ValueError
    """
    # Check columns first (more fundamental requirement)
    if len(data.columns) == 0:
        raise ValueError(
            f"{param_name} must have at least one column "
            f"(has {len(data.columns)} columns)"
        )

    if len(data) == 0:
        raise ValueError(
            f"{param_name} cannot be empty (has {len(data)} rows)"
        )

    return data


def validate_list_of_strings(
    value: Any,
    param_name: str,
    allow_empty: bool = True,
) -> List[str]:
    """
    Validate that value is a list of strings.

    Parameters
    ----------
    value : Any
        Value to validate.
    param_name : str
        Parameter name for error messages.
    allow_empty : bool, default=True
        Whether empty list is allowed.

    Returns
    -------
    list of str
        The validated list.

    Raises
    ------
    TypeError
        If value is not a list or contains non-strings.
    ValueError
        If list is empty and allow_empty=False.

    Examples
    --------
    >>> validate_list_of_strings(["a", "b"], "labels")
    ['a', 'b']

    >>> validate_list_of_strings([], "labels", allow_empty=False)
    # Raises ValueError

    >>> validate_list_of_strings(["a", 1], "labels")
    # Raises TypeError
    """
    if not isinstance(value, list):
        raise TypeError(
            f"{param_name} must be a list, got {type(value).__name__}"
        )

    if not allow_empty and len(value) == 0:
        raise ValueError(f"{param_name} cannot be empty")

    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise TypeError(
                f"{param_name}[{i}] must be a string, "
                f"got {type(item).__name__}"
            )

    return value
