"""Test for a simple text labels example."""

import pytest
from maplibreum import Map


def test_simple_text_labels():
    """Test adding simple text labels to map features."""
    
    # Create map
    m = Map(
        map_style='https://demotiles.maplibre.org/style.json',
        center=[0, 0],
        zoom=2
    )
    
    # Create GeoJSON data with labeled points
    points_data = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-74.0059, 40.7128]  # New York
                },
                'properties': {
                    'name': 'New York',
                    'type': 'city'
                }
            },
            {
                'type': 'Feature', 
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-0.1276, 51.5074]  # London
                },
                'properties': {
                    'name': 'London',
                    'type': 'city'
                }
            },
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [139.6917, 35.6895]  # Tokyo
                },
                'properties': {
                    'name': 'Tokyo',
                    'type': 'city'
                }
            }
        ]
    }
    
    # Add the source
    m.add_source('cities', points_data)
    
    # Add a circle layer for the points
    m.add_layer({
        'id': 'city-circles',
        'type': 'circle',
        'source': 'cities',
        'paint': {
            'circle-radius': 8,
            'circle-color': '#007cbf',
            'circle-stroke-color': '#ffffff',
            'circle-stroke-width': 2
        }
    })
    
    # Add a symbol layer for text labels
    m.add_layer({
        'id': 'city-labels',
        'type': 'symbol',
        'source': 'cities',
        'layout': {
            'text-field': ['get', 'name'],
            'text-font': ['Open Sans Regular'],
            'text-size': 14,
            'text-offset': [0, 1.5],
            'text-anchor': 'top'
        },
        'paint': {
            'text-color': '#333333',
            'text-halo-color': '#ffffff',
            'text-halo-width': 1
        }
    })
    
    # Verify components were added correctly
    source_names = [source['name'] for source in m.sources]
    assert 'cities' in source_names
    
    # Verify layers were added
    assert len(m.layers) == 2
    
    layer_ids = [layer['id'] for layer in m.layers]
    assert 'city-circles' in layer_ids
    assert 'city-labels' in layer_ids
    
    # Check circle layer
    circle_layer = None
    for layer in m.layers:
        if layer['id'] == 'city-circles':
            circle_layer = layer
            break
    
    assert circle_layer is not None
    assert circle_layer['definition']['type'] == 'circle'
    assert circle_layer['definition']['paint']['circle-color'] == '#007cbf'
    assert circle_layer['definition']['paint']['circle-radius'] == 8
    
    # Check label layer
    label_layer = None
    for layer in m.layers:
        if layer['id'] == 'city-labels':
            label_layer = layer
            break
    
    assert label_layer is not None
    assert label_layer['definition']['type'] == 'symbol'
    assert label_layer['definition']['layout']['text-field'] == ['get', 'name']
    assert label_layer['definition']['layout']['text-size'] == 14
    assert label_layer['definition']['paint']['text-color'] == '#333333'
    
    # Generate HTML and verify content
    html = m._repr_html_()
    
    # Should contain the map style
    assert 'demotiles.maplibre.org/style.json' in html
    
    # Should contain city data
    assert 'New York' in html
    assert 'London' in html
    assert 'Tokyo' in html
    
    # Should contain coordinates
    assert '-74.0059' in html
    assert '40.7128' in html
    
    # Should contain layer properties
    assert '#007cbf' in html  # circle color
    assert '#333333' in html  # text color


if __name__ == "__main__":
    test_simple_text_labels()
    print("✓ simple-text-labels test passed")