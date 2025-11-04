"""
HTML viewer generation for trelliscope displays.

Generates index.html files that load the trelliscopejs-lib viewer.
"""

from pathlib import Path
from typing import Optional


def generate_viewer_html(
    display_name: str,
    config_path: str = "./config.json",
    title: Optional[str] = None,
    viewer_version: str = "0.7.16",
    debug: bool = False,
) -> str:
    """
    Generate HTML for trelliscope viewer.

    Parameters
    ----------
    display_name : str
        Name of the display for the page title.
    config_path : str, default="./config.json"
        Path to config.json file (relative to HTML file). Use "./config.json"
        for multi-display mode or "./displayInfo.json" for single-display mode.
    title : str, optional
        Custom page title. If not provided, uses "Trelliscope - {display_name}".
    viewer_version : str, default="0.7.16"
        Version of trelliscopejs-lib to use.
    debug : bool, default=False
        If True, includes debug console with fetch/image logging.

    Returns
    -------
    str
        Complete HTML document as string.

    Examples
    --------
    >>> html = generate_viewer_html("my_display")
    >>> with open("index.html", "w") as f:
    ...     f.write(html)
    """
    if title is None:
        title = f"Trelliscope - {display_name}"

    # Base HTML with standard viewer
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="https://unpkg.com/trelliscopejs-lib@{viewer_version}/dist/assets/index.css">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        #trelliscope-root {{
            width: 100vw;
            height: 100vh;
        }}"""

    if debug:
        html += """
        #debug-console {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.95);
            color: #00ff00;
            padding: 10px;
            font-family: monospace;
            font-size: 11px;
            max-height: 300px;
            overflow: auto;
            z-index: 10000;
            border-top: 2px solid #00ff00;
        }
        .debug-success { color: #00ff00; font-weight: bold; }
        .debug-error { color: #ff0000; font-weight: bold; }
        .debug-info { color: #00bfff; }"""

    html += """
    </style>
</head>
<body>
    <div id="trelliscope-root" class="trelliscope-not-spa"></div>"""

    if debug:
        html += """
    <div id="debug-console">
        <div style="font-weight: bold; margin-bottom: 5px;">Debug Console</div>
        <div id="debug-log"></div>
    </div>

    <script>
        const debugLog = document.getElementById('debug-log');
        function log(msg, type = 'info') {
            console.log(msg);
            const className = type === 'success' ? 'debug-success' : type === 'error' ? 'debug-error' : 'debug-info';
            debugLog.innerHTML += `<div class="${className}">${msg}</div>`;
            debugLog.parentElement.scrollTop = debugLog.parentElement.scrollHeight;
        }

        // Intercept fetch requests
        const originalFetch = window.fetch;
        window.fetch = async function(...args) {
            const url = args[0];
            log(`FETCH: ${url}`, 'info');
            const response = await originalFetch(...args);

            if (response.ok) {
                log(`  ✓ ${response.status} ${response.statusText}`, 'success');
            } else {
                log(`  ✗ ${response.status} ${response.statusText}`, 'error');
            }

            return response;
        };

        // Track image loading
        let imageCount = 0;
        const OriginalImage = window.Image;
        window.Image = function() {
            const img = new OriginalImage();
            const originalSrcSet = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src').set;
            Object.defineProperty(img, 'src', {
                set: function(value) {
                    imageCount++;
                    log(`IMAGE #${imageCount}: ${value}`, 'success');
                    originalSrcSet.call(this, value);
                },
                get: function() {
                    return this.getAttribute('src');
                }
            });
            return img;
        };

        log('✓ Debug interceptors active', 'success');
    </script>"""

    html += f"""

    <script type="module">
        try {{"""

    if debug:
        html += """
            log('Loading viewer module...', 'info');"""

    html += f"""
            const module = await import('https://unpkg.com/trelliscopejs-lib@{viewer_version}/dist/assets/index.js');
            const initFunc = window.trelliscopeApp || module.trelliscopeApp;

            if (typeof initFunc === 'function') {{"""

    if debug:
        html += """
                log('✓ Viewer loaded', 'success');
                log('Initializing display...', 'info');"""
    else:
        html += """
                console.log('Initializing Trelliscope viewer...');"""

    html += f"""
                initFunc('trelliscope-root', '{config_path}');"""

    if debug:
        html += """

                // Monitor for panel loading
                setTimeout(() => {
                    const root = document.getElementById('trelliscope-root');
                    const text = root ? root.textContent : '';

                    if (text.match(/\\d+\\s*-\\s*\\d+\\s+of\\s+\\d+/)) {
                        log('✓ Display loaded with panels', 'success');
                    } else if (text.includes('0 of 0')) {
                        log('✗ No panels loaded (0 of 0)', 'error');
                    }

                    const imgs = root ? root.querySelectorAll('img') : [];
                    log(`Total images in DOM: ${imgs.length}`, imgs.length > 0 ? 'success' : 'info');
                }, 3000);"""

    html += """
            } else {"""

    if debug:
        html += """
                log('✗ Viewer function not found!', 'error');
                log('Available: ' + Object.keys(module).join(', '), 'info');"""
    else:
        html += """
                console.error('trelliscopeApp function not found!');"""

    html += """
            }
        } catch (error) {"""

    if debug:
        html += """
            log(`✗ Error: ${error.message}`, 'error');"""
    else:
        html += """
            console.error('Error loading viewer:', error);"""

    html += """
        }
    </script>
</body>
</html>
"""

    return html


def write_viewer_html(
    output_path: Path,
    display_name: str,
    config_path: str = "./displayInfo.json",
    title: Optional[str] = None,
    viewer_version: str = "0.7.16",
    debug: bool = False,
) -> Path:
    """
    Write index.html viewer file to disk.

    Parameters
    ----------
    output_path : Path
        Directory to write index.html file.
    display_name : str
        Name of the display for the page title.
    config_path : str, default="./displayInfo.json"
        Path to displayInfo.json file (relative to HTML file).
    title : str, optional
        Custom page title. If not provided, uses "Trelliscope - {display_name}".
    viewer_version : str, default="0.7.16"
        Version of trelliscopejs-lib to use.
    debug : bool, default=False
        If True, includes debug console with fetch/image logging.

    Returns
    -------
    Path
        Path to written index.html file.

    Examples
    --------
    >>> from pathlib import Path
    >>> output = Path("./my_display")
    >>> html_path = write_viewer_html(output, "my_display")
    >>> print(html_path)
    ./my_display/index.html
    """
    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate HTML
    html = generate_viewer_html(
        display_name=display_name,
        config_path=config_path,
        title=title,
        viewer_version=viewer_version,
        debug=debug,
    )

    # Write to file
    html_path = output_path / "index.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html_path
