"""Regression test: popup HTML must render literally, not be escaped.

Migrated from development/test_popup_regression.py, which manually drove
the Jinja2 environment against the template instead of calling the public
API, and was never collected by pytest.
"""

from maplibreum.core import Map


def test_popup_html_is_not_escaped():
    m = Map()
    m.add_popup(html="<h1>Hello World!</h1>", coordinates=[0, 0])

    rendered = m.render()

    assert "<h1>Hello World!</h1>" in rendered
    assert "&lt;h1&gt;" not in rendered
