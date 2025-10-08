# Repository Guidelines

## Repository Organization

### Directory Structure
The repository follows a clean organizational structure to keep development artifacts separate from core code:

```
maplibreum_prototype/
├── maplibreum/           # Core library code
├── tests/                # Test suite
├── examples/             # User-facing example notebooks
├── docs/                 # Documentation
├── development/          # Development artifacts (NOT misc/)
│   ├── reports/          # Progress reports, session logs
│   ├── javascript_injection_huntdown/  # JS injection tracking
│   │   ├── JAVASCRIPT_INJECTION_ANALYSIS.md
│   │   └── javascript_injection_roadmap.json
│   └── maplibre_examples/  # MapLibre examples testing suite
├── playwright_tests/     # Browser-based tests
└── [config files]        # pyproject.toml, setup.cfg, etc.
```

### File Creation Guidelines

**When creating new files, agents MUST place them in appropriate documented subfolders:**

1. **Progress Reports & Session Logs** → `development/reports/`
   - Format: `PROGRESS_REPORT_YYYY_MM_DD_*.md`
   - Session summaries, milestone reports, completion logs

2. **JavaScript Injection Tracking** → `development/javascript_injection_huntdown/`
   - `JAVASCRIPT_INJECTION_ANALYSIS.md` - Analysis document
   - `javascript_injection_roadmap.json` - Progress tracker
   - Related analysis files

3. **MapLibre Examples** → `development/maplibre_examples/`
   - Testing suite for MapLibre GL JS example coverage
   - Scraped pages, status tracking, reproduced examples

4. **Test Files** → `tests/` or `tests/test_examples/`
   - Unit tests: `tests/test_*.py`
   - Example tests: `tests/test_examples/test_*.py`

5. **Documentation** → `docs/`
   - API documentation (`.rst` files)
   - Guides and tutorials (`.md` files)

6. **User Examples** → `examples/`
   - Jupyter notebooks (`.ipynb`)
   - Generated HTML examples (`.html`)

**DO NOT create files in the repository root unless:**
- It's a standard configuration file (e.g., `pyproject.toml`, `README.md`)
- It's a top-level documentation file (e.g., `CHANGELOG.md`, `LICENSE`)
- Explicitly instructed by the user

**Keep the repository organized! No more "misc" dumps!**

## Virtual Environment Setup
- **ALWAYS use the `.venv` virtual environment** for all Python operations
- If `.venv` doesn't exist, create it first:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e .
  pip install pytest jupyter
  ```
- Activate before working:
  ```bash
  source .venv/bin/activate
  ```
- All commands (pytest, pip, python) must run inside `.venv`

## Coding Style
- Follow [PEP 8](https://peps.python.org/pep-0008/) for all Python code.
- Use 4 spaces per indentation level.
- Group imports into standard library, third-party, and local sections.

## Testing
- Activate `.venv` first: `source .venv/bin/activate`
- Run `pytest` from the repository root to execute the test suite.

## Template Editing
- Templates live in `maplibreum/templates/` and use Jinja2 syntax.
- Preserve existing placeholders like `{{ variable }}` and `{% block %}`.
- Keep indentation and spacing consistent; avoid inline scripts unless necessary.

## Dependencies
- Python 3.8+
- Jinja2 >= 3.0
- pytest (for tests)
- jupyter (for examples)

Install with:

```bash
pip install -e .
pip install pytest jupyter
```

## Running Examples
- Example notebooks are located in the `examples/` directory.
- Launch them with:

```bash
jupyter notebook examples
```
