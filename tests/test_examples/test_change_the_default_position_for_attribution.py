"""Test for the change-the-default-position-for-attribution example."""

from maplibreum.core import Map


def test_attribution_control_custom_position():
    """Move the attribution control to the top-left corner."""
    m = Map()
    m.add_control("attribution", position="top-left")

    html = m.render()
    expected = 'map.addControl(new maplibregl.AttributionControl({}), "top-left");'
    assert expected in html
