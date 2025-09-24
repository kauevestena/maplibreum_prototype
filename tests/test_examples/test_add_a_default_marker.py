"""Test for add-a-default-marker MapLibre example."""

import pytest
from maplibreum.core import Map


def test_add_a_default_marker():
    """Test recreating the 'add-a-default-marker' MapLibre example.
    
    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [12.550343, 55.665957],
        zoom: 6
    });

    const marker = new maplibregl.Marker()
        .setLngLat([12.550343, 55.665957])
        .addTo(map);
    ```
    """
    # Create map with the same configuration as the original example
    m = Map(
        map_style='https://demotiles.maplibre.org/style.json',
        center=[12.550343, 55.665957],
        zoom=6
    )
    
    # Add a marker at the same location
    m.add_marker(coordinates=[12.550343, 55.665957])
    
    # Verify the map was created correctly
    assert m.center == [12.550343, 55.665957]
    assert m.zoom == 6
    assert m.map_style == 'https://demotiles.maplibre.org/style.json'
    
    # Verify the marker was added using a MapLibre Marker instance
    assert len(m.layers) == 0
    assert len(m.sources) == 0
    assert len(m.popups) == 0  # No popup for default marker
    assert len(m.markers) == 1

    marker_definition = m.markers[0]
    assert marker_definition["coordinates"] == [12.550343, 55.665957]
    assert marker_definition["color"] == "#007cbf"
    
    # Verify the HTML renders correctly
    html = m.render()
    assert 'demotiles.maplibre.org/style.json' in html
    assert '12.550343' in html
    assert '55.665957' in html