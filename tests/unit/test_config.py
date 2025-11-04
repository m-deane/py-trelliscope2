"""Unit tests for viewer configuration."""

import pytest
from trelliscope.config import ViewerConfig, merge_configs


class TestViewerConfigInit:
    """Test ViewerConfig initialization and defaults."""

    def test_default_initialization(self):
        """Test default configuration values."""
        config = ViewerConfig()

        assert config.theme == "light"
        assert config.show_info is True
        assert config.show_labels is True
        assert config.show_panel_count is True
        assert config.panel_aspect is None
        assert config.initial_sort is None
        assert config.initial_filter is None
        assert config.custom_css is None
        assert config.config_options == {}

    def test_custom_initialization(self):
        """Test initialization with custom values."""
        config = ViewerConfig(
            theme="dark",
            show_info=False,
            panel_aspect=1.5,
            custom_css=".panel { border: 1px solid red; }"
        )

        assert config.theme == "dark"
        assert config.show_info is False
        assert config.panel_aspect == 1.5
        assert config.custom_css == ".panel { border: 1px solid red; }"

    def test_invalid_theme_raises_error(self):
        """Test invalid theme value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid theme"):
            ViewerConfig(theme="invalid")

    def test_valid_themes(self):
        """Test all valid theme values."""
        for theme in ["light", "dark", "auto"]:
            config = ViewerConfig(theme=theme)
            assert config.theme == theme

    def test_invalid_panel_aspect_type_raises_error(self):
        """Test invalid panel_aspect type raises TypeError."""
        with pytest.raises(TypeError, match="panel_aspect must be a number"):
            ViewerConfig(panel_aspect="invalid")

    def test_negative_panel_aspect_raises_error(self):
        """Test negative panel_aspect raises ValueError."""
        with pytest.raises(ValueError, match="panel_aspect must be positive"):
            ViewerConfig(panel_aspect=-1.0)

    def test_zero_panel_aspect_raises_error(self):
        """Test zero panel_aspect raises ValueError."""
        with pytest.raises(ValueError, match="panel_aspect must be positive"):
            ViewerConfig(panel_aspect=0)

    def test_valid_panel_aspect(self):
        """Test valid panel_aspect values."""
        config = ViewerConfig(panel_aspect=1.5)
        assert config.panel_aspect == 1.5

        config = ViewerConfig(panel_aspect=2)
        assert config.panel_aspect == 2


class TestViewerConfigSort:
    """Test initial_sort validation and methods."""

    def test_valid_initial_sort(self):
        """Test valid initial_sort configuration."""
        sort_config = [
            {"var": "value", "dir": "asc"},
            {"var": "name", "dir": "desc"}
        ]
        config = ViewerConfig(initial_sort=sort_config)

        assert config.initial_sort == sort_config

    def test_sort_without_dir_key(self):
        """Test sort config without 'dir' key is valid."""
        sort_config = [{"var": "value"}]
        config = ViewerConfig(initial_sort=sort_config)

        assert config.initial_sort == sort_config

    def test_sort_missing_var_raises_error(self):
        """Test sort config without 'var' key raises ValueError."""
        with pytest.raises(ValueError, match="must have 'var' key"):
            ViewerConfig(initial_sort=[{"dir": "asc"}])

    def test_invalid_sort_direction_raises_error(self):
        """Test invalid sort direction raises ValueError."""
        with pytest.raises(ValueError, match="must be 'asc' or 'desc'"):
            ViewerConfig(initial_sort=[{"var": "value", "dir": "invalid"}])

    def test_initial_sort_not_list_raises_error(self):
        """Test initial_sort not a list raises TypeError."""
        with pytest.raises(TypeError, match="initial_sort must be a list"):
            ViewerConfig(initial_sort={"var": "value"})

    def test_sort_item_not_dict_raises_error(self):
        """Test sort item not a dict raises TypeError."""
        with pytest.raises(TypeError, match="Each sort item must be a dict"):
            ViewerConfig(initial_sort=["value"])

    def test_with_sort_method(self):
        """Test with_sort method adds sort configuration."""
        config = ViewerConfig().with_sort("value", "desc")

        assert config.initial_sort == [{"var": "value", "dir": "desc"}]

    def test_with_sort_multiple_times(self):
        """Test with_sort can be called multiple times."""
        config = (ViewerConfig()
                  .with_sort("value", "desc")
                  .with_sort("name", "asc"))

        assert config.initial_sort == [
            {"var": "value", "dir": "desc"},
            {"var": "name", "dir": "asc"}
        ]

    def test_with_sort_default_direction(self):
        """Test with_sort defaults to ascending."""
        config = ViewerConfig().with_sort("value")

        assert config.initial_sort == [{"var": "value", "dir": "asc"}]

    def test_with_sort_invalid_direction_raises_error(self):
        """Test with_sort with invalid direction raises ValueError."""
        config = ViewerConfig()

        with pytest.raises(ValueError, match="must be 'asc' or 'desc'"):
            config.with_sort("value", "invalid")


class TestViewerConfigToDict:
    """Test to_dict method."""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        config = ViewerConfig(theme="dark", show_info=False)
        result = config.to_dict()

        assert result["theme"] == "dark"
        assert result["show_info"] is False
        assert result["show_labels"] is True  # default
        assert result["show_panel_count"] is True  # default

    def test_to_dict_excludes_none_values(self):
        """Test to_dict excludes None values."""
        config = ViewerConfig()
        result = config.to_dict()

        assert "panel_aspect" not in result
        assert "initial_sort" not in result
        assert "initial_filter" not in result
        assert "custom_css" not in result

    def test_to_dict_includes_non_none_optional_values(self):
        """Test to_dict includes non-None optional values."""
        config = ViewerConfig(
            panel_aspect=1.5,
            initial_sort=[{"var": "value", "dir": "asc"}],
            custom_css=".panel { color: red; }"
        )
        result = config.to_dict()

        assert result["panel_aspect"] == 1.5
        assert result["initial_sort"] == [{"var": "value", "dir": "asc"}]
        assert result["custom_css"] == ".panel { color: red; }"

    def test_to_dict_merges_config_options(self):
        """Test to_dict merges config_options into top level."""
        config = ViewerConfig(
            theme="dark",
            config_options={"debug": True, "custom_option": "value"}
        )
        result = config.to_dict()

        assert result["theme"] == "dark"
        assert result["debug"] is True
        assert result["custom_option"] == "value"
        assert "config_options" not in result


class TestViewerConfigPresets:
    """Test preset configuration methods."""

    def test_dark_theme_preset(self):
        """Test dark_theme preset."""
        config = ViewerConfig.dark_theme()

        assert config.theme == "dark"
        assert isinstance(config, ViewerConfig)

    def test_light_theme_preset(self):
        """Test light_theme preset."""
        config = ViewerConfig.light_theme()

        assert config.theme == "light"
        assert isinstance(config, ViewerConfig)

    def test_minimal_preset(self):
        """Test minimal preset."""
        config = ViewerConfig.minimal()

        assert config.theme == "light"
        assert config.show_info is False
        assert config.show_labels is False
        assert config.show_panel_count is False


class TestViewerConfigMethods:
    """Test configuration methods."""

    def test_with_css_method(self):
        """Test with_css method."""
        css = ".panel { border: 2px solid blue; }"
        config = ViewerConfig().with_css(css)

        assert config.custom_css == css

    def test_with_option_method(self):
        """Test with_option method."""
        config = ViewerConfig().with_option("debug", True)

        assert config.config_options["debug"] is True

    def test_with_option_multiple_times(self):
        """Test with_option can be called multiple times."""
        config = (ViewerConfig()
                  .with_option("debug", True)
                  .with_option("theme_variant", "cool"))

        assert config.config_options["debug"] is True
        assert config.config_options["theme_variant"] == "cool"

    def test_method_chaining(self):
        """Test method chaining works correctly."""
        config = (ViewerConfig()
                  .with_sort("value", "desc")
                  .with_css(".panel { color: red; }")
                  .with_option("debug", True))

        assert config.initial_sort == [{"var": "value", "dir": "desc"}]
        assert config.custom_css == ".panel { color: red; }"
        assert config.config_options["debug"] is True


class TestMergeConfigs:
    """Test merge_configs function."""

    def test_merge_with_none_base(self):
        """Test merge with None base config."""
        override = {"theme": "dark"}
        result = merge_configs(None, override)

        assert result == {"theme": "dark"}

    def test_merge_with_none_override(self):
        """Test merge with None override config."""
        base = ViewerConfig(theme="dark")
        result = merge_configs(base, None)

        assert result["theme"] == "dark"

    def test_merge_with_both_none(self):
        """Test merge with both configs None."""
        result = merge_configs(None, None)

        assert result == {}

    def test_merge_basic(self):
        """Test basic config merge."""
        base = ViewerConfig(theme="light", show_info=True)
        override = {"theme": "dark"}
        result = merge_configs(base, override)

        assert result["theme"] == "dark"
        assert result["show_info"] is True

    def test_merge_override_takes_precedence(self):
        """Test override values take precedence."""
        base = ViewerConfig(
            theme="light",
            show_info=True,
            show_labels=True
        )
        override = {
            "show_info": False,
            "custom_option": "value"
        }
        result = merge_configs(base, override)

        assert result["theme"] == "light"
        assert result["show_info"] is False
        assert result["show_labels"] is True
        assert result["custom_option"] == "value"

    def test_merge_with_config_options(self):
        """Test merge includes config_options."""
        base = ViewerConfig(
            theme="dark",
            config_options={"debug": True}
        )
        override = {"show_info": False}
        result = merge_configs(base, override)

        assert result["theme"] == "dark"
        assert result["debug"] is True
        assert result["show_info"] is False


class TestViewerConfigEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_initial_filter_accepted(self):
        """Test initial_filter is accepted (no validation yet)."""
        filter_config = [{"var": "value", "op": "gt", "value": 10}]
        config = ViewerConfig(initial_filter=filter_config)

        assert config.initial_filter == filter_config

    def test_empty_initial_sort(self):
        """Test empty initial_sort list."""
        config = ViewerConfig(initial_sort=[])

        assert config.initial_sort == []

    def test_complex_configuration(self):
        """Test complex configuration with all options."""
        config = ViewerConfig(
            theme="auto",
            show_info=False,
            show_labels=False,
            show_panel_count=True,
            panel_aspect=16/9,
            initial_sort=[
                {"var": "value", "dir": "desc"},
                {"var": "name", "dir": "asc"}
            ],
            initial_filter=[
                {"var": "value", "op": "gt", "value": 10}
            ],
            custom_css="""
                .panel {
                    border: 2px solid blue;
                    margin: 10px;
                }
            """,
            config_options={
                "debug": True,
                "log_level": "info"
            }
        )

        result = config.to_dict()

        assert result["theme"] == "auto"
        assert result["show_info"] is False
        assert result["panel_aspect"] == pytest.approx(16/9)
        assert len(result["initial_sort"]) == 2
        assert result["debug"] is True
        assert result["log_level"] == "info"
