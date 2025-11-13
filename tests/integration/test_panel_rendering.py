"""Integration tests for panel rendering workflow."""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

matplotlib = pytest.importorskip("matplotlib")
plt = pytest.importorskip("matplotlib.pyplot")

from trelliscope import Display


class TestMatplotlibPanelRendering:
    """Test rendering matplotlib panels in Display."""

    def test_render_matplotlib_panels(self):
        """Test end-to-end workflow with matplotlib figures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create matplotlib figures
            def make_plot(i):
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.plot([1, 2, 3, 4], [i, i * 2, i * 3, i * 4])
                ax.set_title(f"Plot {i}")
                ax.set_xlabel("X")
                ax.set_ylabel("Y")
                return fig

            # Create DataFrame with figure objects
            df = pd.DataFrame(
                {
                    "plot": [make_plot(i) for i in range(5)],
                    "category": ["A", "B", "C", "D", "E"],
                    "value": [10, 20, 30, 40, 50],
                }
            )

            # Create and write display
            output = (
                Display(df, name="matplotlib_test")
                .set_panel_column("plot")
                .infer_metas()
                .write(output_path=Path(tmpdir) / "output")
            )

            # Clean up matplotlib figures
            for fig in df["plot"]:
                plt.close(fig)

            # Verify output structure
            assert output.exists()
            assert (output / "displayInfo.json").exists()
            assert (output / "metadata.csv").exists()
            assert (output / "panels").is_dir()

            # Verify panel files
            panel_files = list((output / "panels").glob("*.png"))
            assert len(panel_files) == 5

            # Verify panel filenames (indexed 0-4)
            expected_files = {f"{i}.png" for i in range(5)}
            actual_files = {f.name for f in panel_files}
            assert actual_files == expected_files

            # Verify each panel file has content
            for panel_file in panel_files:
                assert panel_file.stat().st_size > 1000  # PNG should have substance

            # Verify metadata CSV doesn't include plot column
            metadata = pd.read_csv(output / "metadata.csv")
            assert len(metadata) == 5
            assert "plot" not in metadata.columns
            assert "category" in metadata.columns
            assert "value" in metadata.columns

    def test_render_panels_false_skips_rendering(self):
        """Test that render_panels=False skips panel rendering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create DataFrame with figures
            def make_plot(i):
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3])
                return fig

            df = pd.DataFrame(
                {"plot": [make_plot(i) for i in range(3)], "value": [1, 2, 3]}
            )

            # Write without rendering
            output = (
                Display(df, name="no_render")
                .set_panel_column("plot")
                .write(output_path=Path(tmpdir) / "output", render_panels=False)
            )

            # Clean up figures
            for fig in df["plot"]:
                plt.close(fig)

            # Verify panels directory was NOT created
            assert not (output / "panels").exists()

            # But JSON and CSV should still exist
            assert (output / "displayInfo.json").exists()
            assert (output / "metadata.csv").exists()

    def test_lazy_panel_rendering(self):
        """Test rendering panels from callable (lazy evaluation)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create callables that return figures
            def make_plot_callable(i):
                def create_plot():
                    fig, ax = plt.subplots()
                    ax.plot([1, 2, 3], [i, i * 2, i * 3])
                    ax.set_title(f"Lazy Plot {i}")
                    return fig

                return create_plot

            df = pd.DataFrame(
                {
                    "plot": [make_plot_callable(i) for i in range(3)],
                    "label": ["Plot A", "Plot B", "Plot C"],
                }
            )

            # Write display (callables will be executed during render)
            output = (
                Display(df, name="lazy_test")
                .set_panel_column("plot")
                .write(output_path=Path(tmpdir) / "output")
            )

            # Verify panels were rendered
            panel_files = list((output / "panels").glob("*.png"))
            assert len(panel_files) == 3

            # Clean up any figures that might be left
            plt.close("all")

    def test_mixed_plot_styles(self):
        """Test rendering panels with different matplotlib styles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create different types of plots
            plots = []

            # Line plot
            fig1, ax1 = plt.subplots()
            ax1.plot([1, 2, 3, 4], [1, 4, 2, 3])
            plots.append(fig1)

            # Scatter plot
            fig2, ax2 = plt.subplots()
            ax2.scatter([1, 2, 3, 4], [3, 1, 4, 2])
            plots.append(fig2)

            # Bar plot
            fig3, ax3 = plt.subplots()
            ax3.bar(["A", "B", "C"], [5, 7, 3])
            plots.append(fig3)

            df = pd.DataFrame({"plot": plots, "plot_type": ["line", "scatter", "bar"]})

            # Write display
            output = (
                Display(df, name="mixed_plots")
                .set_panel_column("plot")
                .infer_metas()
                .write(output_path=Path(tmpdir) / "output")
            )

            # Clean up figures
            for fig in plots:
                plt.close(fig)

            # Verify all panels rendered
            panel_files = list((output / "panels").glob("*.png"))
            assert len(panel_files) == 3

    def test_panel_rendering_with_errors(self):
        """Test that rendering continues even if some panels fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mix of valid figures and invalid objects
            fig1, ax1 = plt.subplots()
            ax1.plot([1, 2, 3])

            fig2, ax2 = plt.subplots()
            ax2.plot([4, 5, 6])

            df = pd.DataFrame(
                {
                    "plot": [fig1, "not a figure", fig2],  # Middle one will fail
                    "value": [1, 2, 3],
                }
            )

            # Write display (should continue despite error)
            output = (
                Display(df, name="error_test")
                .set_panel_column("plot")
                .write(output_path=Path(tmpdir) / "output")
            )

            # Clean up figures
            plt.close(fig1)
            plt.close(fig2)

            # Verify some panels were rendered (2 out of 3)
            panel_files = list((output / "panels").glob("*.png"))
            assert len(panel_files) == 2  # Only the valid figures

    def test_large_number_of_panels(self):
        """Test rendering many panels efficiently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            n_panels = 50

            # Create many small figures
            def make_simple_plot(i):
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.plot([1, 2, 3], [i, i + 1, i + 2])
                ax.set_title(f"Plot {i}")
                return fig

            df = pd.DataFrame(
                {
                    "plot": [make_simple_plot(i) for i in range(n_panels)],
                    "index": range(n_panels),
                }
            )

            # Write display
            output = (
                Display(df, name="many_panels")
                .set_panel_column("plot")
                .write(output_path=Path(tmpdir) / "output")
            )

            # Clean up all figures
            for fig in df["plot"]:
                plt.close(fig)

            # Verify all panels rendered
            panel_files = list((output / "panels").glob("*.png"))
            assert len(panel_files) == n_panels

            # Verify displayInfo.json and metadata.csv
            with open(output / "displayInfo.json") as f:
                info = json.load(f)
            assert info["name"] == "many_panels"

            metadata = pd.read_csv(output / "metadata.csv")
            assert len(metadata) == n_panels


class TestPanelRenderingConfiguration:
    """Test panel rendering with different configurations."""

    def test_custom_dpi(self):
        """Test rendering with custom DPI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])

            df = pd.DataFrame({"plot": [fig], "value": [1]})

            # TODO: Add support for custom DPI in Display.write()
            # For now, just test default behavior
            output = (
                Display(df, name="custom_dpi")
                .set_panel_column("plot")
                .write(output_path=Path(tmpdir) / "output")
            )

            plt.close(fig)

            # Verify panel exists
            panel_files = list((output / "panels").glob("*.png"))
            assert len(panel_files) == 1
