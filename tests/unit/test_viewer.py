"""Unit tests for viewer HTML generation."""

import tempfile
from pathlib import Path

import pytest

from trelliscope.viewer import (
    _dict_to_js_object,
    _list_to_js_array,
    generate_deployment_readme,
    generate_viewer_html,
    write_index_html,
)


class TestGenerateViewerHTML:
    """Test HTML generation for viewer."""

    def test_generate_basic_html(self):
        """Test basic HTML generation."""
        html = generate_viewer_html("my_display")

        # Check essential elements
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "my_display" in html
        assert "trelliscopejs-lib" in html
        assert "Trelliscope(" in html  # Corrected API call pattern

    def test_html_contains_display_name(self):
        """Test display name appears in HTML."""
        html = generate_viewer_html("test_display")

        assert "test_display" in html
        assert "./test_display/displayInfo.json" in html

    def test_html_with_latest_version(self):
        """Test HTML with latest CDN version."""
        html = generate_viewer_html("my_display", viewer_version="latest")

        # "latest" should resolve to specific version (0.7.16)
        assert "esm.sh/trelliscopejs-lib@0.7.16" in html
        assert "?bundle" in html

    def test_html_with_specific_version(self):
        """Test HTML with specific CDN version."""
        html = generate_viewer_html("my_display", viewer_version="2.0.0")

        assert "unpkg.com/trelliscopejs-lib@2.0.0" in html

    def test_html_with_custom_config(self):
        """Test HTML with custom config."""
        config = {"theme": "dark", "debug": True}
        html = generate_viewer_html("my_display", config=config)

        # Config should be merged into JS object
        assert "Trelliscope(" in html  # Corrected API call

    def test_html_has_required_structure(self):
        """Test HTML has all required structural elements."""
        html = generate_viewer_html("my_display")

        assert "<head>" in html
        assert "<body>" in html
        assert '<div id="trelliscope-root">' in html
        assert "</html>" in html

    def test_html_includes_css_link(self):
        """Test HTML includes CSS link."""
        html = generate_viewer_html("my_display")

        assert '<link rel="stylesheet"' in html
        assert "index.css" in html

    def test_html_includes_js_script(self):
        """Test HTML includes JS script tag."""
        html = generate_viewer_html("my_display")

        assert "<script" in html
        assert "esm.sh/trelliscopejs-lib" in html
        assert "?bundle" in html

    def test_html_uses_esm_modules(self):
        """Test HTML uses ES modules with esm.sh bundling."""
        html = generate_viewer_html("my_display")

        # Should use ESM with esm.sh (bundles all dependencies including React)
        assert '<script type="module">' in html
        assert "esm.sh/trelliscopejs-lib" in html
        assert "?bundle" in html

    def test_html_calls_trelliscope_api(self):
        """Test HTML calls correct Trelliscope API."""
        html = generate_viewer_html("my_display")

        # Should call Trelliscope(id, config) matching R API pattern
        assert "Trelliscope(" in html
        assert "'trelliscope-root'" in html or '"trelliscope-root"' in html


