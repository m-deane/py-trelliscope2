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
        # Plotly HTML files contain Plotly.newPlot(divId, data, layout, config)
        # We need to extract the data and layout arrays/objects
        # Handle multiline content and binary-encoded data (bdata)
        
        def find_balanced_brackets(text, start_pos, open_char='[', close_char=']'):
            """Find balanced brackets starting from start_pos."""
            if text[start_pos] != open_char:
                return None
            depth = 0
            pos = start_pos
            while pos < len(text):
                if text[pos] == open_char:
                    depth += 1
                elif text[pos] == close_char:
                    depth -= 1
                    if depth == 0:
                        return pos + 1
                pos += 1
            return None
        
        def find_balanced_braces(text, start_pos):
            """Find balanced braces starting from start_pos."""
            return find_balanced_brackets(text, start_pos, '{', '}')
        
        # Find Plotly.newPlot call
        plotly_match = re.search(r'Plotly\.newPlot\(\s*["\']([^"\']+)["\']', html_content)
        if plotly_match:
            try:
                # Find the position after the div ID
                start_pos = plotly_match.end()
                
                # Skip whitespace and comma
                while start_pos < len(html_content) and html_content[start_pos] in ' \n\r\t,':
                    start_pos += 1
                
                # Extract data array (starts with [)
                if html_content[start_pos] == '[':
                    data_end = find_balanced_brackets(html_content, start_pos, '[', ']')
                    if data_end:
                        data_str = html_content[start_pos:data_end]
                        
                        # Skip whitespace and comma after data
                        layout_start = data_end
                        while layout_start < len(html_content) and html_content[layout_start] in ' \n\r\t,':
                            layout_start += 1
                        
                        # Extract layout object (starts with {)
                        if html_content[layout_start] == '{':
                            layout_end = find_balanced_braces(html_content, layout_start)
                            if layout_end:
                                layout_str = html_content[layout_start:layout_end]
                                
                                # Parse JSON
                                data = json.loads(data_str)
                                layout = json.loads(layout_str)
                                
                                # Create figure from extracted data
                                return go.Figure(data=data, layout=layout)
            except (json.JSONDecodeError, ValueError, IndexError):
                # If parsing fails, try next method
                pass

        # Try method 2: Look for script tags with JSON data
        # This handles both application/json and text/javascript with embedded JSON
        pattern2a = r'<script[^>]*type=["\']application/json["\'][^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</script>'
        pattern2b = r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>'
        
        # Try pattern with id first (more specific)
        matches = re.findall(pattern2a, html_content, re.DOTALL)
        for script_id, match_content in matches:
            try:
                fig_dict = json.loads(match_content.strip())
                if 'data' in fig_dict or 'layout' in fig_dict:
                    return go.Figure(fig_dict)
            except (json.JSONDecodeError, ValueError):
                continue
        
        # Try pattern without id
        matches = re.findall(pattern2b, html_content, re.DOTALL)
        for match_content in matches:
            try:
                fig_dict = json.loads(match_content.strip())
                if 'data' in fig_dict or 'layout' in fig_dict:
                    return go.Figure(fig_dict)
            except (json.JSONDecodeError, ValueError):
                continue

        # Method 3: Try to extract from window.PlotlyData (if present)
        pattern3 = r'window\.PlotlyData\s*=\s*(\{.*?\});'
        match3 = re.search(pattern3, html_content, re.DOTALL)
        if match3:
            try:
                fig_dict = json.loads(match3.group(1))
                if 'data' in fig_dict or 'layout' in fig_dict:
                    return go.Figure(fig_dict)
            except json.JSONDecodeError:
                pass
        
        # If all methods fail, raise informative error
        raise ValueError(
            "Could not extract Plotly figure from HTML. "
            "The HTML file may not contain a valid Plotly figure, or the format is not supported. "
            "Please ensure the HTML was generated using plotly.io.to_html() or plotly.offline.plot()."
        )

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
