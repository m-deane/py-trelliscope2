# py-trelliscope Documentation

This directory contains the complete documentation for py-trelliscope.

## Building Documentation Locally

### Prerequisites

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser
```

### Build HTML Documentation

```bash
cd docs
make html
```

Open `_build/html/index.html` in your browser.

### Clean Build

```bash
make clean
make html
```

### Live Reload (Development)

```bash
pip install sphinx-autobuild
make livehtml
```

Opens auto-reloading server at http://localhost:8000

## Documentation Structure

```
docs/
├── index.rst                    # Main documentation index
├── conf.py                      # Sphinx configuration
├── user_guide/                  # User guides and tutorials
│   ├── getting_started.rst
│   ├── creating_displays.rst
│   ├── meta_variables.rst
│   ├── panel_types.rst
│   └── examples.rst
├── api/                         # API reference
│   ├── display.rst
│   ├── meta.rst
│   ├── panels.rst
│   ├── serialization.rst
│   ├── inference.rst
│   ├── export.rst
│   └── server.rst
├── advanced/                    # Advanced topics
│   ├── architecture.rst
│   ├── panel_interfaces.rst
│   ├── custom_panels.rst
│   ├── performance.rst
│   └── deployment.rst
└── contributing/                # Contributor guides
    ├── development.rst
    ├── testing.rst
    └── documentation.rst
```

## Output Formats

### HTML

```bash
make html
```

Output: `_build/html/`

### PDF (requires LaTeX)

```bash
make latexpdf
```

Output: `_build/latex/py-trelliscope.pdf`

### EPUB

```bash
make epub
```

Output: `_build/epub/py-trelliscope.epub`

### Markdown

```bash
make markdown
```

Output: `_build/markdown/`

## Viewing Generated Documentation

The documentation is automatically deployed to GitHub Pages on every push to main:

**URL**: https://your-username.github.io/py-trelliscope2/

## Contributing to Documentation

### Adding New Pages

1. Create `.rst` file in appropriate directory
2. Add to relevant `toctree` in parent file
3. Build and verify

### Docstring Style

Use NumPy-style docstrings:

```python
def function(param1: str, param2: int) -> bool:
    """
    Short description.

    Longer description with more details.

    Parameters
    ----------
    param1 : str
        Description of param1.
    param2 : int
        Description of param2.

    Returns
    -------
    bool
        Description of return value.

    Examples
    --------
    >>> function("test", 42)
    True
    """
    pass
```

### Building and Testing

Before committing documentation changes:

1. Build locally: `make html`
2. Check for warnings
3. Verify links: `make linkcheck`
4. Review rendered output

## Automated Builds

Documentation is built automatically via GitHub Actions:

- **On Push**: Builds and deploys to GitHub Pages
- **On PR**: Builds and uploads as artifact
- **Link Checking**: Runs on all commits

See `.github/workflows/docs.yml` for configuration.

## Troubleshooting

### Import Errors

Ensure package is installed:

```bash
pip install -e ".[viz]"
```

### Missing Modules

Install documentation dependencies:

```bash
pip install -r docs/requirements.txt
```

### Build Failures

Clean and rebuild:

```bash
make clean
make html
```

Check Sphinx output for specific errors.

## Documentation Standards

1. **API Reference**: Auto-generated from docstrings
2. **User Guides**: Hand-written tutorials and explanations
3. **Examples**: Complete, runnable code examples
4. **Cross-references**: Use `:doc:`, `:class:`, `:func:` directives
5. **Code Blocks**: Include language specifier (python, bash, json)

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [NumPy Docstring Guide](https://numpydoc.readthedocs.io/en/latest/format.html)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
