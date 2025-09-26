"""Test for add-custom-icons-with-markers MapLibre example."""

import pytest
from maplibreum.core import Map
from maplibreum.markers import DivIcon


def test_add_custom_icons_with_markers():
    """Test recreating the 'add-custom-icons-with-markers' MapLibre example.
    
    Original JavaScript:
    ```
    const geojson = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {
                    'message': 'Foo',
                    'iconSize': [60, 60]
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-66.324462890625, -16.024695711685304]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'message': 'Bar',
                    'iconSize': [50, 50]
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-61.2158203125, -15.97189158092897]
                }
            },
            {
                'type': 'Feature',
                'properties': {
                    'message': 'Baz',
                    'iconSize': [40, 40]
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-63.29223632812499, -18.28151823530889]
                }
            }
        ]
    };

    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [-65.017, -16.457],
        zoom: 5
    });

    // add markers to map
    geojson.features.forEach((marker) => {
        // create a DOM element for the marker
        const el = document.createElement('div');
        el.className = 'marker';
        el.style.backgroundImage =
            `url(https://picsum.photos/${
                marker.properties.iconSize.join('/')
            }/)`;
        el.style.width = `${marker.properties.iconSize[0]}px`;
        el.style.height = `${marker.properties.iconSize[1]}px`;

        el.addEventListener('click', () => {
            window.alert(marker.properties.message);
        });

        // add marker to map
        new maplibregl.Marker({element: el})
            .setLngLat(marker.geometry.coordinates)
            .addTo(map);
    });
    ```
    """
    # Create map with the same configuration as the original example
    m = Map(
        map_style='https://demotiles.maplibre.org/style.json',
        center=[-65.017, -16.457],
        zoom=5
    )
    
    # Define the same geojson data as the original example
    geojson_features = [
        {
            'properties': {'message': 'Foo', 'iconSize': [60, 60]},
            'coordinates': [-66.324462890625, -16.024695711685304]
        },
        {
            'properties': {'message': 'Bar', 'iconSize': [50, 50]},
            'coordinates': [-61.2158203125, -15.97189158092897]
        },
        {
            'properties': {'message': 'Baz', 'iconSize': [40, 40]},
            'coordinates': [-63.29223632812499, -18.28151823530889]
        }
    ]
    
    # Add custom markers for each feature
    for feature in geojson_features:
        icon_size = feature['properties']['iconSize']
        message = feature['properties']['message']
        coordinates = feature['coordinates']
        
        # Create a custom DivIcon that mimics the original JavaScript
        custom_icon = DivIcon(
            html='',
            class_name='marker'
        )
        
        # Add CSS styling that matches the original
        custom_icon.css = f"""
        .marker {{
            display: block;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            padding: 0;
            background-image: url(https://picsum.photos/{icon_size[0]}/{icon_size[1]}/);
            width: {icon_size[0]}px;
            height: {icon_size[1]}px;
        }}
        """
        
        # Add marker with popup that shows the message
        m.add_marker(
            coordinates=coordinates,
            icon=custom_icon,
            popup=f'<div>{message}</div>'
        )
    
    # Verify the components were added correctly
    assert m.center == [-65.017, -16.457]
    assert m.zoom == 5
    assert m.map_style == 'https://demotiles.maplibre.org/style.json'
    
    # Verify all markers were added
    assert len(m.markers) == 3
    
    # Check each marker
    for i, marker_data in enumerate(m.markers):
        expected_coords = geojson_features[i]['coordinates']
        expected_message = geojson_features[i]['properties']['message']
        
        assert marker_data['coordinates'] == expected_coords
        assert expected_message in marker_data['popup']
        assert marker_data['icon'] is not None
        assert marker_data['icon'].class_name == 'marker'
        
    # Verify the HTML renders correctly  
    html = m.render()
    assert 'demotiles.maplibre.org/style.json' in html
    assert '-65.017' in html
    assert '-16.457' in html
    assert 'Foo' in html
    assert 'Bar' in html
    assert 'Baz' in html
    assert 'picsum.photos' in html