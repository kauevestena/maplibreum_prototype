"""Test for display-a-popup-on-hover example."""

import pytest
from maplibreum import Map


def test_display_a_popup_on_hover():
    """Test displaying popups on hover using symbol layer with tooltips."""
    
    # Create map with same parameters as original
    m = Map(
        map_style='https://tiles.openfreemap.org/styles/bright',
        center=[-77.04, 38.907],
        zoom=11.15
    )
    
    # Add custom marker image
    m.add_image('custom-marker', url='https://maplibre.org/maplibre-gl-js/docs/assets/custom_marker.png')
    
    # GeoJSON data from the original example (subset for testing)
    places_data = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {
                    'description': '<strong>Make it Mount Pleasant</strong><p>Make it Mount Pleasant is a handmade and vintage market and afternoon of live entertainment and kids activities. 12:00-6:00 p.m.</p>'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-77.038659, 38.931567]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'description': '<strong>Mad Men Season Five Finale Watch Party</strong><p>Head to Lounge 201 (201 Massachusetts Avenue NE) Sunday for a Mad Men Season Five Finale Watch Party, complete with 60s costume contest, Mad Men trivia, and retro food and drink. 8:00-11:00 p.m. $10 general admission, $20 admission and two hour open bar.</p>'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-77.003168, 38.894651]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'description': '<strong>Big Backyard Beach Bash and Wine Fest</strong><p>EatBar (2761 Washington Boulevard Arlington VA) is throwing a Big Backyard Beach Bash and Wine Fest on Saturday, serving up conch fritters, fish tacos and crab sliders, and Red Apron hot dogs. 12:00-3:00 p.m. $25.</p>'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-77.090372, 38.881189]
                }
            }
        ]
    }
    
    # Add the places source
    m.add_source('places', places_data)
    
    # Add layer with custom marker
    m.add_layer({
        'id': 'places',
        'type': 'symbol',
        'source': 'places',
        'layout': {
            'icon-image': 'custom-marker',
            'icon-overlap': 'always'
        }
    })
    
    # In the original example, popups are shown on hover using JavaScript events
    # In maplibreum, we simulate this with tooltips on the layer
    # This is a simplified version - the full hover functionality would require
    # more complex event handling that may not be fully supported yet
    
    # Add tooltips to simulate the hover behavior
    for feature in places_data['features']:
        coords = feature['geometry']['coordinates']
        description = feature['properties']['description']
        
        # In a full implementation, we'd use layer events for mouseover/mouseout
        # For now, we'll add markers with tooltips to simulate the behavior
        m.add_marker(
            coordinates=coords,
            tooltip=description,
            color='transparent'  # Make invisible since we have the symbol layer
        )
    
    # Verify the components were added correctly
    source_names = [source['name'] for source in m.sources]
    assert 'places' in source_names
    assert len(m.layers) >= 1
    
    # Check that the places layer exists
    places_layer = None
    for layer in m.layers:
        if layer['id'] == 'places':
            places_layer = layer
            break
    
    assert places_layer is not None
    assert places_layer['definition']['type'] == 'symbol'
    assert places_layer['definition']['layout']['icon-image'] == 'custom-marker'
    assert places_layer['definition']['layout']['icon-overlap'] == 'always'
    
    # Verify image was added
    assert len(m.images) == 1
    assert m.images[0]['id'] == 'custom-marker'
    assert 'custom_marker.png' in m.images[0]['url']
    
    # Verify markers were added (for tooltip simulation)
    assert len(m.markers) == 3
    
    # Generate HTML and verify content
    html = m._repr_html_()
    
    # Should contain the map style and center
    assert 'tiles.openfreemap.org/styles/bright' in html
    assert '-77.04' in html
    assert '38.907' in html
    
    # Should contain places source and layer
    assert 'places' in html
    assert 'custom-marker' in html
    
    # Should contain feature descriptions in tooltips
    assert 'Make it Mount Pleasant' in html
    assert 'Mad Men Season Five Finale Watch Party' in html
    assert 'Big Backyard Beach Bash and Wine Fest' in html


if __name__ == "__main__":
    test_display_a_popup_on_hover()
    print("✓ display-a-popup-on-hover test passed")