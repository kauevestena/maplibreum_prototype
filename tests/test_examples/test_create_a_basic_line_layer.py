"""Test for create-a-basic-line-layer MapLibre example."""

from maplibreum import Map


def test_create_a_basic_line_layer():
    """Test creating a basic line layer with simple styling.

    This creates a simple straight line with basic styling properties.

    Equivalent JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [0, 0],
        zoom: 3
    });

    map.on('load', () => {
        map.addSource('line', {
            'type': 'geojson',
            'data': {
                'type': 'Feature',
                'properties': {},
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-10, -10],
                        [10, 10]
                    ]
                }
            }
        });

        map.addLayer({
            'id': 'line',
            'type': 'line',
            'source': 'line',
            'layout': {
                'line-join': 'round',
                'line-cap': 'round'
            },
            'paint': {
                'line-color': '#ff0000',
                'line-width': 4
            }
        });
    });
    ```
    """
    # Create map with the same configuration as the example
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json", center=[0, 0], zoom=3
    )

    # Create simple line data
    line_data = {
        "type": "Feature",
        "properties": {},
        "geometry": {"type": "LineString", "coordinates": [[-10, -10], [10, 10]]},
    }

    # Add the GeoJSON source
    m.add_source("line", {"type": "geojson", "data": line_data})

    # Add the line layer
    m.add_layer(
        {
            "id": "line",
            "type": "line",
            "source": "line",
            "layout": {"line-join": "round", "line-cap": "round"},
            "paint": {"line-color": "#ff0000", "line-width": 4},
        }
    )

    # Verify the map was created correctly
    assert m.center == [0, 0]
    assert m.zoom == 3
    assert m.map_style == "https://demotiles.maplibre.org/style.json"

    # Verify the source was added
    assert len(m.sources) == 1
    line_source = m.sources[0]
    assert line_source["name"] == "line"
    assert line_source["definition"]["type"] == "geojson"
    assert line_source["definition"]["data"] == line_data

    # Verify the layer was added
    assert len(m.layers) == 1
    line_layer = m.layers[0]
    assert line_layer["id"] == "line"
    assert line_layer["definition"]["type"] == "line"
    assert line_layer["definition"]["source"] == "line"
    assert line_layer["definition"]["paint"]["line-color"] == "#ff0000"
    assert line_layer["definition"]["paint"]["line-width"] == 4
    assert line_layer["definition"]["layout"]["line-join"] == "round"
    assert line_layer["definition"]["layout"]["line-cap"] == "round"

    # Verify the HTML renders correctly
    html = m.render()
    assert "demotiles.maplibre.org/style.json" in html
    assert "line" in html
    assert "#ff0000" in html
