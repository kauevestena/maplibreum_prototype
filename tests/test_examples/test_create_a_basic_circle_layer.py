"""Test for create-a-basic-circle-layer MapLibre example."""

from maplibreum import Map


def test_create_a_basic_circle_layer():
    """Test creating a basic circle layer (simplified version of animate-a-point).
    
    This is a simplified static version of the original 'animate-a-point' example,
    showing just the basic circle layer creation without animation.
    
    Original JavaScript (static version):
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [0, 0],
        zoom: 2
    });

    map.on('load', () => {
        map.addSource('point', {
            'type': 'geojson',
            'data': {
                'type': 'Point',
                'coordinates': [20, 0]
            }
        });

        map.addLayer({
            'id': 'point',
            'source': 'point',
            'type': 'circle',
            'paint': {
                'circle-radius': 10,
                'circle-color': '#007cbf'
            }
        });
    });
    ```
    """
    # Create map with the same configuration as the original example
    m = Map(
        map_style='https://demotiles.maplibre.org/style.json',
        center=[0, 0],
        zoom=2
    )
    
    # Create a simple point geometry
    point_data = {
        'type': 'Point',
        'coordinates': [20, 0]
    }
    
    # Add the GeoJSON source
    m.add_source('point', {
        'type': 'geojson',
        'data': point_data
    })
    
    # Add the circle layer
    m.add_layer({
        'id': 'point',
        'source': 'point',
        'type': 'circle',
        'paint': {
            'circle-radius': 10,
            'circle-color': '#007cbf'
        }
    })
    
    # Verify the map was created correctly
    assert m.center == [0, 0]
    assert m.zoom == 2
    assert m.map_style == 'https://demotiles.maplibre.org/style.json'
    
    # Verify the source was added
    assert len(m.sources) == 1
    point_source = m.sources[0]
    assert point_source['name'] == 'point'
    assert point_source['definition']['type'] == 'geojson'
    assert point_source['definition']['data'] == point_data
    
    # Verify the layer was added
    assert len(m.layers) == 1
    circle_layer = m.layers[0]
    assert circle_layer['id'] == 'point'
    assert circle_layer['definition']['type'] == 'circle'
    assert circle_layer['definition']['source'] == 'point'
    assert circle_layer['definition']['paint']['circle-radius'] == 10
    assert circle_layer['definition']['paint']['circle-color'] == '#007cbf'
    
    # Verify the HTML renders correctly
    html = m.render()
    assert 'demotiles.maplibre.org/style.json' in html
    assert 'circle' in html
    assert '#007cbf' in html