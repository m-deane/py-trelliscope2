"""
Meta variable classes for trelliscope cognostics.

Meta variables (cognostics) provide metadata about each panel that enables
filtering, sorting, and labeling in the viewer. This module defines the type
hierarchy for different meta variable types.
"""

from typing import Optional, List, Any, Dict
import attrs
import pandas as pd


@attrs.define
class MetaVariable:
    """
    Base class for meta variables (cognostics).

    Meta variables describe panel metadata and enable interactive filtering
    and sorting in the trelliscope viewer.

    Parameters
    ----------
    varname : str
        Column name in DataFrame.
    label : str, optional
        Display label for viewer. Defaults to varname if not provided.
    desc : str, optional
        Description for tooltip in viewer.
    type : str
        Meta variable type identifier.

    Attributes
    ----------
    varname : str
        Column name.
    label : str
        Display label.
    desc : str
        Description.
    type : str
        Type identifier.
    """

    varname: str
    label: Optional[str] = None
    desc: Optional[str] = None
    type: str = attrs.field(init=False, default="")

    def __attrs_post_init__(self):
        """Set label to varname if not provided."""
        if self.label is None:
            self.label = self.varname

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert meta variable to JSON-serializable dictionary.

        Returns
        -------
        dict
            Dictionary representation matching displayInfo.json schema.

        Examples
        --------
        >>> meta = FactorMeta("category", levels=["A", "B", "C"])
        >>> meta.to_dict()
        {'varname': 'category', 'label': 'category', 'type': 'factor', ...}
        """
        result = {
            "varname": self.varname,
            "label": self.label,
            "type": self.type,
        }

        # Add description only if provided
        if self.desc:
            result["desc"] = self.desc

        return result

    @classmethod
    def from_series(
        cls,
        series: pd.Series,
        varname: Optional[str] = None,
        **kwargs
    ) -> "MetaVariable":
        """
        Create meta variable from pandas Series with type inference.

        Parameters
        ----------
        series : pd.Series
            Data series to infer from.
        varname : str, optional
            Column name. Uses series.name if not provided.
        **kwargs
            Additional parameters for specific meta type.

        Returns
        -------
        MetaVariable
            Inferred meta variable instance.

        Raises
        ------
        ValueError
            If varname cannot be determined from series.name or parameter.
        """
        if varname is None:
            if series.name is None:
                raise ValueError(
                    "varname must be provided when series.name is None"
                )
            varname = str(series.name)

        # This is overridden in subclasses for type-specific inference
        return cls(varname=varname, **kwargs)


@attrs.define
class FactorMeta(MetaVariable):
    """
    Categorical meta variable with defined levels.

    Parameters
    ----------
    varname : str
        Column name.
    levels : list of str, optional
        Unique category values. Inferred from data if not provided.
    label : str, optional
        Display label.
    desc : str, optional
        Description.

    Attributes
    ----------
    type : str
        Always "factor".
    levels : list of str or None
        Category levels.
    """

    levels: Optional[List[str]] = None
    type: str = attrs.field(init=False, default="factor")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with levels."""
        result = super().to_dict()
        if self.levels is not None:
            result["levels"] = self.levels
        return result

    @classmethod
    def from_series(
        cls,
        series: pd.Series,
        varname: Optional[str] = None,
        **kwargs
    ) -> "FactorMeta":
        """
        Create FactorMeta from series, inferring levels.

        Parameters
        ----------
        series : pd.Series
            Categorical or object series.
        varname : str, optional
            Column name.
        **kwargs
            Additional parameters.

        Returns
        -------
        FactorMeta
            Meta variable with inferred levels.
        """
        if varname is None:
            varname = str(series.name)

        # Infer levels from unique values (excluding NaN)
        if "levels" not in kwargs:
            unique_vals = series.dropna().unique()
            kwargs["levels"] = sorted([str(v) for v in unique_vals])

        return cls(varname=varname, **kwargs)


@attrs.define
class NumberMeta(MetaVariable):
    """
    Numeric continuous meta variable.

    Parameters
    ----------
    varname : str
        Column name.
    digits : int, default=2
        Number of decimal places for display.
    locale : bool, default=False
        Use locale-specific number formatting.
    log : bool, default=False
        Display on logarithmic scale.
    label : str, optional
        Display label.
    desc : str, optional
        Description.

    Attributes
    ----------
    type : str
        Always "number".
    """

    digits: int = 2
    locale: bool = False
    log: bool = False
    type: str = attrs.field(init=False, default="number")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with numeric options."""
        result = super().to_dict()
        result["digits"] = self.digits
        result["locale"] = self.locale
        result["log"] = self.log
        return result

    @classmethod
    def from_series(
        cls,
        series: pd.Series,
        varname: Optional[str] = None,
        **kwargs
    ) -> "NumberMeta":
        """
        Create NumberMeta from numeric series.

        Parameters
        ----------
        series : pd.Series
            Numeric series.
        varname : str, optional
            Column name.
        **kwargs
            Additional parameters.

        Returns
        -------
        NumberMeta
            Meta variable for numeric data.
        """
        if varname is None:
            varname = str(series.name)

        return cls(varname=varname, **kwargs)


@attrs.define
class DateMeta(MetaVariable):
    """
    Date meta variable (no time component).

    Parameters
    ----------
    varname : str
        Column name.
    format : str, optional
        Date format string (e.g., "%Y-%m-%d").
    label : str, optional
        Display label.
    desc : str, optional
        Description.

    Attributes
    ----------
    type : str
        Always "date".
    """

    format: Optional[str] = None
    type: str = attrs.field(init=False, default="date")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with date format."""
        result = super().to_dict()
        if self.format:
            result["format"] = self.format
        return result

    @classmethod
    def from_series(
        cls,
        series: pd.Series,
        varname: Optional[str] = None,
        **kwargs
    ) -> "DateMeta":
        """
        Create DateMeta from datetime series.

        Parameters
        ----------
        series : pd.Series
            Datetime series.
        varname : str, optional
            Column name.
        **kwargs
            Additional parameters.

        Returns
        -------
        DateMeta
            Meta variable for date data.
        """
        if varname is None:
            varname = str(series.name)

        return cls(varname=varname, **kwargs)


