"""Integration tests for Display.view() and viewer functionality."""

import pytest
import tempfile
import pandas as pd
import time
from pathlib import Path

matplotlib = pytest.importorskip("matplotlib")
plt = pytest.importorskip("matplotlib.pyplot")

from trelliscope import Display


class TestDisplayView:
    """Test Display.view() method integration."""

    def test_view_writes_display_if_not_written(self):
        """Test view() writes display if not already written."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create matplotlib figures
            def make_plot(i):
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3], [i, i*2, i*3])
                return fig

            df = pd.DataFrame({
                'plot': [make_plot(i) for i in range(3)],
                'value': [10, 20, 30]
            })

            # Create display without writing
            display = (Display(df, name="test_view", path=Path(tmpdir))
                       .set_panel_column('plot'))

            # Clean up figures
            for fig in df['plot']:
                plt.close(fig)

            # view() should write the display
            url = display.view(port=8020, open_browser=False, blocking=False)

            # Verify display was written
            output_path = Path(tmpdir) / "test_view"
            assert output_path.exists()
            assert (output_path / "displayInfo.json").exists()
            assert (output_path / "metadata.csv").exists()

            # Verify URL format
            assert url == "http://localhost:8020/index.html"

            # Verify index.html was created
            assert (Path(tmpdir) / "index.html").exists()

    def test_view_uses_existing_display(self):
        """Test view() uses existing display if already written."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and write display first
            def make_plot(i):
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3])
                return fig

            df = pd.DataFrame({
                'plot': [make_plot(i) for i in range(2)],
                'value': [1, 2]
            })

            display = (Display(df, name="test", path=Path(tmpdir))
                       .set_panel_column('plot'))
            output_path = display.write()

            # Clean up figures
            for fig in df['plot']:
                plt.close(fig)

            # Get write time
            display_info_path = output_path / "displayInfo.json"
            write_time = display_info_path.stat().st_mtime

            # Wait a moment
            time.sleep(0.1)

            # view() should use existing display (not rewrite)
            url = display.view(port=8021, open_browser=False, blocking=False, force_write=False)

            # Verify file wasn't modified
            assert display_info_path.stat().st_mtime == write_time

            # Verify URL and index.html
            assert url == "http://localhost:8021/index.html"
            assert (Path(tmpdir) / "index.html").exists()

    def test_view_force_write_rewrites_display(self):
        """Test view() with force_write=True rewrites display."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and write display
            def make_plot(i):
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3])
                return fig

            df = pd.DataFrame({
                'plot': [make_plot(i) for i in range(2)],
                'value': [1, 2]
            })

            display = (Display(df, name="test", path=Path(tmpdir))
                       .set_panel_column('plot'))
            output_path = display.write()

            # Clean up figures
            for fig in df['plot']:
                plt.close(fig)

            # Get write time
            display_info_path = output_path / "displayInfo.json"
            write_time = display_info_path.stat().st_mtime

            # Wait to ensure timestamp difference
            time.sleep(0.2)

            # view() with force_write should rewrite
            display.view(port=8022, open_browser=False, blocking=False, force_write=True)

            # Verify file was modified
            assert display_info_path.stat().st_mtime > write_time

    def test_view_creates_index_html_with_correct_content(self):
        """Test view() creates index.html with correct content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create simple display
            df = pd.DataFrame({
                'panel': ['a', 'b'],
                'value': [1, 2]
            })

            display = (Display(df, name="test_html", path=Path(tmpdir))
                       .set_panel_column('panel'))
            display.write(render_panels=False)

            # Call view
            display.view(port=8023, open_browser=False, blocking=False)

            # Check index.html content
            index_path = Path(tmpdir) / "index.html"
            assert index_path.exists()

            content = index_path.read_text()
            assert "<!DOCTYPE html>" in content
            assert "test_html" in content
            assert "trelliscopejs-lib" in content
            assert "TrelliscopeApp.createApp" in content

    def test_view_with_custom_viewer_version(self):
        """Test view() with custom viewer version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({
                'panel': ['a'],
                'value': [1]
            })

            display = (Display(df, name="test", path=Path(tmpdir))
                       .set_panel_column('panel'))
            display.write(render_panels=False)

            # View with specific version
            display.view(port=8024, open_browser=False, blocking=False, viewer_version="2.0.0")

            # Check index.html has version
            index_path = Path(tmpdir) / "index.html"
            content = index_path.read_text()
            assert "@2.0.0" in content

    def test_view_without_panel_column_raises_error(self):
        """Test view() without panel column raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'value': [1, 2, 3]})

            display = Display(df, name="test", path=Path(tmpdir))

            # Should raise error because panel column not set
            with pytest.raises(ValueError, match="panel_column must be set"):
                display.view(port=8025, open_browser=False)

    def test_view_returns_correct_url(self):
        """Test view() returns correct URL format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({
                'panel': ['a'],
                'value': [1]
            })

            display = (Display(df, name="test", path=Path(tmpdir))
                       .set_panel_column('panel'))

            # Test URL format
            url = display.view(port=8032, open_browser=False, blocking=False)
            assert url == "http://localhost:8032/index.html"
            assert "localhost" in url
            assert "8032" in url
            assert "index.html" in url


class TestViewerIndexHTML:
    """Test index.html generation in viewer workflow."""

    def test_index_html_in_parent_directory(self):
        """Test index.html is created in parent of display directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({
                'panel': ['a', 'b'],
                'value': [1, 2]
            })

            display = (Display(df, name="my_display", path=Path(tmpdir))
                       .set_panel_column('panel'))
            display.write(render_panels=False)

            display.view(port=8027, open_browser=False, blocking=False)

            # index.html should be in tmpdir (parent of my_display)
            index_path = Path(tmpdir) / "index.html"
            assert index_path.exists()

            # Display directory should exist
            display_dir = Path(tmpdir) / "my_display"
            assert display_dir.exists()

    def test_index_html_references_correct_display(self):
        """Test index.html references correct display path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({
                'panel': ['a'],
                'value': [1]
            })

            display = (Display(df, name="my_display", path=Path(tmpdir))
                       .set_panel_column('panel'))
            display.write(render_panels=False)

            display.view(port=8028, open_browser=False, blocking=False)

            # Check index.html content
            index_path = Path(tmpdir) / "index.html"
            content = index_path.read_text()

            # Should reference display directory
            assert "./my_display/displayInfo.json" in content


class TestViewerWithPanels:
    """Test viewer with actual rendered panels."""

    def test_view_with_matplotlib_panels(self):
        """Test view() with matplotlib panels."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create matplotlib figures
            def make_plot(i):
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3], [i, i*2, i*3])
                ax.set_title(f"Plot {i}")
                return fig

            df = pd.DataFrame({
                'plot': [make_plot(i) for i in range(3)],
                'category': ['A', 'B', 'C']
            })

            display = (Display(df, name="plots", path=Path(tmpdir))
                       .set_panel_column('plot')
                       .infer_metas())

            # Clean up figures
            for fig in df['plot']:
                plt.close(fig)

            # View display
            url = display.view(port=8029, open_browser=False, blocking=False)

            # Verify complete structure
            display_dir = Path(tmpdir) / "plots"
            assert (display_dir / "displayInfo.json").exists()
            assert (display_dir / "metadata.csv").exists()
            assert (display_dir / "panels").is_dir()
            assert (Path(tmpdir) / "index.html").exists()

            # Verify panels were rendered
            panel_files = list((display_dir / "panels").glob("*.png"))
            assert len(panel_files) == 3

    def test_view_complete_workflow(self):
        """Test complete workflow from Display creation to view()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create display with method chaining
            def make_plot(i):
                fig, ax = plt.subplots(figsize=(5, 4))
                ax.plot([1, 2, 3, 4], [i, i*2, i*3, i*4], marker='o')
                ax.set_title(f"Category {chr(65+i)}")
                return fig

            df = pd.DataFrame({
                'plot': [make_plot(i) for i in range(4)],
                'category': ['A', 'B', 'C', 'D'],
                'value': [10, 20, 30, 40]
            })

            # Complete workflow with chaining
            display = (Display(df, name="complete_test", path=Path(tmpdir))
                       .set_panel_column('plot')
                       .infer_metas()
                       .set_default_layout(ncol=2, nrow=2))

            # Clean up figures
            for fig in df['plot']:
                plt.close(fig)

            # View (this will write and start server)
            url = display.view(port=8031, open_browser=False, blocking=False)

            # Verify everything exists
            output_dir = Path(tmpdir) / "complete_test"
            assert output_dir.exists()
            assert (output_dir / "displayInfo.json").exists()
            assert (output_dir / "metadata.csv").exists()
            assert (output_dir / "panels").is_dir()
            assert (Path(tmpdir) / "index.html").exists()

            # Verify metadata
            metadata = pd.read_csv(output_dir / "metadata.csv")
            assert len(metadata) == 4
            assert "category" in metadata.columns
            assert "value" in metadata.columns

            # Clean up all figures
            plt.close('all')
