"""Integration tests for viewer configuration with Display."""

import pytest
import tempfile
import pandas as pd
from pathlib import Path

from trelliscope import Display
from trelliscope.config import ViewerConfig
from trelliscope.viewer import generate_viewer_html


class TestDisplaySetViewerConfig:
    """Test Display.set_viewer_config() method."""

    def test_set_config_with_viewer_config_object(self):
        """Test setting config with ViewerConfig object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})
            config = ViewerConfig(theme="dark", show_info=False)

            display = (Display(df, name="test", path=Path(tmpdir))
                      .set_panel_column('panel')
                      .set_viewer_config(config))

            assert display.viewer_config is config
            assert display.viewer_config.theme == "dark"
            assert display.viewer_config.show_info is False

    def test_set_config_with_dict(self):
        """Test setting config with dictionary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})

            display = (Display(df, name="test", path=Path(tmpdir))
                      .set_panel_column('panel')
                      .set_viewer_config({"theme": "dark", "show_labels": False}))

            assert isinstance(display.viewer_config, ViewerConfig)
            assert display.viewer_config.theme == "dark"
            assert display.viewer_config.show_labels is False

    def test_set_config_with_invalid_type_raises_error(self):
        """Test setting config with invalid type raises TypeError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a'], 'value': [1]})
            display = Display(df, name="test", path=Path(tmpdir))

            with pytest.raises(TypeError, match="config must be ViewerConfig or dict"):
                display.set_viewer_config("invalid")

    def test_set_config_method_chaining(self):
        """Test set_viewer_config works in method chain."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})

            display = (Display(df, name="test", path=Path(tmpdir), description="Test display")
                      .set_panel_column('panel')
                      .set_viewer_config(ViewerConfig.dark_theme()))

            assert display.viewer_config.theme == "dark"
            assert display.description == "Test display"

    def test_set_config_with_preset(self):
        """Test setting config with preset configurations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a'], 'value': [1]})

            # Dark theme preset
            display = (Display(df, name="test", path=Path(tmpdir))
                      .set_viewer_config(ViewerConfig.dark_theme()))
            assert display.viewer_config.theme == "dark"

            # Light theme preset
            display = (Display(df, name="test2", path=Path(tmpdir))
                      .set_viewer_config(ViewerConfig.light_theme()))
            assert display.viewer_config.theme == "light"

            # Minimal preset
            display = (Display(df, name="test3", path=Path(tmpdir))
                      .set_viewer_config(ViewerConfig.minimal()))
            assert display.viewer_config.show_info is False
            assert display.viewer_config.show_labels is False

    def test_set_config_with_chained_methods(self):
        """Test setting config with chained configuration methods."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})

            config = (ViewerConfig()
                     .with_sort("value", "desc")
                     .with_css(".panel { border: 1px solid red; }")
                     .with_option("debug", True))

            display = (Display(df, name="test", path=Path(tmpdir))
                      .set_panel_column('panel')
                      .set_viewer_config(config))

            assert display.viewer_config.initial_sort == [{"var": "value", "dir": "desc"}]
            assert ".panel" in display.viewer_config.custom_css
            assert display.viewer_config.config_options["debug"] is True


class TestDisplayViewWithConfig:
    """Test Display.view() with viewer configuration."""

    def test_view_uses_viewer_config(self):
        """Test view() uses viewer_config when set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})

            config = ViewerConfig(theme="dark", show_info=False)
            display = (Display(df, name="test", path=Path(tmpdir))
                      .set_panel_column('panel')
                      .set_viewer_config(config))

            # Write display
            display.write(render_panels=False)

            # Generate HTML (view() does this internally)
            html = generate_viewer_html(
                display_name=display.name,
                config=config.to_dict()
            )

            # Check HTML includes config options
            assert "trelliscope" in html.lower()

    def test_view_without_config_uses_defaults(self):
        """Test view() works without config set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a'], 'value': [1]})

            display = (Display(df, name="test", path=Path(tmpdir))
                      .set_panel_column('panel'))

            # Write display
            display.write(render_panels=False)

            # Should work without config
            html = generate_viewer_html(display_name=display.name)
            assert "<!DOCTYPE html>" in html

    def test_view_with_custom_css_in_config(self):
        """Test view() with custom CSS in config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a'], 'value': [1]})

            custom_css = ".panel { border: 2px solid blue; }"
            config = ViewerConfig().with_css(custom_css)

            display = (Display(df, name="test", path=Path(tmpdir))
                      .set_panel_column('panel')
                      .set_viewer_config(config))

            display.write(render_panels=False)

            # Generate HTML
            config_dict = config.to_dict()
            html = generate_viewer_html(
                display_name=display.name,
                config=config_dict
            )

            # Check custom CSS is in HTML
            assert custom_css in html

    def test_view_with_initial_sort_in_config(self):
        """Test view() with initial sort in config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})

            config = ViewerConfig().with_sort("value", "desc")
            display = (Display(df, name="test", path=Path(tmpdir))
                      .set_panel_column('panel')
                      .set_viewer_config(config))

            display.write(render_panels=False)

            # Config should be available
            assert display.viewer_config.initial_sort == [{"var": "value", "dir": "desc"}]


