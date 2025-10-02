"""Unit tests for the Map class."""
from maplibreum.core import Map

def test_animate_camera_around():
    """Test that animate_camera_around adds the correct animation JavaScript."""
    m = Map()
    m.animate_camera_around(period_ms=40000)
    html = m.render()

    assert "function rotateCamera(timestamp)" in html
    assert "map.rotateTo((timestamp * 360 / 40000) % 360, {duration: 0});" in html
    assert "requestAnimationFrame(rotateCamera)" in html