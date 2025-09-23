"""Test for the render-world-copies MapLibre example."""

from maplibreum.core import Map


def test_disable_render_world_copies():
    """Ensure only a single world copy renders by disabling wraparound."""
    m = Map(map_options={"renderWorldCopies": False})

    html = m.render()
    assert '"renderWorldCopies": false' in html
