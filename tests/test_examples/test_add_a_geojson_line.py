"""Test for add-a-geojson-line MapLibre example."""

import pytest
from maplibreum.core import Map


def test_add_a_geojson_line():
    """Test recreating the 'add-a-geojson-line' MapLibre example.
    
    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://tiles.openfreemap.org/styles/bright',
        center: [-122.486052, 37.830348],
        zoom: 15
    });

    map.on('load', () => {
        map.addSource('route', {
            'type': 'geojson',
            'data': {
                'type': 'Feature',
                'properties': {},
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-122.48369693756104, 37.83381888486939],
                        [-122.48348236083984, 37.83317489144141],
                        // ... more coordinates
                        [-122.49378204345702, 37.83368330777276]
                    ]
                }
            }
        });
        map.addLayer({
            'id': 'route',
            'type': 'line',
            'source': 'route',
            'layout': {
                'line-join': 'round',
                'line-cap': 'round'
            },
            'paint': {
                'line-color': '#888',
                'line-width': 8
            }
        });
    });
    ```
    """
    # Create the route coordinates from the original example
    route_coordinates = [
        [-122.48369693756104, 37.83381888486939],
        [-122.48348236083984, 37.83317489144141],
        [-122.48339653015138, 37.83270036637107],
        [-122.48356819152832, 37.832056363179625],
        [-122.48404026031496, 37.83114119107971],
        [-122.48404026031496, 37.83049717427869],
        [-122.48348236083984, 37.829920943955045],
        [-122.48356819152832, 37.82954808664175],
        [-122.48507022857666, 37.82944639795659],
        [-122.48610019683838, 37.82880236636284],
        [-122.48695850372314, 37.82931081282506],
        [-122.48700141906738, 37.83080223556934],
        [-122.48751640319824, 37.83168351665737],
        [-122.48803138732912, 37.832158048267786],
        [-122.48888969421387, 37.83297152392784],
        [-122.48987674713133, 37.83263257682617],
        [-122.49043464660643, 37.832937629287755],
        [-122.49125003814696, 37.832429207817725],
        [-122.49163627624512, 37.832564787218985],
        [-122.49223709106445, 37.83337825839438],
        [-122.49378204345702, 37.83368330777276]
    ]
    
    # Create map with the same configuration as the original example
    m = Map(
        map_style='https://tiles.openfreemap.org/styles/bright',
        center=[-122.486052, 37.830348],
        zoom=15
    )
    
    # Create the GeoJSON line data
    geojson_data = {
        'type': 'Feature',
        'properties': {},
        'geometry': {
            'type': 'LineString',
            'coordinates': route_coordinates
        }
    }
    
    # Add the line layer with styling
    m.add_line_layer(
        name='route',
        source={'type': 'geojson', 'data': geojson_data},
        paint={
            'line-color': '#888',
            'line-width': 8
        },
        layout={
            'line-join': 'round',
            'line-cap': 'round'
        }
    )
    
    # Verify the map was created correctly
    assert m.center == [-122.486052, 37.830348]
    assert m.zoom == 15
    assert m.map_style == 'https://tiles.openfreemap.org/styles/bright'
    
    # Verify the line layer was added
    assert len(m.layers) == 1  # Should have one line layer
    assert len(m.sources) == 1  # Should have one source
    
    # Verify the layer properties
    line_layer = m.layers[0]
    assert line_layer['definition']['type'] == 'line'
    assert line_layer['definition']['id'] == 'route'
    assert line_layer['definition']['paint']['line-color'] == '#888'
    assert line_layer['definition']['paint']['line-width'] == 8
    assert line_layer['definition']['layout']['line-join'] == 'round'
    assert line_layer['definition']['layout']['line-cap'] == 'round'
    
    # Verify the source contains the correct GeoJSON data
    line_source = m.sources[0]
    assert line_source['definition']['type'] == 'geojson'
    assert line_source['definition']['data']['type'] == 'Feature'
    assert line_source['definition']['data']['geometry']['type'] == 'LineString'
    assert len(line_source['definition']['data']['geometry']['coordinates']) == len(route_coordinates)
    assert line_source['definition']['data']['geometry']['coordinates'][0] == route_coordinates[0]
    assert line_source['definition']['data']['geometry']['coordinates'][-1] == route_coordinates[-1]
    
    # Verify the HTML renders correctly
    html = m.render()
    assert 'tiles.openfreemap.org/styles/bright' in html
    assert '#888' in html
    assert 'LineString' in html