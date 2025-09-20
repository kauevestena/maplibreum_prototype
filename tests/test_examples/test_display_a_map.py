"""Test for display-a-map MapLibre example."""

import pytest
from maplibreum.core import Map


def test_display_a_map():
    """Test recreating the 'display-a-map' MapLibre example.
    
    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map', // container id
        style: 'https://demotiles.maplibre.org/style.json', // style URL
        center: [0, 0], // starting position [lng, lat]
        zoom: 1, // starting zoom
        maplibreLogo: true
    });
    ```
    """
    # Create map with the same configuration as the original example
    m = Map(
        map_style='https://demotiles.maplibre.org/style.json',
        center=[0, 0],
        zoom=1
    )
    
    # Verify the map was created correctly
    assert m.center == [0, 0]
    assert m.zoom == 1
    assert m.map_style == 'https://demotiles.maplibre.org/style.json'
    
    # Verify no additional layers or popups were added (just basic map)
    assert len(m.layers) == 0  # No additional layers
    assert len(m.popups) == 0  # No popups
    assert len(m.sources) == 0  # No additional sources
    
    # Verify the HTML renders correctly
    html = m.render()
    assert 'demotiles.maplibre.org/style.json' in html
    assert '"center": [0, 0]' in html
    assert '"zoom": 1' in html