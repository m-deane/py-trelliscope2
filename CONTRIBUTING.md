# Contributing to py-trelliscope

Thank you for your interest in contributing to py-trelliscope! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize the project's goals

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing others' private information
- Unethical or unprofessional conduct

---

## Getting Started

### Ways to Contribute

1. **Report Bugs**: Open an issue with reproduction steps
2. **Suggest Features**: Propose new functionality or improvements
3. **Fix Issues**: Pick up issues labeled `good first issue` or `help wanted`
4. **Improve Documentation**: Fix typos, clarify explanations, add examples
5. **Write Tests**: Increase test coverage
6. **Review Pull Requests**: Provide feedback on open PRs

### Before Contributing

1. **Check Existing Issues**: Avoid duplicates by searching existing issues
2. **Discuss Large Changes**: Open an issue to discuss major changes before implementing
3. **Read Documentation**: Familiarize yourself with the [Architecture Guide](docs/architecture.md)

---

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (conda or venv)

### Installation

1. **Fork and Clone**

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/py-trelliscope2.git
cd py-trelliscope2
```

2. **Create Virtual Environment**

```bash
# Using conda (recommended)
conda create -n py-trelliscope python=3.9
conda activate py-trelliscope

# Or using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install in Development Mode**

```bash
pip install -e ".[dev]"
```

This installs:
- py-trelliscope in editable mode
- Development dependencies (pytest, pytest-cov, black, etc.)

4. **Verify Installation**

```bash
pytest
```

All tests should pass.

---

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/issue-123
```

**Branch Naming Conventions**:

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or fixes

### 2. Make Changes

- Write code following [Coding Standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trelliscope --cov-report=html

# Run specific test file
pytest tests/unit/test_display.py

# Run specific test
pytest tests/unit/test_display.py::TestDisplay::test_constructor
```

### 4. Format Code

```bash
# Format with black
black trelliscope/ tests/

# Check with flake8 (if installed)
flake8 trelliscope/ tests/
```

### 5. Commit Changes

```bash
git add .
git commit -m "Clear, concise commit message"
```

**Commit Message Guidelines**:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line: 50 characters or less
- Reference issues: "Fix #123: Brief description"

**Good Examples**:

```
Add CurrencyMeta locale support
Fix #123: Handle null values in metadata CSV
Refactor inference logic for datetime columns
Update API documentation for Display.write()
```

### 6. Push and Create PR

```bash
git push origin feature/my-feature
```

Then open a Pull Request on GitHub.

---

## Coding Standards

### Python Style

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Line Length**: 88 characters (Black's default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings (Black's default)
- **Imports**: One per line, grouped (stdlib, third-party, local)

### Code Formatting

