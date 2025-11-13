"""Tests for MatplotlibAdapter."""

import tempfile
from pathlib import Path

import pytest

matplotlib = pytest.importorskip("matplotlib")
plt = pytest.importorskip("matplotlib.pyplot")

from trelliscope.panels.matplotlib_adapter import MatplotlibAdapter


class TestMatplotlibAdapterDetect:
    """Tests for matplotlib figure detection."""

    def test_detect_matplotlib_figure(self):
        """Test detection of matplotlib Figure objects."""
        fig, ax = plt.subplots()
        adapter = MatplotlibAdapter()
        assert adapter.detect(fig) is True

    def test_detect_non_matplotlib_object(self):
        """Test that non-matplotlib objects are not detected."""
        adapter = MatplotlibAdapter()
        assert adapter.detect("not a figure") is False
        assert adapter.detect(123) is False
        assert adapter.detect(None) is False
        assert adapter.detect([1, 2, 3]) is False

    def test_detect_dict(self):
        """Test that dict objects are not detected as matplotlib."""
        adapter = MatplotlibAdapter()
        assert adapter.detect({"data": []}) is False


class TestMatplotlibAdapterSave:
    """Tests for saving matplotlib figures."""

    def test_save_creates_png_file(self):
        """Test saving figure as PNG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])

            adapter = MatplotlibAdapter(output_format="png")
            output_path = adapter.save(fig, Path(tmpdir) / "test")

            assert output_path.exists()
            assert output_path.suffix == ".png"
            assert output_path.name == "test.png"
            plt.close(fig)

    def test_save_creates_jpeg_file(self):
        """Test saving figure as JPEG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])

            adapter = MatplotlibAdapter(output_format="jpeg")
            output_path = adapter.save(fig, Path(tmpdir) / "test")

            assert output_path.exists()
            assert output_path.suffix == ".jpeg"
            plt.close(fig)

    def test_save_creates_svg_file(self):
        """Test saving figure as SVG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])

            adapter = MatplotlibAdapter(output_format="svg")
            output_path = adapter.save(fig, Path(tmpdir) / "test")

            assert output_path.exists()
            assert output_path.suffix == ".svg"
            plt.close(fig)

    def test_save_with_custom_dpi(self):
        """Test saving with custom DPI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])

            adapter = MatplotlibAdapter(output_format="png", dpi=150)
            output_path = adapter.save(fig, Path(tmpdir) / "test")

            assert output_path.exists()
            plt.close(fig)

    def test_save_override_format_in_kwargs(self):
        """Test overriding format via kwargs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])

            # Adapter configured for PNG
            adapter = MatplotlibAdapter(output_format="png")
            # But save as SVG
            output_path = adapter.save(fig, Path(tmpdir) / "test", format="svg")

            assert output_path.suffix == ".svg"
            plt.close(fig)

    def test_save_non_figure_raises_error(self):
        """Test that saving non-figure raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = MatplotlibAdapter()

            with pytest.raises(ValueError, match="not a matplotlib Figure"):
                adapter.save("not a figure", Path(tmpdir) / "test")


class TestMatplotlibAdapterConfiguration:
    """Tests for adapter configuration."""

    def test_initialization_defaults(self):
        """Test default configuration."""
        adapter = MatplotlibAdapter()
        assert adapter.format == "png"
        assert adapter.dpi == 100
        assert adapter.bbox_inches == "tight"

    def test_initialization_custom(self):
        """Test custom configuration."""
        adapter = MatplotlibAdapter(
            output_format="svg", dpi=150, bbox_inches="standard"
        )
        assert adapter.format == "svg"
        assert adapter.dpi == 150
        assert adapter.bbox_inches == "standard"

    def test_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid format"):
            MatplotlibAdapter(output_format="invalid")

    def test_get_interface_type(self):
        """Test getting interface type."""
        adapter = MatplotlibAdapter()
        assert adapter.get_interface_type() == "panel_local"

    def test_get_format(self):
        """Test getting format."""
        adapter = MatplotlibAdapter(output_format="svg")
        assert adapter.get_format() == "svg"


class TestMatplotlibAdapterIntegration:
    """Integration tests for matplotlib adapter."""

    def test_full_workflow(self):
        """Test complete workflow from figure to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create figure
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
            ax.set_title("Test Plot")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")

            # Save with adapter
            adapter = MatplotlibAdapter(output_format="png", dpi=100)
            output_path = adapter.save(fig, Path(tmpdir) / "myplot")

            # Verify file exists and has content
            assert output_path.exists()
            assert output_path.stat().st_size > 1000  # Should have some content

            plt.close(fig)

    def test_multiple_figures(self):
        """Test saving multiple figures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = MatplotlibAdapter()

            for i in range(5):
                fig, ax = plt.subplots()
                ax.plot(range(i + 1))

                output_path = adapter.save(fig, Path(tmpdir) / f"plot_{i}")

                assert output_path.exists()
                assert output_path.name == f"plot_{i}.png"

                plt.close(fig)

            # Verify all files created
            files = list(Path(tmpdir).glob("*.png"))
            assert len(files) == 5