@attrs.define
class TimeMeta(MetaVariable):
    """
    Datetime meta variable with time component.

    Parameters
    ----------
    varname : str
        Column name.
    timezone : str, optional
        Timezone identifier (e.g., "UTC", "America/New_York").
    format : str, optional
        Datetime format string.
    label : str, optional
        Display label.
    desc : str, optional
        Description.

    Attributes
    ----------
    type : str
        Always "time".
    """

    timezone: Optional[str] = None
    format: Optional[str] = None
    type: str = attrs.field(init=False, default="time")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with time options."""
        result = super().to_dict()
        if self.timezone:
            result["timezone"] = self.timezone
        if self.format:
            result["format"] = self.format
        return result

    @classmethod
    def from_series(
        cls,
        series: pd.Series,
        varname: Optional[str] = None,
        **kwargs
    ) -> "TimeMeta":
        """
        Create TimeMeta from datetime series.

        Parameters
        ----------
        series : pd.Series
            Datetime series.
        varname : str, optional
            Column name.
        **kwargs
            Additional parameters.

        Returns
        -------
        TimeMeta
            Meta variable for datetime data.
        """
        if varname is None:
            varname = str(series.name)

        # Infer timezone from series if available
        if "timezone" not in kwargs and hasattr(series.dtype, "tz"):
            tz = series.dtype.tz
            if tz is not None:
                kwargs["timezone"] = str(tz)

        return cls(varname=varname, **kwargs)


@attrs.define
class CurrencyMeta(MetaVariable):
    """
    Currency/monetary meta variable.

    Parameters
    ----------
    varname : str
        Column name.
    code : str, default="USD"
        Currency code (ISO 4217, e.g., "USD", "EUR", "GBP").
    digits : int, default=2
        Number of decimal places.
    locale : bool, default=True
        Use locale-specific currency formatting.
    label : str, optional
        Display label.
    desc : str, optional
        Description.

    Attributes
    ----------
    type : str
        Always "currency".
    """

    code: str = "USD"
    digits: int = 2
    locale: bool = True
    type: str = attrs.field(init=False, default="currency")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with currency options."""
        result = super().to_dict()
        result["code"] = self.code
        result["digits"] = self.digits
        result["locale"] = self.locale
        return result


@attrs.define
class HrefMeta(MetaVariable):
    """
    Hyperlink meta variable.

    Parameters
    ----------
    varname : str
        Column name containing URLs.
    label_col : str, optional
        Column name containing link text. If not provided, URL is displayed.
    label : str, optional
        Display label for the meta variable itself.
    desc : str, optional
        Description.

    Attributes
    ----------
    type : str
        Always "href".
    """

    label_col: Optional[str] = None
    type: str = attrs.field(init=False, default="href")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with href options."""
        result = super().to_dict()
        if self.label_col:
            result["label_col"] = self.label_col
        return result


@attrs.define
class GraphMeta(MetaVariable):
    """
    Sparkline/micro-visualization meta variable.

    Parameters
    ----------
    varname : str
        Column name containing graph data.
    direction : str, optional
        Trend direction: "up", "down", or "neutral".
    idvarname : str, optional
        ID variable name for linking.
    label : str, optional
        Display label.
    desc : str, optional
        Description.

    Attributes
    ----------
    type : str
        Always "graph".
    """

    direction: Optional[str] = None
    idvarname: Optional[str] = None
    type: str = attrs.field(init=False, default="graph")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with graph options."""
        result = super().to_dict()
        if self.direction:
            result["direction"] = self.direction
        if self.idvarname:
            result["idvarname"] = self.idvarname
        return result


@attrs.define
class StringMeta(MetaVariable):
    """
    String/text meta variable for categorical text data.

    Parameters
    ----------
    varname : str
        Column name.
    label : str, optional
        Display label.
    desc : str, optional
        Description.

    Attributes
    ----------
    type : str
        Always "string".
    """

    type: str = attrs.field(init=False, default="string")

    @classmethod
    def from_series(
        cls,
        series: pd.Series,
        varname: Optional[str] = None,
        **kwargs
    ) -> "StringMeta":
        """
        Create StringMeta from string series.

        Parameters
        ----------
        series : pd.Series
            String/object series.
        varname : str, optional
            Column name.
        **kwargs
            Additional parameters.

        Returns
        -------
        StringMeta
            Meta variable for string data.
        """
        if varname is None:
            varname = str(series.name)

        return cls(varname=varname, **kwargs)
