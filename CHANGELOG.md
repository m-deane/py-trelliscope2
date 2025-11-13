# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Production-grade code quality improvements
- Comprehensive type annotations (MyPy 0 errors)
- Modern pyproject.toml packaging (PEP 517/518/621)
- PEP 561 py.typed marker for type information export
- Production readiness audit documentation
- Flake8 configuration (.flake8)
- Comprehensive tool configurations (black, isort, pylint, mypy, pytest)

### Changed
- Migrated from deprecated setup.py to pyproject.toml
- Improved pylint score from 9.17/10 to 9.48/10
- Renamed parameters shadowing built-ins (type→panel_type, format→output_format)
- Auto-formatted all code with black (88-character line length)
- Organized all imports with isort (black profile)

### Fixed
- All 103 flake8 errors resolved (now 0 errors)
- All 35+ mypy type errors resolved (now 0 errors)
- Removed unused imports and variables
- Fixed f-strings without placeholders
- Fixed broad exception catching patterns
- Fixed no-else-raise anti-pattern

### Removed
- Deprecated setup.py file (replaced by pyproject.toml)
- Unused imports and variables

## [0.1.0] - 2024-11-13

### Added
- Core Display class with fluent API
- Meta variable type system (8 types: factor, number, currency, date, time, href, graph, base)
- DataFrame type inference for automatic meta variable detection
- Panel interface abstractions (Local, REST, WebSocket)
- Panel rendering with matplotlib and plotly adapters
- JSON serialization for trelliscopejs-lib viewer compatibility
- Viewer HTML generation and integration
- Multi-display support
- Static export utilities
- Development server with Flask
- Configuration management system
- Comprehensive test suite (unit and integration tests)
- Example notebooks and scripts
- Project documentation (CLAUDE.md, README.md, CONTRIBUTING.md)

### Technical Architecture
- 3-tier hybrid architecture: Python → JSON → JavaScript viewer
- 1-based factor indexing for R compatibility
- File-based and REST API panel sources
- Embedded cogData with separate metadata files
- Compatible with trelliscopejs-lib v0.7.16

[Unreleased]: https://github.com/trelliscope/py-trelliscope2/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/trelliscope/py-trelliscope2/releases/tag/v0.1.0
