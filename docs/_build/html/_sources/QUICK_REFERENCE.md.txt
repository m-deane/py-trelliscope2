# py-trelliscope Documentation - Quick Reference

## 📖 Documentation Links

### Online Documentation
- **Main Docs**: https://your-username.github.io/py-trelliscope2/
- **API Reference**: https://your-username.github.io/py-trelliscope2/api/display.html
- **User Guide**: https://your-username.github.io/py-trelliscope2/user_guide/getting_started.html

### Local Documentation
- **HTML**: `file:///Users/matthewdeane/Documents/Data%20Science/python/_projects/py-trelliscope2/docs/_build/html/index.html`
- **Source**: `docs/` directory

## 🚀 Quick Commands

### Building Documentation

```bash
# Build HTML
cd docs && make html

# Clean and rebuild
cd docs && make clean && make html

# Live preview (auto-reload)
cd docs && make livehtml

# Build PDF
cd docs && make latexpdf

# Check links
cd docs && make linkcheck
```

### Viewing Documentation

```bash
# Open in browser (macOS)
open docs/_build/html/index.html

# Start local server
cd docs/_build/html && python -m http.server 8000
```

## 📚 Documentation Structure

### For Users
- **Getting Started**: `user_guide/getting_started.rst` - Installation and quick start
- **Creating Displays**: `user_guide/creating_displays.rst` - Display configuration
- **Meta Variables**: `user_guide/meta_variables.rst` - Cognostics guide
- **Panel Types**: `user_guide/panel_types.rst` - Panel rendering
- **Examples**: `user_guide/examples.rst` - Complete working examples

### For Developers
- **Display API**: `api/display.rst` - Main Display class
- **Meta API**: `api/meta.rst` - Meta variable types
- **Panels API**: `api/panels.rst` - Panel management
- **Serialization**: `api/serialization.rst` - JSON output
- **Inference**: `api/inference.rst` - Type inference

### Advanced Topics
- **Architecture**: `advanced/architecture.rst` - System design

## 🔧 Common Tasks

### Adding New Documentation Page

1. Create `.rst` file in appropriate directory:
   ```bash
   touch docs/user_guide/new_feature.rst
   ```

2. Add to parent `toctree`:
   ```rst
   .. toctree::
      :maxdepth: 2

      user_guide/new_feature
   ```

3. Build and verify:
   ```bash
   cd docs && make html
   ```

### Updating API Documentation

1. Update docstrings in Python code
2. Rebuild documentation (auto-extracts from docstrings):
   ```bash
   cd docs && make html
   ```

### Fixing Broken Links

1. Run link checker:
   ```bash
   cd docs && make linkcheck
   ```

2. Review output in `_build/linkcheck/output.txt`
3. Fix broken links in source files
4. Rebuild

## 📝 Docstring Style

Use NumPy-style docstrings:

```python
def function(param1: str, param2: int = 10) -> bool:
    """
    One-line summary.

    Longer description with details about what the function does.

    Parameters
    ----------
    param1 : str
        Description of param1.
    param2 : int, optional
        Description of param2, by default 10.

    Returns
    -------
    bool
        Description of return value.

    Examples
    --------
    >>> function("test", 42)
    True

    >>> function("example")
    False

    See Also
    --------
    related_function : Related functionality
    """
    return param1 == "test" and param2 > 20
```

## 🎯 Key Features

### Auto-generated API Reference
- Extracted from docstrings using Sphinx autodoc
- Type hints automatically rendered
- Cross-references to related classes/functions

### User Guides
- Step-by-step tutorials
- Complete working examples
- Progressive difficulty levels

### Search Functionality
- Full-text search across all pages
- Quick navigation to relevant sections

### Mobile Responsive
- Read the Docs theme
- Works on all devices
- Touch-friendly navigation

### Multiple Formats
- HTML (interactive)
- PDF (printable)
- EPUB (e-reader)
- Markdown (plain text)

## 🤖 Automated Builds

### GitHub Actions
- Builds on every push to main
- Deploys to GitHub Pages automatically
- Link validation on all commits

### Workflow File
- `.github/workflows/docs.yml`
- Triggers: push, PR, manual dispatch

## 🐛 Troubleshooting

### Build Fails

**Issue**: Import errors during build
**Solution**:
```bash
pip install -e ".[viz]"
pip install -r docs/requirements.txt
```

**Issue**: Missing modules
**Solution**: Install documentation dependencies:
```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser linkify-it-py
```

### Warnings

**Issue**: Many warnings during build
**Solution**: Most warnings are non-blocking. Focus on errors first.

### Links Not Working

**Issue**: Internal links broken
**Solution**:
1. Use correct syntax: `:doc:`path/to/doc``
2. Check file exists
3. Rebuild: `make clean && make html`

## 📊 Documentation Stats

- **Total Pages**: 20+
- **API References**: 7 modules
- **User Guides**: 5 tutorials
- **Code Examples**: 50+
- **Build Time**: ~15 seconds
- **Output Size**: ~2.5 MB

## 🎓 Best Practices

1. **Write docstrings first** - Before or while coding
2. **Include examples** - Show usage in docstrings
3. **Use type hints** - Automatically documented
4. **Test examples** - Ensure they work
5. **Update regularly** - Keep docs in sync with code
6. **Review locally** - Check formatting before committing

## 🔗 Useful Links

- **Sphinx Documentation**: https://www.sphinx-doc.org/
- **RST Syntax**: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
- **NumPy Docstrings**: https://numpydoc.readthedocs.io/en/latest/format.html
- **Read the Docs Theme**: https://sphinx-rtd-theme.readthedocs.io/

## 📧 Support

- **Issues**: https://github.com/your-username/py-trelliscope2/issues
- **Discussions**: https://github.com/your-username/py-trelliscope2/discussions
- **Documentation Issues**: Tag with `documentation` label

---

**Last Updated**: November 4, 2025
**Documentation Version**: 1.0.0
**py-trelliscope Version**: 0.1.0
