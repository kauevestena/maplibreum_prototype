"""Test for display-a-popup-on-click MapLibre example."""

import pytest
from maplibreum.core import Map


def test_display_a_popup_on_click():
    """Test recreating the 'display-a-popup-on-click' MapLibre example.
    
    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://tiles.openfreemap.org/styles/bright',
        center: [-77.04, 38.907],
        zoom: 11.15
    });

    map.on('load', () => {
        map.addSource('places', {
            'type': 'geojson',
            'data': {
                'type': 'FeatureCollection',
                'features': [
                    {
                        'type': 'Feature',
                        'properties': {
                            'description': '<strong>Make it Mount Pleasant</strong><p>...',
                            'icon': 'theatre'
                        },
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [-77.038659, 38.931567]
                        }
                    },
                    // ... more features
                ]
            }
        });
        
        map.addLayer({
            'id': 'places',
            'type': 'symbol',
            'source': 'places',
            'layout': {
                'icon-image': '{icon}',
                'icon-overlap': 'always'
            }
        });

        map.on('click', 'places', (e) => {
            const coordinates = e.features[0].geometry.coordinates.slice();
            const description = e.features[0].properties.description;
            
            new maplibregl.Popup()
                .setLngLat(coordinates)
                .setHTML(description)
                .addTo(map);
        });
    });
    ```
    
    Note: This test demonstrates the data structure and layer creation.
    Full interactive popup functionality would require additional event handling
    implementation in maplibreum.
    """
    # Create the places data from the original example
    places_data = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {
                    'description': '<strong>Make it Mount Pleasant</strong><p><a href="http://www.mtpleasantdc.com/makeitmtpleasant" target="_blank" title="Opens in a new window">Make it Mount Pleasant</a> is a handmade and vintage market and afternoon of live entertainment and kids activities. 12:00-6:00 p.m.</p>',
                    'icon': 'theatre'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-77.038659, 38.931567]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'description': '<strong>Mad Men Season Five Finale Watch Party</strong><p>Head to Lounge 201 (201 Massachusetts Avenue NE) Sunday for a <a href="http://madmens5finale.eventbrite.com/" target="_blank" title="Opens in a new window">Mad Men Season Five Finale Watch Party</a>, complete with 60s costume contest, Mad Men trivia, and retro food and drink. 8:00-11:00 p.m. $10 general admission, $20 admission and two hour open bar.</p>',
                    'icon': 'theatre'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-77.003168, 38.894651]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'description': '<strong>Big Backyard Beach Bash and Wine Fest</strong><p>EatBar (2761 Washington Boulevard Arlington VA) is throwing a <a href="http://tallulaeatbar.ticketleap.com/2012beachblanket/" target="_blank" title="Opens in a new window">Big Backyard Beach Bash and Wine Fest</a> on Saturday, serving up conch fritters, fish tacos and crab sliders, and Red Apron hot dogs. 12:00-3:00 p.m. $25.grill hot dogs.</p>',
                    'icon': 'bar'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-77.090372, 38.881189]
                }
            }
        ]
    }
    
    # Create map with the same configuration as the original example
    m = Map(
        map_style='https://tiles.openfreemap.org/styles/bright',
        center=[-77.04, 38.907],
        zoom=11.15
    )
    
    # Add symbol layer for the places
    m.add_symbol_layer(
        name='places',
        source={'type': 'geojson', 'data': places_data},
        layout={
            'icon-image': '{icon}',  # This uses feature properties
            'icon-overlap': 'always'
        }
    )
    
    # Verify the map was created correctly
    assert m.center == [-77.04, 38.907]
    assert m.zoom == 11.15
    assert m.map_style == 'https://tiles.openfreemap.org/styles/bright'
    
    # Verify the symbol layer was added
    assert len(m.layers) == 1  # Should have one symbol layer
    assert len(m.sources) == 1  # Should have one source
    
    # Verify the layer properties
    symbol_layer = m.layers[0]
    assert symbol_layer['definition']['type'] == 'symbol'
    assert symbol_layer['definition']['id'] == 'places'
    assert symbol_layer['definition']['layout']['icon-image'] == '{icon}'
    assert symbol_layer['definition']['layout']['icon-overlap'] == 'always'
    
    # Verify the source contains the correct GeoJSON data
    places_source = m.sources[0]
    assert places_source['definition']['type'] == 'geojson'
    assert places_source['definition']['data']['type'] == 'FeatureCollection'
    assert len(places_source['definition']['data']['features']) == 3
    
    # Verify first feature
    first_feature = places_source['definition']['data']['features'][0]
    assert first_feature['properties']['icon'] == 'theatre'
    assert 'Make it Mount Pleasant' in first_feature['properties']['description']
    assert first_feature['geometry']['coordinates'] == [-77.038659, 38.931567]
    
    # Verify the HTML renders correctly
    html = m.render()
    assert 'tiles.openfreemap.org/styles/bright' in html
    assert 'Make it Mount Pleasant' in html
    assert 'theatre' in html
    assert '{icon}' in html  # The property expression


def test_display_a_popup_on_click_with_click_handler():
    """Test the popup-on-click functionality using maplibreum's event system.
    
    This demonstrates how you might implement similar functionality using
    maplibreum's current event handling capabilities.
    """
    # Create map and places data (simplified for this test)
    m = Map(
        map_style='https://tiles.openfreemap.org/styles/bright',
        center=[-77.04, 38.907],
        zoom=11.15
    )
    
    # Add a single place with a popup that can be triggered
    places_data = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {
                    'description': '<strong>Test Location</strong><p>This is a test location for popup functionality.</p>',
                    'icon': 'theatre'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-77.038659, 38.931567]
                }
            }
        ]
    }
    
    # Add symbol layer
    m.add_symbol_layer(
        name='places',
        source={'type': 'geojson', 'data': places_data},
        layout={
            'icon-image': '{icon}',
            'icon-overlap': 'always'
        }
    )
    
    # Add a click event handler (this will register a general click handler)
    click_events = []
    
    def handle_click(event_data):
        # In a real implementation, this would filter for clicks on the 'places' layer
        # and extract feature properties to create a popup
        click_events.append(event_data)
    
    m.on_click(handle_click)
    
    # Verify event handler is registered
    html = m.render()
    assert "map.on('click'" in html
    
    # Verify the structure is correct for implementing click-based popups
    assert len(m.layers) == 1
    assert m.layers[0]['definition']['type'] == 'symbol'
    assert len(click_events) == 0  # No events triggered yet in test
    
    # The actual event handling would happen in the browser when the map is rendered