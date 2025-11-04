"""HTML generation utilities for trelliscope viewer."""

from pathlib import Path
from typing import Optional, Dict, Any


def generate_viewer_html(
    display_name: str,
    config: Optional[Dict[str, Any]] = None,
    viewer_version: str = "latest",
) -> str:
    """Generate HTML page that loads trelliscopejs viewer from CDN.

    This creates a standalone HTML page that loads the trelliscopejs-lib
    JavaScript viewer from a CDN and initializes it with the display.

    Parameters
    ----------
    display_name : str
        Name of the display directory
    config : dict, optional
        Additional configuration options for the viewer
    viewer_version : str, optional
        Version of trelliscopejs-lib to use. Default: "latest"
        Can be specific version like "2.0.0" or "latest"

    Returns
    -------
    str
        Complete HTML page as string

    Examples
    --------
    >>> html = generate_viewer_html("my_display")
    >>> print(html[:50])
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset...

    >>> # With specific version
    >>> html = generate_viewer_html("my_display", viewer_version="2.0.0")

    >>> # With custom config
    >>> html = generate_viewer_html(
    ...     "my_display",
    ...     config={"theme": "dark"}
    ... )
    """
    # Build CDN URLs
    # Use specific version and UMD build for browser compatibility
    if viewer_version == "latest":
        viewer_version = "0.7.16"  # Use known working version instead of "latest"

    css_url = f"https://unpkg.com/trelliscopejs-lib@{viewer_version}/dist/assets/index.css"
    # Use unpkg.com - the official CDN for npm packages
    js_url = f"https://unpkg.com/trelliscopejs-lib@{viewer_version}/dist/assets/index.js"

    # Build config object (R API uses: trelliscopeApp(id, config))
    # The element ID is passed as first parameter, not in config
    config_dict = {
        "displayListPath": f"./{display_name}/displayInfo.json",
        "spa": False,
    }

    # Extract custom_css before merging (it's not a viewer config option)
    custom_css = None
    if config and "custom_css" in config:
        custom_css = config.pop("custom_css")

    # Merge custom config if provided
    if config:
        config_dict.update(config)

    # Convert config to JavaScript object notation
    config_js = _dict_to_js_object(config_dict)

    # Element ID for initialization
    element_id = "trelliscope-root"

    # Build custom CSS section
    custom_css_section = ""
    if custom_css:
        custom_css_section = f"\n        /* Custom CSS */\n        {custom_css}\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Trelliscope - {display_name}</title>
    <link rel="stylesheet" href="{css_url}">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        #trelliscope-root {{
            width: 100vw;
            height: 100vh;
        }}{custom_css_section}
    </style>
</head>
<body>
    <div id="{element_id}" class="trelliscope-not-spa"></div>

    <script type="module">
        try {{
            const module = await import('{js_url}');
            const initFunc = window.trelliscopeApp || module.trelliscopeApp;

            if (typeof initFunc === 'function') {{
                console.log('Initializing Trelliscope viewer...');
                initFunc('{element_id}', './config.json');
            }} else {{
                console.error('trelliscopeApp function not found!');
            }}
        }} catch (error) {{
            console.error('Error loading viewer:', error);
        }}
    </script>
