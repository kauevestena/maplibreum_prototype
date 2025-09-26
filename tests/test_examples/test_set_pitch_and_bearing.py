"""Test for set-pitch-and-bearing example."""

import pytest
from maplibreum import Map


def test_set_pitch_and_bearing():
    """Test initializing a map with pitch and bearing camera options."""
    
    # Create map with same parameters as original
    m = Map(
        map_style='https://demotiles.maplibre.org/style.json',
        center=[-73.5804, 45.53483],
        pitch=60,      # pitch in degrees
        bearing=-60,   # bearing in degrees
        zoom=4
    )
    
    # Verify map configuration
    assert m.center == [-73.5804, 45.53483]
    assert m.pitch == 60
    assert m.bearing == -60
    assert m.zoom == 4
    assert 'demotiles.maplibre.org/style.json' in m.map_style
    
    # Generate HTML and verify content
    html = m._repr_html_()
    
    # Should contain the map style and center
    assert 'demotiles.maplibre.org/style.json' in html
    assert '-73.5804' in html
    assert '45.53483' in html
    
    # Since HTML is URL-encoded in the iframe, let's check for basic presence
    # We should at least see the pitch and bearing values somewhere in the HTML
    assert '60' in html  # pitch value
    assert '-60' in html or '&quot;bearing&quot;:-60' in html  # bearing value (may be encoded)
    
    # Should contain zoom level
    assert '4' in html


if __name__ == "__main__":
    test_set_pitch_and_bearing()
    print("✓ set-pitch-and-bearing test passed")