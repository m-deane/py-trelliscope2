"""Unit tests for export utilities."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from trelliscope import Display
from trelliscope.export import (
    export_static,
    export_static_from_display,
    validate_export,
)


class TestExportStatic:
    """Test export_static function."""

    def test_export_creates_directory(self):
        """Test export creates output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n2\n")

            # Export
            output = Path(tmpdir) / "export"
            result = export_static(display_dir, output, include_readme=False)

            assert result == output
            assert output.exists()
            assert output.is_dir()

    def test_export_copies_display_directory(self):
        """Test export copies display files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            # Export
            output = Path(tmpdir) / "export"
            export_static(display_dir, output, include_readme=False)

            # Check copied display
            copied_display = output / "my_display"
            assert copied_display.exists()
            assert (copied_display / "displayInfo.json").exists()
            assert (copied_display / "metadata.csv").exists()

    def test_export_creates_index_html(self):
        """Test export creates index.html."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            # Export
            output = Path(tmpdir) / "export"
            export_static(display_dir, output, include_readme=False)

            # Check index.html
            index = output / "index.html"
            assert index.exists()
            content = index.read_text()
            assert "<!DOCTYPE html>" in content
            assert "my_display" in content
            assert "trelliscopejs" in content

    def test_export_creates_readme_by_default(self):
        """Test export creates README.md by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            # Export (default include_readme=True)
            output = Path(tmpdir) / "export"
            export_static(display_dir, output)

            # Check README
            readme = output / "README.md"
            assert readme.exists()
            content = readme.read_text()
            assert "Trelliscope Display" in content
            assert "my_display" in content

    def test_export_without_readme(self):
        """Test export without README when include_readme=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            # Export without README
            output = Path(tmpdir) / "export"
            export_static(display_dir, output, include_readme=False)

            # README should not exist
            assert not (output / "README.md").exists()

    def test_export_with_specific_viewer_version(self):
        """Test export with specific viewer version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            # Export with version
            output = Path(tmpdir) / "export"
            export_static(
                display_dir, output, viewer_version="2.0.0", include_readme=False
            )

            # Check version in HTML
            index = output / "index.html"
            content = index.read_text()
            assert "@2.0.0" in content

    def test_export_nonexistent_display_raises_error(self):
        """Test export with nonexistent display raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            display_dir = Path(tmpdir) / "nonexistent"
            output = Path(tmpdir) / "export"

            with pytest.raises(FileNotFoundError, match="does not exist"):
                export_static(display_dir, output)

    def test_export_invalid_display_raises_error(self):
        """Test export with invalid display raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory but missing displayInfo.json
            display_dir = Path(tmpdir) / "invalid"
            display_dir.mkdir()

            output = Path(tmpdir) / "export"

            with pytest.raises(ValueError, match="missing displayInfo.json"):
                export_static(display_dir, output)

    def test_export_existing_output_without_overwrite_raises_error(self):
        """Test export to existing directory without overwrite raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            # Export once
            output = Path(tmpdir) / "export"
            export_static(display_dir, output, include_readme=False)

            # Try to export again without overwrite
            with pytest.raises(ValueError, match="already exists"):
                export_static(display_dir, output, overwrite=False)

    def test_export_with_overwrite(self):
        """Test export with overwrite=True replaces existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            # Export once
            output = Path(tmpdir) / "export"
            export_static(display_dir, output, include_readme=False)

            # Create marker file
            marker = output / "marker.txt"
            marker.write_text("old")

            # Export again with overwrite
            export_static(display_dir, output, overwrite=True, include_readme=False)

            # Marker should be gone
            assert not marker.exists()
            # But export should still exist
            assert output.exists()
            assert (output / "index.html").exists()

    def test_export_with_panels(self):
        """Test export with panel files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display with panels
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            panels_dir = display_dir / "panels"
            panels_dir.mkdir()
            (panels_dir / "0.png").write_bytes(b"fake png data")
            (panels_dir / "1.png").write_bytes(b"fake png data")

            # Export
            output = Path(tmpdir) / "export"
            export_static(display_dir, output, include_readme=False)

            # Check panels copied
            exported_panels = output / "my_display" / "panels"
            assert exported_panels.exists()
            assert (exported_panels / "0.png").exists()
            assert (exported_panels / "1.png").exists()