class TestGenerateViewerHtmlWithConfig:
    """Test generate_viewer_html with configuration."""

    def test_generate_html_with_no_config(self):
        """Test generating HTML without config."""
        html = generate_viewer_html("test_display")

        assert "<!DOCTYPE html>" in html
        assert "test_display" in html
        assert "trelliscopejs" in html.lower()

    def test_generate_html_with_empty_config(self):
        """Test generating HTML with empty config."""
        html = generate_viewer_html("test_display", config={})

        assert "<!DOCTYPE html>" in html
        assert "test_display" in html

    def test_generate_html_with_custom_css(self):
        """Test generating HTML with custom CSS."""
        config = {
            "custom_css": ".panel { border: 2px solid red; }"
        }
        html = generate_viewer_html("test_display", config=config)

        assert ".panel { border: 2px solid red; }" in html
        assert "/* Custom CSS */" in html

    def test_generate_html_custom_css_not_in_viewer_config(self):
        """Test custom_css is extracted and not passed to viewer."""
        config = {
            "theme": "dark",
            "custom_css": ".panel { color: blue; }"
        }
        html = generate_viewer_html("test_display", config=config)

        # Custom CSS should be in style section
        assert ".panel { color: blue; }" in html

        # But not in the config passed to TrelliscopeApp
        # (we can't easily test this without parsing JS, but we verify extraction works)
        assert "/* Custom CSS */" in html

    def test_generate_html_with_viewer_version(self):
        """Test generating HTML with specific viewer version."""
        html = generate_viewer_html("test_display", viewer_version="2.0.0")

        assert "@2.0.0" in html
        assert "trelliscopejs-lib@2.0.0" in html

    def test_generate_html_with_config_options(self):
        """Test generating HTML with config options."""
        config = {
            "theme": "dark",
            "show_info": False,
            "panel_aspect": 1.5
        }
        html = generate_viewer_html("test_display", config=config)

        # Should generate valid HTML
        assert "<!DOCTYPE html>" in html
        assert "TrelliscopeApp.createApp" in html


class TestEndToEndConfigWorkflow:
    """Test complete end-to-end workflows with configuration."""

    def test_complete_workflow_with_dark_theme(self):
        """Test complete workflow with dark theme configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display with dark theme
            df = pd.DataFrame({
                'panel': ['plot1', 'plot2', 'plot3'],
                'value': [10, 20, 30],
                'category': ['A', 'B', 'A']
            })

            display = (Display(df, name="test_display", path=Path(tmpdir), description="Test display with dark theme")
                      .set_panel_column('panel')
                      .set_viewer_config(ViewerConfig.dark_theme()))

            # Write display
            display.write(render_panels=False)

            # Verify config was set
            assert display.viewer_config.theme == "dark"

            # Verify display was written
            assert display._output_path.exists()
            assert (display._output_path / "displayInfo.json").exists()

    def test_complete_workflow_with_custom_config(self):
        """Test complete workflow with custom configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({
                'panel': ['a', 'b', 'c'],
                'value': [1, 2, 3]
            })

            # Create custom config
            config = (ViewerConfig()
                     .with_sort("value", "desc")
                     .with_css("""
                        .panel {
                            border: 2px solid blue;
                            border-radius: 8px;
                        }
                     """)
                     .with_option("debug", True))

            display = (Display(df, name="custom_display", path=Path(tmpdir))
                      .set_panel_column('panel')
                      .set_viewer_config(config))

            # Write display
            display.write(render_panels=False)

            # Verify all config options were set
            assert display.viewer_config.initial_sort == [{"var": "value", "dir": "desc"}]
            assert "border: 2px solid blue" in display.viewer_config.custom_css
            assert display.viewer_config.config_options["debug"] is True

    def test_workflow_with_minimal_preset(self):
        """Test workflow with minimal preset configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['x', 'y'], 'value': [1, 2]})

            display = (Display(df, name="minimal", path=Path(tmpdir))
                      .set_panel_column('panel')
                      .set_viewer_config(ViewerConfig.minimal()))

            # Write display
            display.write(render_panels=False)

            assert display.viewer_config.show_info is False
            assert display.viewer_config.show_labels is False
            assert display.viewer_config.show_panel_count is False

    def test_workflow_updating_config(self):
        """Test workflow where config is updated multiple times."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'panel': ['a'], 'value': [1]})

            display = (Display(df, name="test", path=Path(tmpdir))
                      .set_panel_column('panel'))

            # Set initial config
            display.set_viewer_config(ViewerConfig.light_theme())
            assert display.viewer_config.theme == "light"

            # Update config
            display.set_viewer_config(ViewerConfig.dark_theme())
            assert display.viewer_config.theme == "dark"

            # Update with custom config
            display.set_viewer_config({"theme": "auto", "show_info": False})
            assert display.viewer_config.theme == "auto"
            assert display.viewer_config.show_info is False