Use [Black](https://github.com/psf/black) for automatic formatting:

```bash
black trelliscope/ tests/
```

Black is opinionated and eliminates style debates.

### Type Hints

Use type hints for all public functions:

```python
def function_name(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """Docstring here."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int) -> bool:
    """Brief one-line description.

    Longer description if needed, explaining what the function does,
    any important details, and usage notes.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When and why this is raised
        KeyError: When and why this is raised

    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

### Naming Conventions

- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Private**: Prefix with `_` (e.g., `_internal_method`)

### Error Handling

- Raise descriptive exceptions
- Include helpful error messages
- Use specific exception types

```python
# Good
if column not in df.columns:
    raise ValueError(
        f"Column '{column}' not found in DataFrame. "
        f"Available columns: {list(df.columns)}"
    )

# Bad
if column not in df.columns:
    raise Exception("Invalid column")
```

---

## Testing

### Test Organization

```
tests/
├── unit/              # Fast, isolated tests
│   ├── test_display.py
│   ├── test_meta_variables.py
│   └── ...
└── integration/       # End-to-end workflow tests
    └── test_basic_workflow.py
```

### Writing Tests

#### Unit Tests

Test individual components in isolation:

```python
import pytest
from trelliscope import Display

class TestDisplay:
    """Tests for Display class."""

    def test_constructor_sets_name(self):
        """Test that constructor sets display name."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        display = Display(df, name="test_display")
        assert display.name == "test_display"

    def test_invalid_name_raises_error(self):
        """Test that invalid name raises ValueError."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        with pytest.raises(ValueError, match="Invalid name"):
            Display(df, name="123invalid")
```

#### Integration Tests

Test complete workflows:

```python
def test_full_workflow():
    """Test complete workflow from DataFrame to output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create data
        df = pd.DataFrame({
            "panel": ["p1", "p2"],
            "value": [10, 20]
        })

        # Create and write display
        output = (
            Display(df, name="test")
            .set_panel_column("panel")
            .infer_metas()
            .write(output_path=Path(tmpdir) / "output")
        )

        # Verify output
        assert output.exists()
        assert (output / "displayInfo.json").exists()
        assert (output / "metadata.csv").exists()
```

### Test Patterns

#### Parametrize for Multiple Cases

```python
@pytest.mark.parametrize("input,expected", [
    ("factor", FactorMeta),
    ("number", NumberMeta),
    ("currency", CurrencyMeta),
])
def test_meta_type_creation(input, expected):
    """Test meta type creation for various types."""
    result = create_meta(input)
    assert isinstance(result, expected)
```

#### Use Fixtures for Reusable Data

```python
@pytest.fixture
def sample_dataframe():
    """Provide sample DataFrame for tests."""
    return pd.DataFrame({
        "panel": ["p1", "p2", "p3"],
        "category": ["A", "B", "C"],
        "value": [10, 20, 30]
    })

def test_with_fixture(sample_dataframe):
    """Test using fixture."""
    display = Display(sample_dataframe, name="test")
    assert len(display.data) == 3
```

#### Temporary Directories for I/O Tests

```python
def test_write_output():
    """Test writing display to disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output = display.write(output_path=tmpdir)
        assert output.exists()
        # Tests automatically clean up tmpdir
```

### Coverage Goals

- **Overall**: 95%+ coverage
- **New Code**: 100% coverage for new features
- **Pull Requests**: Must not decrease coverage

### Running Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=trelliscope --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## Documentation

### Documentation Structure

```
docs/
├── api.md              # API reference
├── architecture.md     # Architecture guide
└── ...

examples/
├── 01_getting_started.ipynb
└── ...

README.md               # Main documentation
CONTRIBUTING.md         # This file
```

### Updating Documentation

**When to Update**:

- Adding new features → Update API docs and examples
- Changing behavior → Update relevant documentation
- Fixing bugs → Update if behavior description was wrong
- Improving code → No docs update needed

**Documentation Standards**:

- Clear, concise language
- Include code examples
- Use proper markdown formatting
- Link to related documentation

### Example Notebooks

Located in `examples/`:

- Use Jupyter notebooks (.ipynb)
- Include narrative explanations
- Show complete workflows
- Include output cells

**Creating New Examples**:

```bash
jupyter notebook examples/
# Create new notebook: XX_descriptive_name.ipynb
# Follow pattern from existing examples
```

---

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Ensure all docs are current
2. **Add Tests**: All new code must have tests
3. **Run Full Test Suite**: `pytest` must pass
4. **Format Code**: Run `black` on all changed files
5. **Write PR Description**: Explain what, why, and how

### PR Description Template

```markdown
## Description
Brief description of changes

## Motivation and Context
Why is this change needed? What problem does it solve?
Fixes #123 (if applicable)

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How was this tested?
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Ran full test suite
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] No decrease in coverage
```

### Review Process

1. **Automated Checks**: CI runs tests and coverage
2. **Code Review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: Maintainer merges PR

### After Merge

- Your contribution will be in the next release
- You'll be credited in release notes
- Consider contributing more!

---

## Release Process

*For maintainers*

### Version Numbering

py-trelliscope uses [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update Version**

```bash
# In setup.py or pyproject.toml
version = "1.2.3"
```

2. **Update CHANGELOG**

Add release notes to `CHANGELOG.md`:

```markdown
## [1.2.3] - 2024-01-15

### Added
- New feature description

### Changed
- Changed behavior description

### Fixed
- Bug fix description
```

3. **Create Release Tag**

```bash
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

4. **Build and Publish**

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

5. **Create GitHub Release**

- Go to GitHub Releases
- Create new release from tag
- Copy changelog content
- Publish release

---

## Questions?

### Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an issue with reproduction steps
- **Feature Requests**: Open an issue with use case description
- **Security Issues**: Email [security contact] privately

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code contributions

---

## Recognition

Contributors are recognized in:

- Release notes
- CONTRIBUTORS file (if maintained)
- GitHub contributor graph

Thank you for contributing to py-trelliscope!
