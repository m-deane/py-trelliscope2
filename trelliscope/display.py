"""
Core Display class for creating interactive trelliscope displays.

This module provides the primary interface for creating trelliscope displays
from pandas DataFrames with visualization panels and metadata.
"""

from typing import Optional, Union, List, Dict, Any
from pathlib import Path
import pandas as pd
import hashlib
import json

from trelliscope.meta import MetaVariable
from trelliscope.inference import infer_meta_from_series
from trelliscope.serialization import (
    write_display_info,
    write_metadata_json,
    write_metadata_js,
)
from trelliscope.viewer_html import write_viewer_html
from trelliscope.multi_display import create_multi_display_structure


class Display:
    """
    Interactive visualization display for exploring collections of plots.

    Each row in the input DataFrame represents one panel with associated
    metadata (cognostics) for filtering and sorting.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame where one column contains panels (plots/figures) and
        other columns contain cognostics (metadata).
    name : str
        Unique identifier for this display. Must be non-empty.
    description : str, optional
        Human-readable description of the display.
    keysig : str, optional
        Unique key signature for the display. Auto-generated from data
        if not provided.
    path : Path or str, optional
        Output directory path. Defaults to './trelliscope_output'.

    Attributes
    ----------
    data : pd.DataFrame
        Input DataFrame with panels and cognostics.
    name : str
        Display identifier.
    description : str
        Display description.
    keysig : str
        Unique key signature.
    path : Path
        Output directory path.
    panel_column : str or None
        Column name containing panel data.
    metas : dict
        Meta variable configurations.
    state : dict
        Display state (layout, filters, sorts, labels).
    views : list
        Named view configurations.
    panel_options : dict
        Panel dimension options (width, height, aspect).

    Examples
    --------
    >>> import pandas as pd
    >>> from trelliscope import Display
    >>>
    >>> df = pd.DataFrame({
    ...     'plot': [fig1, fig2, fig3],
    ...     'category': ['A', 'B', 'C'],
    ...     'value': [10, 20, 30]
    ... })
    >>>
    >>> display = Display(df, name="my_display")
    >>> display.set_panel_column("plot")
    >>> display.write()

    Raises
    ------
    TypeError
        If data is not a pandas DataFrame.
    ValueError
        If name is empty or not a string.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        name: str,
        description: str = "",
        keysig: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
    ):
        # Validate data type
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                f"data must be a pandas DataFrame, got {type(data).__name__}"
            )

        # Validate name
        if not isinstance(name, str):
            raise ValueError(f"name must be a string, got {type(name).__name__}")
        if not name or not name.strip():
            raise ValueError("name cannot be empty")

        # Store core attributes
        self.data = data.copy()
        self.name = name.strip()
        self.description = description

        # Generate or use provided key signature
        if keysig is None:
            self.keysig = self._generate_keysig()
        else:
            self.keysig = keysig

        # Set output path
        if path is None:
            self.path = Path("./trelliscope_output")
        else:
            self.path = Path(path)

        # Initialize configuration
        self.panel_column: Optional[str] = None
        self._meta_vars: Dict[str, MetaVariable] = {}
        self.state: Dict[str, Any] = {
            "layout": {"ncol": 4, "nrow": None, "page": 1, "arrangement": "row"},
            "labels": [],
            "filters": [],
            "sorts": [],
        }
        self.views: List[Dict[str, Any]] = []
        self.panel_options: Dict[str, Any] = {
            "width": None,
            "height": None,
            "aspect": None,
            "forceSize": False,
        }

        # Panel interface configuration (how panels are loaded)
        self.panel_interface: Optional[Any] = None  # PanelInterface instance

        # Track output paths for viewer integration
        self._output_path: Optional[Path] = None  # Display directory (for writing files)
        self._root_path: Optional[Path] = None    # Root directory (for serving HTTP)

        # Viewer configuration
        self.viewer_config: Optional[Any] = None

    def _generate_keysig(self) -> str:
        """
        Generate unique key signature for display based on data content.

        Uses MD5 hash of display name, column names, data shape, and sample
        rows to create a unique identifier.

        Returns
        -------
        str
            MD5 hash as hexadecimal string.
        """
        components = {
            "name": self.name,
            "columns": list(self.data.columns),
            "shape": self.data.shape,
            "first_row": (
                self.data.iloc[0].to_dict() if len(self.data) > 0 else {}
            ),
            "last_row": (
                self.data.iloc[-1].to_dict() if len(self.data) > 0 else {}
            ),
        }

        content = json.dumps(components, sort_keys=True, default=str)
        return hashlib.md5(content.encode()).hexdigest()

    def set_panel_column(self, column: str) -> "Display":
        """
        Specify which column contains panel data (plots/figures).

        Parameters
        ----------
        column : str
            Column name containing panels.

        Returns
        -------
        Display
            Self for method chaining.

        Raises
        ------
        ValueError
            If column does not exist in DataFrame.

        Examples
        --------
        >>> display = Display(df, name="example")
        >>> display.set_panel_column("plot")
        """
        if column not in self.data.columns:
            raise ValueError(
                f"Column '{column}' not found in DataFrame. "
                f"Available columns: {list(self.data.columns)}"
            )

        self.panel_column = column
        return self

    def set_default_layout(
        self,
        ncol: int = 4,
        nrow: Optional[int] = None,
        page: int = 1,
        arrangement: str = "row",
    ) -> "Display":
        """
        Configure default grid layout for panels.

        Parameters
        ----------
        ncol : int, default=4
            Number of columns in the grid.
        nrow : int, optional
            Number of rows in the grid. If None, calculated automatically.
        page : int, default=1
            Starting page number.
        arrangement : {"row", "col"}, default="row"
            Panel arrangement order ("row" for row-major, "col" for column-major).

        Returns
        -------
        Display
            Self for method chaining.

        Raises
        ------
        ValueError
            If ncol < 1, page < 1, or arrangement not in {"row", "col"}.

        Examples
        --------
        >>> display.set_default_layout(ncol=3, nrow=2, arrangement="row")
        """
        if ncol < 1:
            raise ValueError(f"ncol must be >= 1, got {ncol}")
        if page < 1:
            raise ValueError(f"page must be >= 1, got {page}")
        if arrangement not in {"row", "col"}:
            raise ValueError(
                f"arrangement must be 'row' or 'col', got '{arrangement}'"
            )
        if nrow is not None and nrow < 1:
            raise ValueError(f"nrow must be >= 1 or None, got {nrow}")

        self.state["layout"] = {
            "ncol": ncol,
            "nrow": nrow,
            "page": page,
            "arrangement": arrangement,
        }
        return self

    def set_panel_options(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        aspect: Optional[float] = None,
        force_size: bool = False,
    ) -> "Display":
        """
        Configure panel dimensions and sizing behavior.

        Parameters
        ----------
        width : int, optional
            Panel width in pixels.
        height : int, optional
            Panel height in pixels. Ignored if aspect is specified.
        aspect : float, optional
            Aspect ratio (width/height). Overrides height if specified.
        force_size : bool, default=False
            Force exact dimensions regardless of content.

        Returns
        -------
        Display
            Self for method chaining.

        Raises
        ------
        ValueError
            If width or height < 1, or aspect <= 0.

        Examples
        --------
        >>> display.set_panel_options(width=800, height=600)
        >>> display.set_panel_options(width=800, aspect=1.5)  # 800x533
        """
        if width is not None and width < 1:
            raise ValueError(f"width must be >= 1, got {width}")
        if height is not None and height < 1:
            raise ValueError(f"height must be >= 1, got {height}")
        if aspect is not None and aspect <= 0:
            raise ValueError(f"aspect must be > 0, got {aspect}")

        self.panel_options = {
            "width": width,
            "height": height,
            "aspect": aspect,
            "forceSize": force_size,
        }
        return self

    def set_panel_interface(
        self,
        interface: Optional[Union[str, Any]] = None,
        **kwargs
    ) -> "Display":
        """
        Configure how panels are loaded in the viewer.

        Parameters
        ----------
        interface : PanelInterface, str, or None
            Panel interface configuration. Can be:
            - PanelInterface instance (LocalPanelInterface, RESTPanelInterface, etc.)
            - String type: "local", "rest", or "websocket" (creates interface with **kwargs)
            - None: Uses default LocalPanelInterface
        **kwargs
            Parameters passed to interface constructor if interface is a string.

        Returns
        -------
        Display
            Self for method chaining.

        Raises
        ------
        TypeError
            If interface is not a valid type.
        ValueError
            If interface configuration is invalid.

        Examples
        --------
        >>> from trelliscope import Display, RESTPanelInterface
        >>>
        >>> # Using interface object
        >>> interface = RESTPanelInterface(
        ...     base="http://localhost:5001/api/panels/my_display"
        ... )
        >>> display.set_panel_interface(interface)
        >>>
        >>> # Using string shorthand
        >>> display.set_panel_interface(
        ...     "rest",
        ...     base="http://localhost:5001/api/panels/my_display"
        ... )
        >>>
        >>> # Default local panels
        >>> display.set_panel_interface("local", format="png")
        """
        from trelliscope.panel_interface import (
            PanelInterface,
            LocalPanelInterface,
            create_panel_interface
        )

        if interface is None:
            # Default to local file panels
            self.panel_interface = LocalPanelInterface()
        elif isinstance(interface, str):
            # Create interface from string type
            self.panel_interface = create_panel_interface(interface, **kwargs)
        elif isinstance(interface, PanelInterface):
            # Use provided interface instance
            self.panel_interface = interface
        else:
            raise TypeError(
                f"interface must be PanelInterface, string, or None, "
                f"got {type(interface).__name__}"
            )

        return self

    def set_default_labels(self, labels: List[str]) -> "Display":
        """
        Set which meta variables to show as panel labels.

        Parameters
        ----------
        labels : list of str
            Column names to display as labels.

        Returns
        -------
        Display
            Self for method chaining.

        Raises
        ------
        ValueError
            If any label column does not exist in DataFrame.

        Examples
        --------
        >>> display.set_default_labels(["category", "score"])
        """
        missing = [col for col in labels if col not in self.data.columns]
        if missing:
            raise ValueError(
                f"Label columns not found in DataFrame: {missing}. "
                f"Available columns: {list(self.data.columns)}"
            )

        self.state["labels"] = labels
        return self

    def add_meta_variable(
        self,
        meta: MetaVariable,
        replace: bool = False,
    ) -> "Display":
        """
        Add a meta variable (cognostic) to the display.

        Parameters
        ----------
        meta : MetaVariable
            Meta variable instance to add.
        replace : bool, default=False
            If True, replace existing meta with same varname.
            If False, raise error if meta exists.

        Returns
        -------
        Display
            Self for method chaining.

        Raises
        ------
        TypeError
            If meta is not a MetaVariable instance.
        ValueError
            If meta.varname not in DataFrame columns, or if meta
            already exists and replace=False.

        Examples
        --------
        >>> from trelliscope import FactorMeta
        >>> meta = FactorMeta("category", levels=["A", "B", "C"])
        >>> display.add_meta_variable(meta)
        """
        if not isinstance(meta, MetaVariable):
            raise TypeError(
                f"meta must be a MetaVariable instance, "
                f"got {type(meta).__name__}"
            )

        # Validate that column exists in DataFrame
        if meta.varname not in self.data.columns:
            raise ValueError(
                f"Meta variable '{meta.varname}' not found in DataFrame. "
                f"Available columns: {list(self.data.columns)}"
            )

        # Check for duplicate
        if meta.varname in self._meta_vars and not replace:
            raise ValueError(
                f"Meta variable '{meta.varname}' already exists. "
                f"Use replace=True to overwrite."
            )

        self._meta_vars[meta.varname] = meta
        return self

    def add_meta_def(
        self,
        varname: str,
        meta_type: str,
        replace: bool = True,
        **kwargs
    ) -> "Display":
        """
        Define and add a meta variable inline using type and parameters.

        Parameters
        ----------
        varname : str
            Column name for meta variable.
        meta_type : str
            Meta type: "factor", "number", "date", "time", "currency", "href", "graph".
        replace : bool, default=True
            If True, replace existing meta with same varname.
        **kwargs
            Additional parameters for the meta type constructor.

        Returns
        -------
        Display
            Self for method chaining.

        Raises
        ------
        ValueError
            If meta_type is unknown or varname not in DataFrame.

        Examples
        --------
        >>> display.add_meta_def("category", "factor", levels=["A", "B", "C"])
        >>> display.add_meta_def("value", "number", digits=3, log=True)
        """
        from trelliscope.meta import (
            FactorMeta,
            NumberMeta,
            DateMeta,
            TimeMeta,
            CurrencyMeta,
            HrefMeta,
            GraphMeta,
            StringMeta,
        )

        type_map = {
            "factor": FactorMeta,
            "number": NumberMeta,
            "date": DateMeta,
            "time": TimeMeta,
            "currency": CurrencyMeta,
            "href": HrefMeta,
            "graph": GraphMeta,
            "string": StringMeta,
        }

        if meta_type not in type_map:
            raise ValueError(
                f"Unknown meta_type '{meta_type}'. "
                f"Must be one of {list(type_map.keys())}"
            )

        meta_class = type_map[meta_type]
        meta = meta_class(varname=varname, **kwargs)
        return self.add_meta_variable(meta, replace=replace)

    def infer_metas(
        self,
        columns: Optional[List[str]] = None,
        replace: bool = False,
    ) -> "Display":
        """
        Automatically infer and add meta variables from DataFrame columns.

        Parameters
        ----------
        columns : list of str, optional
            Columns to infer meta for. Defaults to all columns.
        replace : bool, default=False
            If True, replace existing metas for these columns.

        Returns
        -------
        Display
            Self for method chaining.

        Examples
        --------
        >>> # Infer all columns
        >>> display.infer_metas()
        >>>
        >>> # Infer specific columns
        >>> display.infer_metas(columns=["category", "value"])
        """
        if columns is None:
            columns = list(self.data.columns)

        for col in columns:
            if col not in self.data.columns:
                raise ValueError(
                    f"Column '{col}' not found in DataFrame. "
                    f"Available columns: {list(self.data.columns)}"
                )

            # Skip panel column (contains visualization objects, not metadata)
            if col == self.panel_column:
                continue

            # Skip if meta exists and not replacing
            if col in self._meta_vars and not replace:
                continue

            meta = infer_meta_from_series(self.data[col], varname=col)
            self._meta_vars[col] = meta

        return self

    def get_meta_variable(self, varname: str) -> MetaVariable:
        """
        Retrieve a specific meta variable by name.

        Parameters
        ----------
        varname : str
            Meta variable name to retrieve.

        Returns
        -------
        MetaVariable
            The meta variable instance.

        Raises
        ------
        KeyError
            If meta variable not found.

        Examples
        --------
        >>> meta = display.get_meta_variable("category")
        >>> print(meta.type)
        'factor'
        """
        if varname not in self._meta_vars:
            raise KeyError(
                f"Meta variable '{varname}' not found. "
                f"Available: {list(self._meta_vars.keys())}"
            )
        return self._meta_vars[varname]

    def get_all_meta_variables(self) -> Dict[str, MetaVariable]:
        """
        Get all meta variables as a dictionary.

        Returns
        -------
        dict
            Dictionary mapping varnames to MetaVariable instances.

        Examples
        --------
        >>> metas = display.get_all_meta_variables()
        >>> for varname, meta in metas.items():
        ...     print(f"{varname}: {meta.type}")
        """
        return self._meta_vars.copy()

    def list_meta_variables(self) -> List[str]:
        """
        List all meta variable names.

        Returns
        -------
        list of str
            Sorted list of meta variable names.

        Examples
        --------
        >>> display.list_meta_variables()
        ['category', 'date', 'value']
        """
        return sorted(self._meta_vars.keys())

    def write(
        self,
        output_path: Optional[Union[str, Path]] = None,
        force: bool = False,
        render_panels: bool = True,
        create_index: bool = True,
        viewer_debug: bool = False,
        use_multi_display: bool = True,
    ) -> Path:
        """
        Write display to disk as JSON specification and render panels.

        Creates output directory, renders panel files, and writes displayInfo.json,
        metaData.json, metaData.js, metadata.csv, and index.html files.

        Parameters
        ----------
        output_path : Path or str, optional
            Output directory path. Uses display.path if not provided.
        force : bool, default=False
            If True, overwrite existing output directory.
            If False, raise error if directory exists.
        render_panels : bool, default=True
            If True, render panel objects to files (PNG, HTML, etc.).
            If False, only write JSON/CSV files without rendering panels.
        create_index : bool, default=True
            If True, automatically generate index.html viewer file.
            If False, skip index.html generation.
        viewer_debug : bool, default=False
            If True, include debug console in index.html for troubleshooting.
            Only used when create_index=True.
        use_multi_display : bool, default=True
            If True, use multi-display structure with config.json and displays/
            subdirectory. If False, use single-display structure (EXPERIMENTAL).

        Returns
        -------
        Path
            Path to output directory.

        Raises
        ------
        ValueError
            If output directory exists and force=False, or if panel_column
            is not set (currently required).
        OSError
            If directory cannot be created or files cannot be written.

        Examples
        --------
        >>> import pandas as pd
        >>> import matplotlib.pyplot as plt
        >>> from trelliscope import Display
        >>>
        >>> # Create figures
        >>> def make_plot(i):
        ...     fig, ax = plt.subplots()
        ...     ax.plot([1, 2, 3], [i, i*2, i*3])
        ...     return fig
        >>>
        >>> df = pd.DataFrame({
        ...     'plot': [make_plot(i) for i in range(3)],
        ...     'category': ['A', 'B', 'C'],
        ...     'value': [10, 20, 30]
        ... })
        >>>
        >>> display = (Display(df, name="example")
        ...     .set_panel_column("plot")
        ...     .infer_metas())
        >>>
        >>> # Write with panel rendering
        >>> output_dir = display.write()
        >>> print(output_dir)
        ./trelliscope_output/example
        >>>
        >>> # Panels saved to:
        >>> # ./trelliscope_output/example/panels/0.png
        >>> # ./trelliscope_output/example/panels/1.png
        >>> # ./trelliscope_output/example/panels/2.png
        """
        # Validate that panel column is set first
        # (In future versions, this may be optional for metadata-only displays)
        if self.panel_column is None:
            raise ValueError(
                "panel_column must be set before writing. "
                "Use set_panel_column() to specify which column contains panels."
            )

        # Determine output path
        if output_path is None:
            output_path = self.path / self.name
        else:
            output_path = Path(output_path)

        # Check if directory exists
        if output_path.exists() and not force:
            raise ValueError(
                f"Output directory already exists: {output_path}. "
                f"Use force=True to overwrite."
            )

        # Create directory structure
        if use_multi_display:
            # Multi-display structure: root/displays/display_name/
            paths = create_multi_display_structure(
                output_path=output_path,
                display_name=self.name,
                description=self.description,
                collection_name=f"{self.name} Collection"
            )
            display_output_path = paths["display_dir"]
            root_path = paths["root"]
        else:
            # Single-display structure: root/ (experimental)
            output_path.mkdir(parents=True, exist_ok=True)
            display_output_path = output_path
            root_path = output_path

        # Render panels if requested
        if render_panels:
            self._render_panels(display_output_path)

        # Write displayInfo.json
        write_display_info(self, display_output_path)

        # Write metaData.json (required for file-based panels)
        write_metadata_json(self, display_output_path)

        # Write metaData.js (CRITICAL: required by viewer even with embedded cogData)
        write_metadata_js(self, display_output_path)

        # Write metadata CSV with cognostics
        self._write_metadata_csv(display_output_path)

        # Generate index.html viewer file at root
        if create_index:
            config_path = "./config.json" if use_multi_display else "./displayInfo.json"
            write_viewer_html(
                output_path=root_path,
                display_name=self.name,
                config_path=config_path,
                title=f"Trelliscope - {self.name}",
                debug=viewer_debug,
            )
            print(f"  Generated index.html viewer at {root_path}")

        # Store BOTH display path and root path for viewer integration
        self._output_path = display_output_path
        self._root_path = root_path

        return root_path

    def _render_panels(self, output_path: Path) -> None:
        """
        Render all panels to files in the panels/ directory.

        For each row in the DataFrame, extracts the panel object from the
        panel column and renders it using the appropriate adapter (matplotlib,
        plotly, etc.). Callables are executed before rendering (lazy evaluation).

        Parameters
        ----------
        output_path : Path
            Output directory path (panels will be saved to output_path/panels/)

        Raises
        ------
        ValueError
            If no adapter can handle a panel object.
        Exception
            If panel rendering fails.
        """
        from trelliscope.panels.manager import PanelManager

        # Create panels directory
        panels_dir = output_path / "panels"
        panels_dir.mkdir(exist_ok=True)

        # Create panel manager
        manager = PanelManager()

        # Get panel column
        panel_col = self.panel_column

        # Track panel format (will be set from first rendered panel)
        panel_format = None

        # Render each panel
        print(f"Rendering {len(self.data)} panels...")
        for idx, row in self.data.iterrows():
            panel_obj = row[panel_col]

            # Use index as panel ID
            panel_id = str(idx)

            try:
                panel_path = manager.save_panel(
                    panel_obj,
                    panels_dir,
                    panel_id
                )
                print(f"  Rendered panel {idx}: {panel_path.name}")

                # Capture panel format from first rendered panel
                if panel_format is None:
                    panel_format = panel_path.suffix.lstrip('.')  # Remove leading dot

            except Exception as e:
                print(f"  Error rendering panel {idx}: {e}")
                # Continue with remaining panels
                continue

        # Store panel format for serialization
        if panel_format:
            self._panel_format = panel_format

    def _write_metadata_csv(self, output_path: Path) -> Path:
        """
        Write metadata CSV file with panel metadata (cognostics).

        The CSV contains all DataFrame columns except the panel column.
        Panel references are stored in metaData.json and metaData.js files.

        Parameters
        ----------
        output_path : Path
            Output directory path.

        Returns
        -------
        Path
            Path to written metadata.csv file.
        """
        # Get non-panel columns only
        meta_cols = [col for col in self.data.columns if col != self.panel_column]

        # Extract metadata (without panel column)
        metadata_df = self.data[meta_cols].copy()

        # Write CSV
        csv_path = output_path / "metadata.csv"
        metadata_df.to_csv(csv_path, index=False)

        return csv_path

    def set_viewer_config(self, config) -> "Display":
        """Set viewer configuration for display.

        Configure viewer appearance and behavior including theme, initial sort/filter,
        and display options.

        Parameters
        ----------
        config : ViewerConfig or dict
            Viewer configuration. Can be ViewerConfig object or dictionary with
            configuration options.

        Returns
        -------
        Display
            Self for method chaining

        Examples
        --------
        >>> from trelliscope import Display
        >>> from trelliscope.config import ViewerConfig
        >>> import pandas as pd
        >>>
        >>> df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})
        >>> display = Display(df, name="test").set_panel_column('panel')
        >>>
        >>> # Using ViewerConfig object
        >>> config = ViewerConfig(theme="dark", show_info=False)
        >>> display.set_viewer_config(config)
        >>>
        >>> # Using dictionary
        >>> display.set_viewer_config({"theme": "light", "show_labels": True})
        >>>
        >>> # Using preset
        >>> display.set_viewer_config(ViewerConfig.dark_theme())
        >>>
        >>> # With chaining
        >>> display = (Display(df, name="test")
        ...     .set_panel_column('panel')
        ...     .set_viewer_config(ViewerConfig(theme="dark"))
        ...     .view())

        See Also
        --------
        ViewerConfig : Configuration class with presets and validation
        """
        from trelliscope.config import ViewerConfig

        if isinstance(config, dict):
            # Convert dict to ViewerConfig
            self.viewer_config = ViewerConfig(**config)
        elif isinstance(config, ViewerConfig):
            self.viewer_config = config
        else:
            raise TypeError(
                f"config must be ViewerConfig or dict, got {type(config).__name__}"
            )

        return self

    def view(
        self,
        port: int = 8000,
        open_browser: bool = True,
        blocking: bool = False,
        viewer_version: str = "latest",
        force_write: bool = False,
    ) -> str:
        """
        Launch interactive viewer for this display in a web browser.

        Starts a local HTTP server and opens the display in a web browser for
        interactive exploration. The server serves the display files along with
        the trelliscopejs viewer loaded from CDN.

        Parameters
        ----------
        port : int, default=8000
            Port number for the development server.
        open_browser : bool, default=True
            If True, automatically open the display in the default web browser.
            If False, just start the server and print the URL.
        blocking : bool, default=False
            If True, block execution until server is stopped (Ctrl+C).
            If False, run server in background thread and return immediately.
        viewer_version : str, default="latest"
            Version of trelliscopejs-lib to use. Can be "latest" or specific
            version like "2.0.0".
        force_write : bool, default=False
            If True, force rewriting the display even if it exists.
            If False, only write if not already written.

        Returns
        -------
        str
            URL where the display is being served.

        Raises
        ------
        ValueError
            If panel_column is not set.
        OSError
            If server cannot start (e.g., port in use).

        Examples
        --------
        >>> import pandas as pd
        >>> import matplotlib.pyplot as plt
        >>> from trelliscope import Display
        >>>
        >>> # Create and write display
        >>> df = pd.DataFrame({
        ...     'plot': [make_plot(i) for i in range(5)],
        ...     'category': ['A', 'B', 'C', 'D', 'E']
        ... })
        >>> display = (Display(df, name="my_display")
        ...     .set_panel_column("plot")
        ...     .infer_metas())
        >>>
        >>> # View in browser (non-blocking)
        >>> url = display.view()
        Display written to: ./trelliscope_output/my_display
        Display available at: http://localhost:8000/index.html
        Server running in background
        >>>
        >>> # Browser opens automatically, continue working...
        >>> # Do other work while server runs
        >>>
        >>> # Or run in blocking mode (Ctrl+C to stop):
        >>> display.view(blocking=True)
        Serving display at http://localhost:8000/index.html
        Press Ctrl+C to stop
        ^C
        Shutting down server...

        Notes
        -----
        - The server runs on localhost only (not accessible from other machines)
        - In non-blocking mode, the server runs in a background thread
        - Requires internet connection to load trelliscopejs-lib from CDN
        - Multiple displays can be viewed simultaneously on different ports
        """
        from trelliscope.server import DisplayServer
        from trelliscope.viewer import generate_viewer_html, write_index_html
        import webbrowser

        # Ensure display is written
        if self._output_path is None or force_write:
            print(f"Writing display...")
            self.write(force=force_write)
        else:
            # Check if output path still exists
            if not self._output_path.exists():
                print(f"Display not found at {self._output_path}, writing...")
                self.write(force=True)

        # Generate viewer HTML
        config_dict = None
        if self.viewer_config is not None:
            config_dict = self.viewer_config.to_dict()

        html = generate_viewer_html(
            display_name=self.name,
            config=config_dict,
            viewer_version=viewer_version
        )

        # Write index.html to root directory (for multi-display structure)
        # Use root path if available, otherwise fallback to output_path parent
        root_path = getattr(self, '_root_path', self._output_path.parent)
        index_path = root_path / "index.html"
        write_index_html(index_path, html)

        # Start server from ROOT path (not display subdirectory)
        # This is critical for multi-display structure to work correctly
        server = DisplayServer(root_path, port=port)

        try:
            server.start(blocking=False)
        except OSError as e:
            raise OSError(
                f"Cannot start server on port {port}. "
                f"Port may already be in use. Try a different port. "
                f"Original error: {e}"
            ) from e

        # Build URL
        url = f"{server.get_url()}/index.html"

        # Open browser if requested
        if open_browser:
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"Could not open browser: {e}")
                print(f"Please open manually: {url}")

        # Handle blocking vs non-blocking mode
        if blocking:
            print(f"Serving display at {url}")
            print("Press Ctrl+C to stop")
            try:
                server.httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                server.stop()
        else:
            print(f"Display available at: {url}")
            print("Server running in background")
            print(f"Note: Server will stop when Python exits")

        return url

    def show_interactive(
        self,
        mode: str = "external",
        port: int = 8050,
        debug: bool = False,
        force_write: bool = False,
        **kwargs
    ):
        """
        Launch interactive Plotly Dash viewer for this display.

        Creates an interactive Python-based viewer using Plotly Dash that can be
        launched from Jupyter notebooks or as a standalone web application. Provides
        native Python controls for filtering, sorting, and layout customization.

        Parameters
        ----------
        mode : str, default="external"
            Display mode:
            - "external": Open in external browser (default)
            - "inline": Embed in Jupyter notebook (requires jupyter-dash)
            - "jupyterlab": JupyterLab mode (requires jupyter-dash)
        port : int, default=8050
            Port number for the Dash server.
        debug : bool, default=False
            Enable Dash debug mode with hot reloading.
        force_write : bool, default=False
            If True, force rewriting the display even if it exists.
            If False, only write if not already written.
        **kwargs
            Additional arguments passed to DashViewer.

        Returns
        -------
        DashViewer or None
            DashViewer instance if mode="external", None if mode="inline" or "jupyterlab"

        Raises
        ------
        ValueError
            If panel_column is not set.
        ImportError
            If dash, dash-bootstrap-components, or jupyter-dash (for inline/jupyterlab modes)
            are not installed.

        Examples
        --------
        >>> import pandas as pd
        >>> from trelliscope import Display
        >>>
        >>> # Create display
        >>> df = pd.DataFrame({
        ...     'plot': [fig1, fig2, fig3],
        ...     'category': ['A', 'B', 'C'],
        ...     'value': [10, 20, 30]
        ... })
        >>> display = (Display(df, name="my_display")
        ...     .set_panel_column("plot")
        ...     .infer_metas())
        >>>
        >>> # Launch in external browser
        >>> display.show_interactive()
        🚀 Dash viewer starting on http://localhost:8050
        📊 Display: my_display
        📈 Panels: 3
        ✨ Opening browser...
        >>>
        >>> # Embed in Jupyter notebook (for interactive work)
        >>> display.show_interactive(mode="inline")
        >>>
        >>> # JupyterLab mode
        >>> display.show_interactive(mode="jupyterlab")
        >>>
        >>> # Custom port
        >>> display.show_interactive(port=8888)

        Notes
        -----
        - Requires: dash >= 2.18.0, dash-bootstrap-components >= 1.6.0
        - For Jupyter integration: jupyter-dash >= 0.4.2
        - Interactive features include:
          * Multi-type filters (factor, number, date, etc.)
          * Multi-column sorting
          * Dynamic grid layout (adjustable columns/rows)
          * Pagination controls
          * Panel labels
        - Unlike view(), this creates a native Python Dash app instead of serving
          static HTML files
        - Plotly panels are rendered natively (no iframes) for better performance
        - Use view() for traditional HTML viewer with trelliscopejs-lib

        See Also
        --------
        view : Launch traditional HTML viewer
        write : Write display files to disk
        """
        try:
            from trelliscope.dash_viewer import DashViewer
        except ImportError as e:
            raise ImportError(
                "Dash viewer requires additional dependencies. Install with:\n"
                "  pip install dash dash-bootstrap-components\n"
                "For Jupyter support also install:\n"
                "  pip install jupyter-dash"
            ) from e

        # Ensure display is written
        if self._output_path is None or force_write:
            print(f"Writing display...")
            self.write(force=force_write)
        else:
            # Check if output path still exists
            if not self._output_path.exists():
                print(f"Display not found at {self._output_path}, writing...")
                self.write(force=True)

        # Create and run viewer
        viewer = DashViewer(
            display_path=self._output_path,
            mode=mode,
            debug=debug,
            **kwargs
        )

        viewer.run(port=port)

        return viewer if mode == "external" else None

    def __repr__(self) -> str:
        """Return string representation of Display."""
        n_panels = len(self.data)
        n_cols = len(self.data.columns)
        panel_set = "set" if self.panel_column else "not set"

        return (
            f"Display(name='{self.name}', "
            f"n_panels={n_panels}, "
            f"n_columns={n_cols}, "
            f"panel_column={panel_set})"
        )
