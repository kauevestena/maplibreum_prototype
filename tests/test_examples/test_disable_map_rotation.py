"""Test for the disable-map-rotation MapLibre example."""

from maplibreum.core import Map


def test_disable_map_rotation_interactions():
    """Replicate the rotation disabling snippet from the gallery example."""
    m = Map(center=[-122.447303, 37.753574], zoom=12)
    m.add_on_load_js(
        "map.dragRotate.disable();\n"
        "map.touchZoomRotate.disableRotation();"
    )

    html = m.render()
    assert "map.dragRotate.disable();" in html
    assert "map.touchZoomRotate.disableRotation();" in html
