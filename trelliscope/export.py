"""Static export utilities for deploying trelliscope displays."""

import shutil
from pathlib import Path
from typing import Optional, Union

from trelliscope.viewer import generate_viewer_html, generate_deployment_readme


def export_static(
    display_path: Union[str, Path],
    output_path: Union[str, Path],
    viewer_version: str = "latest",
    include_readme: bool = True,
    overwrite: bool = False,
) -> Path:
    """Export display as standalone static website.

    Creates a self-contained directory with all files needed to deploy
    the display to any static hosting service (GitHub Pages, Netlify, etc.).

    The exported site includes:
    - index.html with embedded trelliscopejs viewer
    - Complete display directory with all assets
    - Optional README.md with deployment instructions

    Parameters
    ----------
    display_path : Path or str
        Path to the display directory to export (e.g., "output/my_display")
    output_path : Path or str
        Where to create the exported site (e.g., "export/my_site")
    viewer_version : str, default="latest"
        Version of trelliscopejs-lib to use. Can be "latest" or specific
        version like "2.0.0"
    include_readme : bool, default=True
        If True, generate README.md with deployment instructions
    overwrite : bool, default=False
        If True, overwrite existing output directory.
        If False, raise error if output exists.

    Returns
    -------
    Path
        Path to the exported site directory

    Raises
    ------
    FileNotFoundError
        If display_path does not exist
    ValueError
        If output_path exists and overwrite=False
    OSError
        If files cannot be copied or written

    Examples
    --------
    >>> from trelliscope import Display, export_static
    >>> import pandas as pd
    >>>
    >>> # Create and write display
    >>> df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})
    >>> display = (Display(df, name="my_display")
    ...     .set_panel_column('panel')
    ...     .write())
    >>>
    >>> # Export for static hosting
    >>> site_dir = export_static(
    ...     display_path="trelliscope_output/my_display",
    ...     output_path="export/my_site"
    ... )
    >>>
    >>> # Result:
    >>> # export/my_site/
    >>> #   ├── index.html          # Viewer page
    >>> #   ├── README.md           # Deployment guide
    >>> #   └── my_display/         # Display data
    >>> #       ├── displayInfo.json
    >>> #       ├── metadata.csv
    >>> #       └── panels/
    >>>
    >>> # Deploy to GitHub Pages:
    >>> # 1. cd export/my_site
    >>> # 2. git init && git add . && git commit -m "Initial"
    >>> # 3. Push to gh-pages branch

    Notes
    -----
    - The exported site loads trelliscopejs-lib from CDN (requires internet)
    - All display files (panels, metadata) are copied to output directory
    - The site is completely self-contained and portable
    - Can be deployed to any static hosting service

    See Also
    --------
    Display.view : View display locally during development
    generate_viewer_html : Generate HTML for viewer
    """
    display_path = Path(display_path)
    output_path = Path(output_path)

    # Validate display path exists
    if not display_path.exists():
        raise FileNotFoundError(f"Display directory does not exist: {display_path}")

    if not display_path.is_dir():
        raise ValueError(f"Display path must be a directory: {display_path}")

    # Check required display files
    if not (display_path / "displayInfo.json").exists():
        raise ValueError(
            f"Invalid display directory: missing displayInfo.json in {display_path}"
        )

    # Check output path
    if output_path.exists() and not overwrite:
        raise ValueError(
            f"Output directory already exists: {output_path}. "
            f"Use overwrite=True to replace it."
        )

    # Create output directory (remove if exists and overwrite=True)
    if output_path.exists() and overwrite:
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Copy display directory
    display_name = display_path.name
    target_display_dir = output_path / display_name

    print(f"Copying display files from {display_path}...")
    shutil.copytree(display_path, target_display_dir)
    print(f"  ✓ Copied to {target_display_dir}")

    # Generate index.html
    print(f"Generating viewer HTML...")
    html = generate_viewer_html(display_name, viewer_version=viewer_version)
    index_path = output_path / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"  ✓ Created {index_path}")

    # Generate README if requested
    if include_readme:
        print(f"Generating deployment README...")
        readme = generate_deployment_readme(display_name)
        readme_path = output_path / "README.md"
        readme_path.write_text(readme, encoding="utf-8")
        print(f"  ✓ Created {readme_path}")

    print(f"\n✓ Static site exported to: {output_path}")
    print(f"\nTo deploy:")
    print(f"  1. cd {output_path}")
    print(f"  2. Serve locally: python -m http.server 8000")
    print(f"  3. Or deploy to GitHub Pages, Netlify, etc.")

    return output_path