</body>
</html>"""

    return html


def write_index_html(
    output_path: Path,
    html: str,
) -> Path:
    """Write HTML content to index.html file.

    Parameters
    ----------
    output_path : Path
        Path where index.html should be written
    html : str
        HTML content to write

    Returns
    -------
    Path
        Path to the created index.html file

    Examples
    --------
    >>> html = generate_viewer_html("my_display")
    >>> path = write_index_html(Path("output/index.html"), html)
    >>> print(path)
    output/index.html
    """
    output_path = Path(output_path)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def _dict_to_js_object(d: Dict[str, Any], indent: int = 12) -> str:
    """Convert Python dict to JavaScript object notation.

    Parameters
    ----------
    d : dict
        Dictionary to convert
    indent : int, optional
        Number of spaces for indentation. Default: 12

    Returns
    -------
    str
        JavaScript object notation string

    Examples
    --------
    >>> _dict_to_js_object({"id": "root", "spa": False})
    '{\\n            id: "root",\\n            spa: false\\n        }'
    """
    lines = ["{"]
    items = list(d.items())

    for i, (key, value) in enumerate(items):
        # Convert value to JS representation
        if isinstance(value, bool):
            js_value = "true" if value else "false"
        elif isinstance(value, str):
            js_value = f'"{value}"'
        elif isinstance(value, (int, float)):
            js_value = str(value)
        elif value is None:
            js_value = "null"
        elif isinstance(value, dict):
            js_value = _dict_to_js_object(value, indent + 4)
        elif isinstance(value, list):
            js_value = _list_to_js_array(value)
        else:
            js_value = f'"{str(value)}"'

        # Add comma except for last item
        comma = "," if i < len(items) - 1 else ""
        lines.append(f"{' ' * indent}{key}: {js_value}{comma}")

    lines.append(f"{' ' * (indent - 4)}}}")
    return "\n".join(lines)


def _list_to_js_array(lst: list) -> str:
    """Convert Python list to JavaScript array notation.

    Parameters
    ----------
    lst : list
        List to convert

    Returns
    -------
    str
        JavaScript array notation string

    Examples
    --------
    >>> _list_to_js_array([1, 2, 3])
    '[1, 2, 3]'
    >>> _list_to_js_array(["a", "b"])
    '["a", "b"]'
    """
    items = []
    for value in lst:
        if isinstance(value, bool):
            items.append("true" if value else "false")
        elif isinstance(value, str):
            items.append(f'"{value}"')
        elif isinstance(value, (int, float)):
            items.append(str(value))
        elif value is None:
            items.append("null")
        else:
            items.append(f'"{str(value)}"')

    return "[" + ", ".join(items) + "]"


def generate_deployment_readme(display_name: str) -> str:
    """Generate README.md with deployment instructions.

    Parameters
    ----------
    display_name : str
        Name of the display

    Returns
    -------
    str
        README content as markdown string

    Examples
    --------
    >>> readme = generate_deployment_readme("my_display")
    >>> print("# Deployment" in readme)
    True
    """
    readme = f"""# Trelliscope Display: {display_name}

This directory contains a trelliscope display that can be viewed in any web browser.

## Viewing Locally

### Option 1: Python HTTP Server

```bash
python -m http.server 8000
```

Then open http://localhost:8000/index.html in your browser.

### Option 2: Python 2

```bash
python -m SimpleHTTPServer 8000
```

### Option 3: PHP

```bash
php -S localhost:8000
```

### Option 4: Node.js

```bash
npx http-server -p 8000
```

## Deploying to Production

### GitHub Pages

1. Create a new repository on GitHub
2. Push this directory to the repository
3. Go to Settings → Pages
4. Select branch and root folder
5. Your display will be available at `https://username.github.io/repo-name/`

### Netlify

1. Sign up at https://netlify.com
2. Drag and drop this folder to Netlify
3. Your display will be deployed automatically

### AWS S3

1. Create an S3 bucket
2. Enable static website hosting
3. Upload all files
4. Set public read permissions
5. Access via the S3 website URL

### Other Hosting Options

Any static file hosting service will work:
- Vercel
- Cloudflare Pages
- Azure Static Web Apps
- Google Cloud Storage

## File Structure

```
{display_name}/
├── index.html           # Viewer page (open this!)
├── {display_name}/      # Display data
│   ├── displayInfo.json # Display configuration
│   ├── metadata.csv     # Panel metadata
│   └── panels/          # Panel files
│       ├── 0.png
│       ├── 1.png
│       └── ...
```

## Requirements

- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+)
- Internet connection (for loading trelliscopejs-lib from CDN)

## Offline Usage

To use offline, you'll need to download trelliscopejs-lib and modify index.html
to reference the local files instead of the CDN.

## Troubleshooting

### Display doesn't load

- Check browser console for errors
- Ensure all files are present
- Try a different web server
- Check that displayInfo.json is valid JSON

### Panels don't show

- Verify panels/ directory exists
- Check file paths in metadata.csv
- Ensure web server has read permissions

### CORS errors

- Use a proper web server, not file:// protocol
- Some browsers block local files for security

## Generated

Created with py-trelliscope: https://github.com/yourusername/py-trelliscope
"""

    return readme
