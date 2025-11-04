"""
py-trelliscope: Interactive visualization displays for exploring collections of plots.

A Python port of R's trelliscope package enabling interactive exploration of
large collections of visualizations through automatic faceting, filtering,
sorting, and rich metadata.
"""

__version__ = "0.1.0"
__author__ = "py-trelliscope contributors"

from trelliscope.display import Display
from trelliscope.meta import (
    MetaVariable,
    FactorMeta,
    NumberMeta,
    DateMeta,
    TimeMeta,
    CurrencyMeta,
    HrefMeta,
    GraphMeta,
)
from trelliscope.panel_interface import (
    PanelInterface,
    LocalPanelInterface,
    RESTPanelInterface,
    WebSocketPanelInterface,
    create_panel_interface,
)
from trelliscope.inference import infer_meta_from_series, infer_meta_dict
from trelliscope.serialization import (
    serialize_display_info,
    write_display_info,
    serialize_to_json_string,
)
from trelliscope.panels import PanelRenderer
from trelliscope.panels.matplotlib_adapter import MatplotlibAdapter
from trelliscope.panels.plotly_adapter import PlotlyAdapter
from trelliscope.panels.manager import PanelManager
from trelliscope.server import DisplayServer
from trelliscope.viewer import generate_viewer_html, write_index_html
from trelliscope.export import (
    export_static,
    export_static_from_display,
    validate_export,
)

__all__ = [
    "Display",
    "MetaVariable",
    "FactorMeta",
    "NumberMeta",
    "DateMeta",
    "TimeMeta",
    "CurrencyMeta",
    "HrefMeta",
    "GraphMeta",
    "PanelInterface",
    "LocalPanelInterface",
    "RESTPanelInterface",
    "WebSocketPanelInterface",
    "create_panel_interface",
    "infer_meta_from_series",
    "infer_meta_dict",
    "serialize_display_info",
    "write_display_info",
    "serialize_to_json_string",
    "PanelRenderer",
    "MatplotlibAdapter",
    "PlotlyAdapter",
    "PanelManager",
    "DisplayServer",
    "generate_viewer_html",
    "write_index_html",
    "export_static",
    "export_static_from_display",
    "validate_export",
]
