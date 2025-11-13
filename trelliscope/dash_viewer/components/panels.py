"""
Panel rendering components for Dash viewer.
"""

from pathlib import Path
from typing import Optional, Union
import base64
import re
import json

from dash import html, dcc
import plotly.graph_objects as go


class PanelRenderer:
    """
    Handles rendering of different panel types (images, Plotly figures).
    """

    @staticmethod
    def render_image_panel(
        panel_path: Path,
        width: Optional[int] = None,
        height: Optional[int] = None,
        panel_key: Optional[str] = None
    ) -> html.Img:
        """
        Render image panel (PNG, JPEG, etc.).

        Parameters
        ----------
        panel_path : Path
            Path to image file
        width : int, optional
            Image width in pixels
        height : int, optional
            Image height in pixels
        panel_key : str, optional
            Panel key for component ID

        Returns
        -------
        html.Img
            Dash HTML Image component
        """
        if not panel_path.exists():
            return html.Div(
                "Image not found",
                style={
                    'width': f'{width}px' if width else '100%',
                    'height': f'{height}px' if height else '400px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'backgroundColor': '#f0f0f0',
                    'color': '#666',
                    'border': '1px dashed #ccc'
                }
            )

        # Read image and encode as base64
        with open(panel_path, 'rb') as f:
            image_bytes = f.read()

        encoded = base64.b64encode(image_bytes).decode('utf-8')

        # Detect image type
        ext = panel_path.suffix.lower()
        if ext == '.png':
            mime_type = 'image/png'
        elif ext in ['.jpg', '.jpeg']:
            mime_type = 'image/jpeg'
        elif ext == '.gif':
            mime_type = 'image/gif'
        elif ext == '.svg':
            mime_type = 'image/svg+xml'
        else:
            mime_type = 'image/png'

        src = f'data:{mime_type};base64,{encoded}'

        style = {
            'width': '100%',
            'height': 'auto',
            'display': 'block'
        }

        if width:
            style['maxWidth'] = f'{width}px'
        if height:
            style['maxHeight'] = f'{height}px'

        component_id = f'panel-img-{panel_key}' if panel_key else None

        return html.Img(
            id=component_id,
            src=src,
            style=style
        )

    @staticmethod
    def render_plotly_panel(
        panel_path: Path,
        width: Optional[int] = None,
        height: Optional[int] = None,
        panel_key: Optional[str] = None
    ) -> Union[dcc.Graph, html.Div]:
        """
        Render Plotly HTML panel as native Dash Graph.

        Extracts Plotly figure from HTML file and renders natively.

        Parameters
        ----------
        panel_path : Path
            Path to Plotly HTML file
        width : int, optional
            Figure width in pixels
        height : int, optional
            Figure height in pixels
        panel_key : str, optional
            Panel key for component ID

        Returns
        -------
        dcc.Graph or html.Div
            Dash Graph component or error div
        """
        if not panel_path.exists():
            return html.Div(
                "Plotly panel not found",
                style={
                    'width': f'{width}px' if width else '100%',
                    'height': f'{height}px' if height else '400px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'backgroundColor': '#f0f0f0',
                    'color': '#666',
                    'border': '1px dashed #ccc'
                }
            )

        try:
            fig = PanelRenderer.extract_plotly_figure(panel_path)

            # Update figure size if specified
            if width or height:
                update_dict = {}
                if width:
                    update_dict['width'] = width
                if height:
                    update_dict['height'] = height
                fig.update_layout(**update_dict)

            component_id = f'panel-plotly-{panel_key}' if panel_key else None

            return dcc.Graph(
                id=component_id,
                figure=fig,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                },
                style={
                    'width': '100%',
                    'height': '100%'
                }
            )

        except Exception as e:
            return html.Div(
                f"Error loading Plotly panel: {str(e)}",
                style={
                    'width': f'{width}px' if width else '100%',
                    'height': f'{height}px' if height else '400px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'backgroundColor': '#fff3cd',
                    'color': '#856404',
                    'border': '1px solid #ffc107',
                    'padding': '10px'
                }
            )

    @staticmethod
    def extract_plotly_figure(html_path: Path) -> go.Figure:
        """
        Extract Plotly figure from HTML file.

        Parses the HTML to find the Plotly.newPlot() call and extracts
        the figure configuration.

        Parameters
        ----------
        html_path : Path
            Path to Plotly HTML file

        Returns
        -------
        go.Figure
            Plotly Figure object

        Raises
        ------
        ValueError
            If figure cannot be extracted from HTML
        """
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Try method 1: Extract from Plotly.newPlot() call
        # Pattern: Plotly.newPlot('div-id', data, layout, config)
        pattern = r'Plotly\.newPlot\([\'"][\w-]+[\'"]\s*,\s*(\[.*?\])\s*,\s*(\{.*?\})\s*,\s*\{.*?\}\s*\)'

        match = re.search(pattern, html_content, re.DOTALL)

        if match:
            try:
                data_json = match.group(1)
                layout_json = match.group(2)

                # Parse JSON
                data = json.loads(data_json)
                layout = json.loads(layout_json)

                return go.Figure(data=data, layout=layout)
            except json.JSONDecodeError:
                pass

        # Try method 2: Look for plotly_data div with JSON
        pattern2 = r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>'
        matches = re.findall(pattern2, html_content, re.DOTALL)

        for match_content in matches:
            try:
                fig_dict = json.loads(match_content)
                if 'data' in fig_dict or 'layout' in fig_dict:
                    return go.Figure(fig_dict)
            except json.JSONDecodeError:
                continue

        # Try method 3: Use plotly.io.from_html (fallback)
        try:
            import plotly.io as pio
            return pio.from_html(html_content)
        except Exception as e:
            raise ValueError(f"Could not extract Plotly figure from HTML: {e}")

    @staticmethod
    def create_panel_container(
        panel_component: Union[html.Img, dcc.Graph, html.Div],
        labels: dict,
        panel_key: str
    ) -> html.Div:
        """
        Create panel container with panel and labels.

        Parameters
        ----------
        panel_component : component
            Panel component (image or graph)
        labels : dict
            Dictionary of label variables: {label_name: value}
        panel_key : str
            Panel key

        Returns
        -------
        html.Div
            Container div with panel and labels
        """
        # Create label elements
        label_elements = []
        for label_name, label_value in labels.items():
            label_elements.append(
                html.Div(
                    f"{label_name}: {label_value}",
                    className='panel-label'
                )
            )

        return html.Div(
            [
                html.Div(
                    panel_component,
                    className='panel-content'
                ),
                html.Div(
                    label_elements,
                    className='panel-labels'
                ) if label_elements else html.Div()
            ],
            className='panel-container',
            id=f'panel-container-{panel_key}'
        )