class TestExportStaticFromDisplay:
    """Test export_static_from_display function."""

    def test_export_from_display_writes_if_needed(self):
        """Test export from display writes display if not written."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display (not written)
            df = pd.DataFrame({"panel": ["a", "b"], "value": [1, 2]})
            display = Display(df, name="test", path=Path(tmpdir)).set_panel_column(
                "panel"
            )

            # Export (should write automatically)
            output = Path(tmpdir) / "export"
            result = export_static_from_display(display, output, include_readme=False)

            # Check display was written
            assert display._output_path is not None
            assert display._output_path.exists()

            # Check export succeeded
            assert result.exists()
            assert (result / "index.html").exists()
            assert (result / "test").exists()

    def test_export_from_written_display(self):
        """Test export from already written display."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and write display
            df = pd.DataFrame({"panel": ["a"], "value": [1]})
            display = Display(df, name="test", path=Path(tmpdir)).set_panel_column(
                "panel"
            )
            display.write(render_panels=False)

            # Export
            output = Path(tmpdir) / "export"
            result = export_static_from_display(
                display, output, write_display=False, include_readme=False
            )

            assert result.exists()
            assert (result / "test").exists()

    def test_export_from_display_without_write_raises_error(self):
        """Test export from unwritten display with write_display=False raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display (not written)
            df = pd.DataFrame({"panel": ["a"], "value": [1]})
            display = Display(df, name="test", path=Path(tmpdir)).set_panel_column(
                "panel"
            )

            # Try to export without writing
            output = Path(tmpdir) / "export"
            with pytest.raises(ValueError, match="has not been written"):
                export_static_from_display(display, output, write_display=False)

    def test_export_from_display_invalid_type_raises_error(self):
        """Test export with non-Display object raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "export"

            with pytest.raises(TypeError, match="Expected Display object"):
                export_static_from_display("not a display", output)


class TestValidateExport:
    """Test validate_export function."""

    def test_validate_complete_export(self):
        """Test validation of complete export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create complete export
            export_dir = Path(tmpdir) / "export"
            export_dir.mkdir()

            # Create index.html
            (export_dir / "index.html").write_text("<html>test</html>")

            # Create display directory
            display_dir = export_dir / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            # Create panels
            panels_dir = display_dir / "panels"
            panels_dir.mkdir()
            (panels_dir / "0.png").write_bytes(b"data")

            # Create README
            (export_dir / "README.md").write_text("# README")

            # Validate
            report = validate_export(export_dir)

            assert report["valid"] is True
            assert len(report["missing_files"]) == 0
            assert report["display_name"] == "my_display"
            assert report["panel_count"] == 1

    def test_validate_missing_index_html(self):
        """Test validation catches missing index.html."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir) / "export"
            export_dir.mkdir()

            # Create display but no index.html
            display_dir = export_dir / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            report = validate_export(export_dir)

            assert report["valid"] is False
            assert "index.html" in report["missing_files"]

    def test_validate_missing_display_info(self):
        """Test validation catches missing displayInfo.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir) / "export"
            export_dir.mkdir()
            (export_dir / "index.html").write_text("<html></html>")

            # Create display dir without displayInfo.json
            display_dir = export_dir / "my_display"
            display_dir.mkdir()
            (display_dir / "metadata.csv").write_text("value\n1\n")

            report = validate_export(export_dir)

            assert report["valid"] is False
            assert any("displayInfo.json" in f for f in report["missing_files"])

    def test_validate_missing_metadata(self):
        """Test validation catches missing metadata.csv."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir) / "export"
            export_dir.mkdir()
            (export_dir / "index.html").write_text("<html></html>")

            # Create display dir without metadata.csv
            display_dir = export_dir / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')

            report = validate_export(export_dir)

            assert report["valid"] is False
            assert any("metadata.csv" in f for f in report["missing_files"])

    def test_validate_warns_missing_readme(self):
        """Test validation warns about missing README."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = Path(tmpdir) / "export"
            export_dir.mkdir()
            (export_dir / "index.html").write_text("<html></html>")

            display_dir = export_dir / "my_display"
            display_dir.mkdir()
            (display_dir / "displayInfo.json").write_text('{"name": "test"}')
            (display_dir / "metadata.csv").write_text("value\n1\n")

            report = validate_export(export_dir)

            # Valid but with warning
            assert report["valid"] is True
            assert any("README" in w for w in report["warnings"])

    def test_validate_nonexistent_export(self):
        """Test validation of nonexistent directory."""
        report = validate_export("/nonexistent/path")

        assert report["valid"] is False
        assert len(report["missing_files"]) > 0
