"""Test for display-a-popup MapLibre example."""

import pytest
from maplibreum.core import Map


def test_display_a_popup():
    """Test recreating the 'display-a-popup' MapLibre example.
    
    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [-96, 37.8],
        zoom: 3
    });

    const popup = new maplibregl.Popup({closeOnClick: false})
        .setLngLat([-96, 37.8])
        .setHTML('<h1>Hello World!</h1>')
        .addTo(map);
    ```
    """
    # Create map with the same configuration as the original example
    m = Map(
        map_style='https://demotiles.maplibre.org/style.json',
        center=[-96, 37.8],
        zoom=3
    )
    
    # Add a popup at the same location with the same content
    m.add_popup(
        html='<h1>Hello World!</h1>',
        coordinates=[-96, 37.8],
        options={'closeOnClick': False}
    )
    
    # Verify the map was created correctly
    assert m.center == [-96, 37.8]
    assert m.zoom == 3
    assert m.map_style == 'https://demotiles.maplibre.org/style.json'
    
    # Verify the popup was added
    assert len(m.popups) == 1  # Should have one popup
    assert len(m.layers) == 0  # No additional layers
    assert len(m.sources) == 0  # No additional sources
    
    # Verify the popup properties
    popup = m.popups[0]
    assert popup['html'] == '<h1>Hello World!</h1>'
    assert popup['coordinates'] == [-96, 37.8]
    assert popup['options']['closeOnClick'] is False
    
    # Verify the HTML renders correctly
    html = m.render()
    assert 'demotiles.maplibre.org/style.json' in html
    assert '<h1>Hello World!</h1>' in html
    assert '[-96, 37.8]' in html
    assert 'closeOnClick' in html