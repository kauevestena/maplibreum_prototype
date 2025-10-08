## Template Editing
- Templates live in `maplibreum/templates/` and use Jinja2 syntax.
- Preserve existing placeholders like `{{ variable }}` and Jinja2 `{% block %}`.
- Do NOT use `{% block %}` or other unsupported Liquid tags in Markdown documentation files (such as this one) because GitHub Pages (Jekyll) will fail to build.
- Keep indentation and spacing consistent; avoid inline scripts unless necessary.
