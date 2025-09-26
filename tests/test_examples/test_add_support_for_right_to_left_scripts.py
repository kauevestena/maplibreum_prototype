"""Test for add-support-for-right-to-left-scripts example."""

import pytest
from maplibreum import Map


def test_add_support_for_right_to_left_scripts():
    """Test enabling right-to-left text support with RTL plugin."""
    
    # Create map with same parameters as original
    m = Map(
        map_style='https://tiles.openfreemap.org/styles/bright',
        center=[44.3763, 33.2788],
        zoom=11
    )
    
    # Enable RTL text plugin similar to the original example
    # The original example uses '@mapbox/mapbox-gl-rtl-text@0.3.0'
    # but maplibreum uses the newer maplibre-gl-rtl-text plugin by default
    m.enable_rtl_text_plugin(
        url='https://unpkg.com/@mapbox/mapbox-gl-rtl-text@0.3.0/dist/mapbox-gl-rtl-text.js',
        lazy=True
    )
    
    # Verify map configuration
    assert m.center == [44.3763, 33.2788]
    assert m.zoom == 11
    assert 'tiles.openfreemap.org/styles/bright' in m.map_style
    
    # Verify RTL text plugin was configured
    assert m.rtl_text_plugin is not None
    assert m.rtl_text_plugin['url'] == 'https://unpkg.com/@mapbox/mapbox-gl-rtl-text@0.3.0/dist/mapbox-gl-rtl-text.js'
    assert m.rtl_text_plugin['lazy'] == True
    
    # Generate HTML and verify content
    html = m._repr_html_()
    
    # Should contain the map style and center
    assert 'tiles.openfreemap.org/styles/bright' in html
    assert '44.3763' in html
    assert '33.2788' in html
    
    # Should contain RTL plugin configuration
    assert 'mapbox-gl-rtl-text' in html
    assert 'setRTLTextPlugin' in html


if __name__ == "__main__":
    test_add_support_for_right_to_left_scripts()
    print("✓ add-support-for-right-to-left-scripts test passed")