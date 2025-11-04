"""
Meta variable type inference from pandas Series.

This module provides automatic type detection to create appropriate
MetaVariable instances from pandas Series based on their dtype and values.
"""

from typing import Optional
import pandas as pd
import numpy as np

from trelliscope.meta import (
    MetaVariable,
    FactorMeta,
    NumberMeta,
    DateMeta,
    TimeMeta,
)


def infer_meta_from_series(
    series: pd.Series,
    varname: Optional[str] = None,
    **kwargs
) -> MetaVariable:
    """
    Automatically infer and create appropriate MetaVariable from pandas Series.

    Inference rules:
    - datetime64[ns] without time component → DateMeta
    - datetime64[ns] with timezone OR time values → TimeMeta
    - Numeric dtypes (int, float) → NumberMeta
    - Categorical, object, string → FactorMeta
    - Boolean → FactorMeta with levels ["False", "True"]

    Parameters
    ----------
    series : pd.Series
        Data series to infer type from.
    varname : str, optional
        Variable name. Uses series.name if not provided.
    **kwargs
        Additional parameters passed to specific meta type constructor.

    Returns
    -------
    MetaVariable
        Appropriate meta variable instance based on inferred type.

    Raises
    ------
    ValueError
        If series is empty or varname cannot be determined.

    Examples
    --------
    >>> import pandas as pd
    >>> from trelliscope.inference import infer_meta_from_series

    >>> # Numeric series → NumberMeta
    >>> series = pd.Series([1.5, 2.7, 3.9], name="values")
    >>> meta = infer_meta_from_series(series)
    >>> meta.type
    'number'

    >>> # Categorical series → FactorMeta
    >>> series = pd.Series(["A", "B", "C"], name="category")
    >>> meta = infer_meta_from_series(series)
    >>> meta.type
    'factor'

    >>> # Datetime series → DateMeta or TimeMeta
    >>> series = pd.Series(pd.date_range("2024-01-01", periods=3), name="dates")
    >>> meta = infer_meta_from_series(series)
    >>> meta.type
    'date'
    """
    # Determine varname
    if varname is None:
        if series.name is None:
            raise ValueError(
                "varname must be provided when series.name is None"
            )
        varname = str(series.name)

    # Handle empty series - default to FactorMeta
    if len(series) == 0:
        return FactorMeta(varname=varname, levels=[], **kwargs)

    # Get dtype
    dtype = series.dtype

    # Boolean → FactorMeta
    if dtype == bool or pd.api.types.is_bool_dtype(dtype):
        if "levels" not in kwargs:
            kwargs["levels"] = ["False", "True"]
        return FactorMeta(varname=varname, **kwargs)

    # Datetime types → DateMeta or TimeMeta
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return _infer_datetime_meta(series, varname, **kwargs)

    # Numeric types → NumberMeta
    if pd.api.types.is_numeric_dtype(dtype):
        return NumberMeta.from_series(series, varname=varname, **kwargs)

    # Categorical, object, string → FactorMeta
    if (isinstance(dtype, pd.CategoricalDtype) or
        pd.api.types.is_object_dtype(dtype) or
        pd.api.types.is_string_dtype(dtype)):
        return FactorMeta.from_series(series, varname=varname, **kwargs)

    # Fallback to FactorMeta for unknown types
    return FactorMeta.from_series(series, varname=varname, **kwargs)


def _infer_datetime_meta(
    series: pd.Series,
    varname: str,
    **kwargs
) -> MetaVariable:
    """
    Infer whether datetime series should be DateMeta or TimeMeta.

    Logic:
    - If series has timezone info → TimeMeta
    - If series has time component (non-midnight times) → TimeMeta
    - Otherwise → DateMeta

    Parameters
    ----------
    series : pd.Series
        Datetime series.
    varname : str
        Variable name.
    **kwargs
        Additional parameters.

    Returns
    -------
    DateMeta or TimeMeta
        Appropriate meta type for datetime data.
    """
    # Check if timezone-aware
    if hasattr(series.dtype, "tz") and series.dtype.tz is not None:
        return TimeMeta.from_series(series, varname=varname, **kwargs)

    # Check if any non-NaT values have time component (non-midnight)
    # by checking if any times are not exactly on day boundaries
    non_nat = series.dropna()
    if len(non_nat) > 0:
        # Convert to datetime if needed and check for time component
        try:
            # Check if any values have hour/minute/second components
            has_time = (
                (non_nat.dt.hour != 0).any() or
                (non_nat.dt.minute != 0).any() or
                (non_nat.dt.second != 0).any() or
                (non_nat.dt.microsecond != 0).any()
            )
            if has_time:
                return TimeMeta.from_series(series, varname=varname, **kwargs)
        except (AttributeError, TypeError):
            # If datetime accessor fails, fall back to DateMeta
            pass

    # Default to DateMeta for date-only data
    return DateMeta.from_series(series, varname=varname, **kwargs)


def infer_meta_dict(
    df: pd.DataFrame,
    columns: Optional[list] = None,
) -> dict:
    """
    Infer meta variables for multiple DataFrame columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to infer from.
    columns : list of str, optional
        Columns to infer. Defaults to all columns.

    Returns
    -------
    dict
        Dictionary mapping column names to MetaVariable instances.

    Examples
    --------
    >>> import pandas as pd
    >>> from trelliscope.inference import infer_meta_dict

    >>> df = pd.DataFrame({
    ...     'id': [1, 2, 3],
    ...     'category': ['A', 'B', 'C'],
    ...     'value': [1.5, 2.7, 3.9]
    ... })
    >>> metas = infer_meta_dict(df)
    >>> list(metas.keys())
    ['id', 'category', 'value']
    >>> metas['value'].type
    'number'
    """
    if columns is None:
        columns = list(df.columns)

    return {
        col: infer_meta_from_series(df[col], varname=col)
        for col in columns
    }
