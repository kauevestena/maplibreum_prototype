"""Test for add-an-icon-to-the-map MapLibre example."""

import pytest
from maplibreum.core import Map, Icon, Marker


def test_add_an_icon_to_the_map():
    """Test recreating the 'add-an-icon-to-the-map' MapLibre example.
    
    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json'
    });

    map.on('load', async () => {
        image = await map.loadImage('https://upload.wikimedia.org/wikipedia/commons/7/7c/201408_cat.png');
        map.addImage('cat', image.data);
        map.addSource('point', {
            'type': 'geojson',
            'data': {
                'type': 'FeatureCollection',
                'features': [
                    {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [0, 0]
                        }
                    }
                ]
            }
        });
        map.addLayer({
            'id': 'points',
            'type': 'symbol',
            'source': 'point',
            'layout': {
                'icon-image': 'cat',
                'icon-size': 0.25
            }
        });
    });
    ```
    
    Note: This test simulates the functionality since maplibreum doesn't currently
    support dynamic image loading. The icon name 'cat' would need to be pre-loaded
    or handled in the MapLibre frontend.
    """
    # Create map with the same configuration as the original example
    m = Map(map_style='https://demotiles.maplibre.org/style.json')
    
    # Create a symbol layer with a custom icon
    # In a full implementation, the 'cat' icon would be loaded from the external URL
    geojson_data = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [0, 0]
                }
            }
        ]
    }
    
    # Add symbol layer with custom icon
    m.add_symbol_layer(
        name='points',
        source={'type': 'geojson', 'data': geojson_data},
        layout={
            'icon-image': 'cat',
            'icon-size': 0.25
        }
    )
    
    # Verify the map was created correctly
    assert m.map_style == 'https://demotiles.maplibre.org/style.json'
    
    # Verify the symbol layer was added
    assert len(m.layers) == 1  # Should have one symbol layer
    assert len(m.sources) == 1  # Should have one source
    
    # Verify the layer properties
    symbol_layer = m.layers[0]
    assert symbol_layer['definition']['type'] == 'symbol'
    assert symbol_layer['definition']['id'] == 'points'
    assert symbol_layer['definition']['layout']['icon-image'] == 'cat'
    assert symbol_layer['definition']['layout']['icon-size'] == 0.25
    
    # Verify the source contains the correct GeoJSON data
    symbol_source = m.sources[0]
    assert symbol_source['definition']['type'] == 'geojson'
    assert symbol_source['definition']['data']['type'] == 'FeatureCollection'
    assert len(symbol_source['definition']['data']['features']) == 1
    assert symbol_source['definition']['data']['features'][0]['geometry']['coordinates'] == [0, 0]
    
    # Verify the HTML renders correctly
    html = m.render()
    assert 'demotiles.maplibre.org/style.json' in html
    assert 'cat' in html
    assert '0.25' in html


def test_add_an_icon_to_the_map_with_marker_api():
    """Test the same functionality using maplibreum's Marker API with Icon.
    
    This provides an alternative approach that's more consistent with maplibreum's design.
    """
    # Create map
    m = Map(map_style='https://demotiles.maplibre.org/style.json')
    
    # Create a custom icon (simulating the 'cat' icon from the example)
    icon = Icon(icon_image='cat', icon_size=0.25)
    
    # Add marker with custom icon at the same location
    marker = Marker(coordinates=[0, 0], icon=icon)
    marker.add_to(m)
    
    # Verify the map was created correctly
    assert m.map_style == 'https://demotiles.maplibre.org/style.json'
    
    # Verify the marker layer was added
    assert len(m.layers) == 1  # Should have one symbol layer for the marker
    assert len(m.sources) == 1  # Should have one source
    
    # Verify the layer properties
    marker_layer = m.layers[0]
    assert marker_layer['definition']['type'] == 'symbol'
    assert marker_layer['definition']['layout']['icon-image'] == 'cat'
    assert marker_layer['definition']['layout']['icon-size'] == 0.25
    
    # Verify the source contains the correct point data
    marker_source = m.sources[0]
    assert marker_source['definition']['type'] == 'geojson'
    assert marker_source['definition']['data']['features'][0]['geometry']['coordinates'] == [0, 0]
    
    # Verify the HTML renders correctly
    html = m.render()
    assert 'demotiles.maplibre.org/style.json' in html
    assert 'cat' in html