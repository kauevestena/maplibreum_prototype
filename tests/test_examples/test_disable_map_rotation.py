"""Test for the disable-map-rotation MapLibre example."""

from maplibreum.core import Map


def test_disable_map_rotation_interactions():
    """Replicate the rotation disabling snippet from the gallery example (original approach)."""
    m = Map(center=[-122.447303, 37.753574], zoom=12)
    m.add_on_load_js(
        "map.dragRotate.disable();\n"
        "map.touchZoomRotate.disableRotation();"
    )

    html = m.render()
    assert "map.dragRotate.disable();" in html
    assert "map.touchZoomRotate.disableRotation();" in html


def test_disable_map_rotation_with_python_api():
    """Test disabling rotation using the new Python API (Phase 1 improvement)."""
    
    m = Map(center=[-122.447303, 37.753574], zoom=12)
    
    # Use the new disable_rotation method instead of JavaScript injection
    m.disable_rotation()
    
    html = m.render()
    
    # Verify the same JavaScript is generated, but through the Python API
    assert "map.dragRotate.disable();" in html
    assert "map.touchZoomRotate.disableRotation();" in html
    assert "map.keyboard.disableRotation();" in html


def test_disable_map_rotation_selective():
    """Test selectively disabling rotation controls."""
    
    m = Map(center=[-122.447303, 37.753574], zoom=12)
    
    # Only disable drag rotation, keep touch and keyboard
    m.disable_rotation(drag_rotate=True, touch_zoom_rotate=False, keyboard_rotate=False)
    
    html = m.render()
    
    # Should only have drag rotation disabled
    assert "map.dragRotate.disable();" in html
    assert "map.touchZoomRotate.disableRotation();" not in html
    assert "map.keyboard.disableRotation();" not in html


def test_disable_map_rotation_map_options():
    """Test using map_options for rotation control (alternative approach)."""
    
    # This demonstrates how to use the existing map_options parameter
    # for more fine-grained control
    m = Map(
        center=[-122.447303, 37.753574], 
        zoom=12,
        map_options={
            "interactive": True,
            "bearingSnap": 0,  # Disable bearing snap to prevent rotation snap
        }
    )
    
    # Still need to disable the rotation handlers
    m.disable_rotation(drag_rotate=True, touch_zoom_rotate=True)
    
    html = m.render()
    
    # Verify map options are applied
    assert '"bearingSnap": 0' in html
    assert '"interactive": true' in html
    
    # Verify rotation is still disabled
    assert "map.dragRotate.disable();" in html
    assert "map.touchZoomRotate.disableRotation();" in html
