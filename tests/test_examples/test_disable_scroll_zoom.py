"""Test for the disable-scroll-zoom MapLibre example."""

from maplibreum.core import Map


def test_disable_scroll_zoom_option():
    """Ensure scroll wheel zooming is disabled via constructor options."""
    m = Map(map_options={"scrollZoom": False})

    html = m.render()
    assert '"scrollZoom": false' in html
