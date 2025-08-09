# Repository Guidelines

## Coding Style
- Follow [PEP 8](https://peps.python.org/pep-0008/) for all Python code.
- Use 4 spaces per indentation level.
- Group imports into standard library, third-party, and local sections.

## Testing
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