class TestWriteIndexHTML:
    """Test writing HTML to file."""

    def test_write_creates_file(self):
        """Test write creates index.html file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "index.html"
            html = generate_viewer_html("test")

            result = write_index_html(output_path, html)

            assert result == output_path
            assert output_path.exists()

    def test_write_content_matches(self):
        """Test written content matches input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "index.html"
            html = generate_viewer_html("test")

            write_index_html(output_path, html)

            content = output_path.read_text(encoding="utf-8")
            assert content == html

    def test_write_to_nested_path(self):
        """Test writing to nested directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "dir" / "index.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            html = generate_viewer_html("test")
            result = write_index_html(output_path, html)

            assert result.exists()
            assert result.read_text(encoding="utf-8") == html


class TestDictToJSObject:
    """Test Python dict to JavaScript object conversion."""

    def test_simple_dict(self):
        """Test simple dictionary conversion."""
        d = {"key": "value"}
        result = _dict_to_js_object(d)

        assert "key:" in result
        assert '"value"' in result
        assert "{" in result
        assert "}" in result

    def test_dict_with_boolean(self):
        """Test dict with boolean values."""
        d = {"enabled": True, "disabled": False}
        result = _dict_to_js_object(d)

        assert "enabled: true" in result
        assert "disabled: false" in result

    def test_dict_with_number(self):
        """Test dict with numeric values."""
        d = {"count": 42, "ratio": 3.14}
        result = _dict_to_js_object(d)

        assert "count: 42" in result
        assert "ratio: 3.14" in result

    def test_dict_with_none(self):
        """Test dict with None value."""
        d = {"value": None}
        result = _dict_to_js_object(d)

        assert "value: null" in result

    def test_dict_with_string(self):
        """Test dict with string value."""
        d = {"name": "test"}
        result = _dict_to_js_object(d)

        assert 'name: "test"' in result

    def test_nested_dict(self):
        """Test nested dictionary conversion."""
        d = {"outer": {"inner": "value"}}
        result = _dict_to_js_object(d)

        assert "outer: {" in result
        assert '"value"' in result

    def test_dict_with_list(self):
        """Test dict with list value."""
        d = {"items": [1, 2, 3]}
        result = _dict_to_js_object(d)

        assert "items: [1, 2, 3]" in result


class TestListToJSArray:
    """Test Python list to JavaScript array conversion."""

    def test_number_list(self):
        """Test list of numbers."""
        result = _list_to_js_array([1, 2, 3])
        assert result == "[1, 2, 3]"

    def test_string_list(self):
        """Test list of strings."""
        result = _list_to_js_array(["a", "b", "c"])
        assert result == '["a", "b", "c"]'

    def test_boolean_list(self):
        """Test list of booleans."""
        result = _list_to_js_array([True, False, True])
        assert result == "[true, false, true]"

    def test_mixed_list(self):
        """Test list with mixed types."""
        result = _list_to_js_array([1, "text", True, None])
        assert result == '[1, "text", true, null]'

    def test_empty_list(self):
        """Test empty list."""
        result = _list_to_js_array([])
        assert result == "[]"


class TestGenerateDeploymentReadme:
    """Test README generation."""

    def test_readme_contains_display_name(self):
        """Test README contains display name."""
        readme = generate_deployment_readme("my_display")

        assert "my_display" in readme

    def test_readme_has_deployment_sections(self):
        """Test README has key deployment sections."""
        readme = generate_deployment_readme("test")

        assert "# Trelliscope Display" in readme
        assert "Viewing Locally" in readme
        assert "Deploying to Production" in readme
        assert "File Structure" in readme

    def test_readme_has_hosting_options(self):
        """Test README lists hosting options."""
        readme = generate_deployment_readme("test")

        assert "GitHub Pages" in readme
        assert "Netlify" in readme
        assert "AWS S3" in readme

    def test_readme_has_python_server_command(self):
        """Test README includes Python server command."""
        readme = generate_deployment_readme("test")

        assert "python -m http.server" in readme

    def test_readme_has_troubleshooting(self):
        """Test README has troubleshooting section."""
        readme = generate_deployment_readme("test")

        assert "Troubleshooting" in readme
        assert "CORS" in readme or "cors" in readme.lower()


class TestViewerIntegration:
    """Integration tests for viewer generation."""

    def test_complete_viewer_workflow(self):
        """Test complete workflow from generation to writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate HTML
            html = generate_viewer_html("test_display")

            # Write to file
            output_path = Path(tmpdir) / "index.html"
            write_index_html(output_path, html)

            # Verify file exists and is valid
            assert output_path.exists()
            content = output_path.read_text(encoding="utf-8")

            # Verify content is complete
            assert "<!DOCTYPE html>" in content
            assert "test_display" in content
            assert "Trelliscope(" in content  # Corrected API call

    def test_viewer_with_custom_version(self):
        """Test viewer with custom version."""
        html = generate_viewer_html("test", viewer_version="1.5.0")

        assert "@1.5.0" in html

    def test_multiple_displays(self):
        """Test generating HTML for multiple displays."""
        displays = ["display1", "display2", "display3"]

        for display_name in displays:
            html = generate_viewer_html(display_name)
            assert display_name in html
            assert f"./{display_name}/displayInfo.json" in html
