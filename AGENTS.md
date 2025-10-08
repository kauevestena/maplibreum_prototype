# Agent Guidelines for MapLibreum Repository

This document provides guidelines and best practices for AI agents working on the MapLibreum repository.

---

## Repository Organization

### Directory Structure

The repository follows a clear organizational structure to maintain a clean, professional layout:

```
maplibreum_prototype/
├── maplibreum/              # Main Python package
│   ├── __init__.py
│   ├── map.py               # Core Map class
│   ├── templates/           # Jinja2 HTML templates
│   └── ...
├── tests/                   # Test files
│   ├── test_examples/       # MapLibre example conversions
│   └── ...
├── examples/                # User-facing examples
│   ├── *.ipynb             # Jupyter notebooks
│   └── *.html              # Generated HTML files
├── docs/                    # Documentation
│   ├── *.rst               # Sphinx/API docs
│   └── *.md                # Markdown guides
├── development/             # Development artifacts
│   ├── reports/            # Progress reports & session logs
│   ├── javascript_injection_huntdown/  # JS injection tracking
│   └── maplibre_examples/  # MapLibre testing suite
├── playwright_tests/        # Browser-based tests
├── AGENTS.md               # This file - Agent guidelines
├── README.md               # Main documentation
├── CHANGELOG.md            # Version history
├── TODO.md                 # Project roadmap
├── pyproject.toml          # Project configuration
└── ...                     # Other standard config files
```

---

## File Creation Guidelines

### Golden Rule

> **DO NOT create files in the repository root unless:**
> - It's a standard configuration file (e.g., `pyproject.toml`, `setup.cfg`)
> - It's a top-level documentation file (e.g., `CHANGELOG.md`, `LICENSE`)
> - Explicitly instructed by the user

**Keep the repository organized! No more "misc" dumps!**

### Where to Place Different File Types

#### Progress Reports & Session Logs
- **Location:** `development/reports/`
- **Format:** `PROGRESS_REPORT_YYYY_MM_DD_*.md`
- **Purpose:** Document work sessions, milestones, and progress updates

#### JavaScript Injection Tracking
- **Location:** `development/javascript_injection_huntdown/`
- **Files:** Analysis documents, roadmap JSON, tracking files
- **Purpose:** Track and document the JavaScript injection cleanup initiative

#### MapLibre Examples
- **Location:** `development/maplibre_examples/`
- **Purpose:** Testing suite for MapLibre GL JS example coverage
- **Contains:** 
  - `pages/` - Downloaded HTML examples
  - `reproduced_pages/` - Generated test outputs
  - `status.json` - Implementation tracking
  - `scrapping.py` - Example fetcher
  - `README.md` - Instructions for agents

#### Test Files
- **Location:** `tests/` or `tests/test_examples/`
- **Pattern:** `test_*.py`
- **Purpose:** Unit tests and MapLibre example conversions

#### Documentation
- **Location:** `docs/`
- **Types:** API docs (`.rst`), guides (`.md`)
- **Purpose:** Sphinx documentation and user guides

#### User Examples
- **Location:** `examples/`
- **Types:** Jupyter notebooks (`.ipynb`), generated HTML
- **Purpose:** User-facing examples and tutorials

#### Development Artifacts
- **Location:** `development/`
- **Purpose:** Any development-time artifacts that aren't part of the package
- **Examples:** Scripts, analysis documents, temporary data

---

## Template Editing

- Templates live in `maplibreum/templates/` and use Jinja2 syntax.
- Preserve existing placeholders like `{{ variable }}` and Jinja2 control structures.
- Do NOT use Liquid tags (like `{% raw %}` or `{% endraw %}`) in Markdown documentation files because GitHub Pages (Jekyll) will fail to build.
- Keep indentation and spacing consistent; avoid inline scripts unless necessary.

---

## Code Development Best Practices

### Making Changes
- Make minimal, focused changes to accomplish the task
- Test changes thoroughly before committing
- Update documentation when changing public APIs
- Follow existing code style and conventions

### Testing
- Run existing tests before making changes: `pytest tests/`
- Add tests for new functionality
- Update tests when changing behavior
- Ensure all tests pass before committing

### Version Control
- Use clear, descriptive commit messages
- Don't commit temporary files or build artifacts
- Check `.gitignore` to ensure proper exclusions
- Review changes before committing

---

## Working with MapLibre Examples

The `development/maplibre_examples/` directory contains a comprehensive testing suite:

### Workflow
1. Parse `status.json` to identify examples needing conversion
2. Analyze HTML files in `pages/` to extract JavaScript code
3. Create equivalent Python/maplibreum code in `tests/test_examples/`
4. Update `status.json` when implementation is complete
5. Run tests with `pytest tests/test_examples/`

### Key Files
- `development/maplibre_examples/status.json` - Tracks which examples are implemented
- `development/maplibre_examples/pages/` - Original MapLibre HTML examples
- `development/maplibre_examples/README.md` - Detailed instructions for agents

---

## Common Pitfalls to Avoid

1. **Don't create files in the root directory** unless they're standard config/docs
2. **Don't create "misc" or "temp" folders** - use proper subfolders
3. **Don't leave commented-out code** unless there's a good reason
4. **Don't break existing tests** - verify all tests pass
5. **Don't commit build artifacts** - check `.gitignore`
6. **Don't use Liquid template tags in Markdown** - breaks GitHub Pages

---

## Questions or Clarifications?

If you need clarification on where to place a file or how to organize something:
1. Check this document first
2. Look at similar existing files for patterns
3. When in doubt, ask the user for guidance

---

**Remember:** A clean, well-organized repository is easier to maintain and contribute to. Thank you for following these guidelines!
