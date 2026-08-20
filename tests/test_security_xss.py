"""Regression tests for the marker-HTML XSS fix.

Migrated from the root-level ad hoc script reproduce_xss.py, which was
never collected by pytest (outside testpaths=["tests"]) and never ran in
CI. Marker HTML used to be spliced into a JS template literal
(``el.innerHTML = `${marker.html}`;``), letting an attacker break out of
the literal with backticks/``${...}``. The fix JSON-encodes the value
(``{{ marker.html | tojson }}``) and sanitizes it with DOMPurify before
assignment, so neither payload below should appear unescaped in the
rendered output.
"""

from maplibreum.core import Map, Marker
from maplibreum.markers import DivIcon


def test_marker_html_template_literal_breakout_is_escaped():
    m = Map()
    payload = "${alert('XSS_SUCCESS')}"
    Marker(coordinates=[0, 0], icon=DivIcon(html=payload)).add_to(m)

    html_output = m.render()

    assert "innerHTML = `${alert('XSS_SUCCESS')}`" not in html_output


def test_marker_html_backtick_breakout_is_escaped():
    m = Map()
    payload = "` + alert('XSS_BACKTICK') + `"
    Marker(coordinates=[0, 0], icon=DivIcon(html=payload)).add_to(m)

    html_output = m.render()

    assert "innerHTML = `` + alert('XSS_BACKTICK') + `" not in html_output
    assert "DOMPurify.sanitize(" in html_output
