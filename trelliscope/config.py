"""Viewer configuration for trelliscope displays."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class ViewerConfig:
    """Configuration for trelliscope viewer appearance and behavior.

    Allows customization of viewer theme, initial state, and display options.

    Parameters
    ----------
    theme : str, optional
        Viewer theme. Options: "light", "dark", "auto". Default: "light"
    show_info : bool, default=True
        Show info panel with display description and metadata summary
    show_labels : bool, default=True
        Show labels on panels
    show_panel_count : bool, default=True
        Show panel count in viewer
    panel_aspect : float, optional
        Force specific aspect ratio for panels (width/height)
    initial_sort : list of dict, optional
        Initial sort configuration. Each dict has keys:
        - "var": variable name to sort by
        - "dir": direction ("asc" or "desc")
    initial_filter : list of dict, optional
        Initial filter configuration
    custom_css : str, optional
        Custom CSS to inject into viewer
    config_options : dict, optional
        Additional viewer configuration options

    Examples
    --------
    >>> from trelliscope.config import ViewerConfig
    >>>
    >>> # Basic theme configuration
    >>> config = ViewerConfig(theme="dark")
    >>>
    >>> # With initial sort and filters
    >>> config = ViewerConfig(
    ...     theme="light",
    ...     initial_sort=[{"var": "value", "dir": "desc"}],
    ...     show_info=True
    ... )
    >>>
    >>> # Custom configuration
    >>> config = ViewerConfig(
    ...     theme="auto",
    ...     panel_aspect=1.5,
    ...     custom_css=".panel { border: 2px solid blue; }"
    ... )
    """

    theme: str = "light"
    show_info: bool = True
    show_labels: bool = True
    show_panel_count: bool = True
    panel_aspect: Optional[float] = None
    initial_sort: Optional[List[Dict[str, str]]] = None
    initial_filter: Optional[List[Dict[str, Any]]] = None
    custom_css: Optional[str] = None
    config_options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate theme
        valid_themes = ["light", "dark", "auto"]
        if self.theme not in valid_themes:
            raise ValueError(
                f"Invalid theme: {self.theme}. "
                f"Must be one of {valid_themes}"
            )

        # Validate panel_aspect
        if self.panel_aspect is not None:
            if not isinstance(self.panel_aspect, (int, float)):
                raise TypeError("panel_aspect must be a number")
            if self.panel_aspect <= 0:
                raise ValueError("panel_aspect must be positive")

        # Validate initial_sort
        if self.initial_sort is not None:
            if not isinstance(self.initial_sort, list):
                raise TypeError("initial_sort must be a list")
            for sort_item in self.initial_sort:
                if not isinstance(sort_item, dict):
                    raise TypeError("Each sort item must be a dict")
                if "var" not in sort_item:
                    raise ValueError("Sort item must have 'var' key")
                if "dir" in sort_item and sort_item["dir"] not in ["asc", "desc"]:
                    raise ValueError("Sort direction must be 'asc' or 'desc'")

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for JSON serialization.

        Returns
        -------
        dict
            Configuration as dictionary

        Examples
        --------
        >>> config = ViewerConfig(theme="dark", show_info=False)
        >>> config.to_dict()
        {'theme': 'dark', 'show_info': False, ...}
        """
        config_dict = asdict(self)

        # Remove None values
        config_dict = {k: v for k, v in config_dict.items() if v is not None}

        # Merge config_options into top level
        if "config_options" in config_dict:
            options = config_dict.pop("config_options")
            config_dict.update(options)

        return config_dict

    @classmethod
    def dark_theme(cls) -> "ViewerConfig":
        """Create config with dark theme preset.

        Returns
        -------
        ViewerConfig
            Configuration with dark theme

        Examples
        --------
        >>> config = ViewerConfig.dark_theme()
        >>> config.theme
        'dark'
        """
        return cls(theme="dark")

    @classmethod
    def light_theme(cls) -> "ViewerConfig":
        """Create config with light theme preset.

        Returns
        -------
        ViewerConfig
            Configuration with light theme

        Examples
        --------
        >>> config = ViewerConfig.light_theme()
        >>> config.theme
        'light'
        """
        return cls(theme="light")

    @classmethod
    def minimal(cls) -> "ViewerConfig":
        """Create minimalist config (no info panel, no labels).

        Returns
        -------
        ViewerConfig
            Minimal configuration

        Examples
        --------
        >>> config = ViewerConfig.minimal()
        >>> config.show_info
        False
        """
        return cls(
            theme="light",
            show_info=False,
            show_labels=False,
            show_panel_count=False,
        )

    def with_sort(self, var: str, direction: str = "asc") -> "ViewerConfig":
        """Add initial sort to configuration.

        Parameters
        ----------
        var : str
            Variable name to sort by
        direction : str, default="asc"
            Sort direction: "asc" or "desc"

        Returns
        -------
        ViewerConfig
            Updated configuration (returns self for chaining)

        Examples
        --------
        >>> config = ViewerConfig().with_sort("value", "desc")
        >>> config.initial_sort
        [{'var': 'value', 'dir': 'desc'}]
        """
        if direction not in ["asc", "desc"]:
            raise ValueError("direction must be 'asc' or 'desc'")

        if self.initial_sort is None:
            self.initial_sort = []

        self.initial_sort.append({"var": var, "dir": direction})
        return self

    def with_css(self, css: str) -> "ViewerConfig":
        """Add custom CSS to configuration.

        Parameters
        ----------
        css : str
            CSS code to inject

        Returns
        -------
        ViewerConfig
            Updated configuration (returns self for chaining)

        Examples
        --------
        >>> config = ViewerConfig().with_css(".panel { border: 2px solid red; }")
        """
        self.custom_css = css
        return self

    def with_option(self, key: str, value: Any) -> "ViewerConfig":
        """Add custom configuration option.

        Parameters
        ----------
        key : str
            Option key
        value : Any
            Option value

        Returns
        -------
        ViewerConfig
            Updated configuration (returns self for chaining)

        Examples
        --------
        >>> config = ViewerConfig().with_option("debug", True)
        """
        self.config_options[key] = value
        return self


def merge_configs(
    base_config: Optional[ViewerConfig],
    override_config: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Merge ViewerConfig with override dictionary.

    Parameters
    ----------
    base_config : ViewerConfig, optional
        Base configuration object
    override_config : dict, optional
        Override values as dictionary

    Returns
    -------
    dict
        Merged configuration

    Examples
    --------
    >>> base = ViewerConfig(theme="dark")
    >>> overrides = {"show_info": False}
    >>> merged = merge_configs(base, overrides)
    >>> merged
    {'theme': 'dark', 'show_info': False, ...}
    """
    result = {}

    # Start with base config
    if base_config is not None:
        result = base_config.to_dict()

    # Apply overrides
    if override_config is not None:
        result.update(override_config)

    return result
