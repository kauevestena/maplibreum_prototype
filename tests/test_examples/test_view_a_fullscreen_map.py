"""Test for the view-a-fullscreen-map MapLibre example."""

from maplibreum.core import Map


def test_view_a_fullscreen_map_control():
    """Ensure the fullscreen control is added to the map."""
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[11.255, 43.77],
        zoom=13,
    )
    m.add_control("fullscreen")

    html = m.render()
    assert "map.addControl(new maplibregl.FullscreenControl()" in html