def export_static_from_display(
    display,
    output_path: Union[str, Path],
    viewer_version: str = "latest",
    include_readme: bool = True,
    overwrite: bool = False,
    write_display: bool = True,
) -> Path:
    """Export display object directly to static site.

    Convenience method that writes the display (if needed) and exports it
    to a static site in one step.

    Parameters
    ----------
    display : Display
        Display object to export
    output_path : Path or str
        Where to create the exported site
    viewer_version : str, default="latest"
        Version of trelliscopejs-lib to use
    include_readme : bool, default=True
        If True, generate README.md with deployment instructions
    overwrite : bool, default=False
        If True, overwrite existing output directory
    write_display : bool, default=True
        If True, write display first if not already written

    Returns
    -------
    Path
        Path to the exported site directory

    Examples
    --------
    >>> from trelliscope import Display
    >>> import pandas as pd
    >>>
    >>> # Create display
    >>> df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})
    >>> display = (Display(df, name="my_display")
    ...     .set_panel_column('panel'))
    >>>
    >>> # Export directly (will write display automatically)
    >>> from trelliscope.export import export_static_from_display
    >>> site_dir = export_static_from_display(
    ...     display,
    ...     output_path="export/my_site"
    ... )
    """
    from trelliscope.display import Display

    if not isinstance(display, Display):
        raise TypeError(f"Expected Display object, got {type(display).__name__}")

    # Ensure display is written
    if write_display and display._output_path is None:
        print("Writing display...")
        display.write()
    elif display._output_path is None:
        raise ValueError(
            "Display has not been written. Call display.write() first or "
            "set write_display=True"
        )

    # Export the written display
    return export_static(
        display_path=display._output_path,
        output_path=output_path,
        viewer_version=viewer_version,
        include_readme=include_readme,
        overwrite=overwrite,
    )


def validate_export(export_path: Union[str, Path]) -> dict:
    """Validate that an exported site has all required files.

    Checks for required files and returns a validation report.

    Parameters
    ----------
    export_path : Path or str
        Path to exported site directory

    Returns
    -------
    dict
        Validation report with keys:
        - valid: bool, True if all checks pass
        - missing_files: list of missing required files
        - warnings: list of warnings
        - display_name: name of the display
        - panel_count: number of panel files found

    Examples
    --------
    >>> from trelliscope.export import validate_export
    >>>
    >>> report = validate_export("export/my_site")
    >>> if report['valid']:
    ...     print("Export is valid!")
    ... else:
    ...     print(f"Missing files: {report['missing_files']}")
    """
    export_path = Path(export_path)
    report = {
        "valid": True,
        "missing_files": [],
        "warnings": [],
        "display_name": None,
        "panel_count": 0,
    }

    # Check export directory exists
    if not export_path.exists():
        report["valid"] = False
        report["missing_files"].append(str(export_path))
        return report

    # Check for index.html
    index_path = export_path / "index.html"
    if not index_path.exists():
        report["valid"] = False
        report["missing_files"].append("index.html")

    # Find display directory (should be the only directory besides __pycache__)
    display_dirs = [
        d
        for d in export_path.iterdir()
        if d.is_dir() and d.name not in ["__pycache__", ".git"]
    ]

    if len(display_dirs) == 0:
        report["valid"] = False
        report["warnings"].append("No display directory found")
        return report

    if len(display_dirs) > 1:
        report["warnings"].append(
            f"Multiple directories found: {[d.name for d in display_dirs]}"
        )

    # Check display directory structure
    display_dir = display_dirs[0]
    report["display_name"] = display_dir.name

    display_info_path = display_dir / "displayInfo.json"
    if not display_info_path.exists():
        report["valid"] = False
        report["missing_files"].append(f"{display_dir.name}/displayInfo.json")

    metadata_path = display_dir / "metadata.csv"
    if not metadata_path.exists():
        report["valid"] = False
        report["missing_files"].append(f"{display_dir.name}/metadata.csv")

    panels_dir = display_dir / "panels"
    if not panels_dir.exists():
        report["warnings"].append(f"No panels directory found in {display_dir.name}")
    else:
        # Count panel files
        panel_files = list(panels_dir.glob("*"))
        panel_files = [f for f in panel_files if f.is_file()]
        report["panel_count"] = len(panel_files)

    # Check for README (optional but recommended)
    readme_path = export_path / "README.md"
    if not readme_path.exists():
        report["warnings"].append("No README.md found (optional but recommended)")

    return report
