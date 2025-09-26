"""Test for create-a-basic-fill-layer MapLibre example."""

from maplibreum import Map


def test_create_a_basic_fill_layer():
    """Test creating a basic fill layer with simple polygon.

    This creates a simple rectangular polygon with basic fill styling.

    Equivalent JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [0, 0],
        zoom: 2
    });

    map.on('load', () => {
        map.addSource('polygon', {
            'type': 'geojson',
            'data': {
                'type': 'Feature',
                'properties': {},
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [-20, -20],
                        [20, -20],
                        [20, 20],
                        [-20, 20],
                        [-20, -20]
                    ]]
                }
            }
        });

        map.addLayer({
            'id': 'polygon',
            'type': 'fill',
            'source': 'polygon',
            'paint': {
                'fill-color': '#00ff00',
                'fill-opacity': 0.6
            }
        });
    });
    ```
    """
    # Create map with the same configuration as the example
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json", center=[0, 0], zoom=2
    )

    # Create simple polygon data (square)
    polygon_data = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-20, -20], [20, -20], [20, 20], [-20, 20], [-20, -20]]],
        },
    }

    # Add the GeoJSON source
    m.add_source("polygon", {"type": "geojson", "data": polygon_data})

    # Add the fill layer
    m.add_layer(
        {
            "id": "polygon",
            "type": "fill",
            "source": "polygon",
            "paint": {"fill-color": "#00ff00", "fill-opacity": 0.6},
        }
    )

    # Verify the map was created correctly
    assert m.center == [0, 0]
    assert m.zoom == 2
    assert m.map_style == "https://demotiles.maplibre.org/style.json"

    # Verify the source was added
    assert len(m.sources) == 1
    polygon_source = m.sources[0]
    assert polygon_source["name"] == "polygon"
    assert polygon_source["definition"]["type"] == "geojson"
    assert polygon_source["definition"]["data"] == polygon_data

    # Verify the layer was added
    assert len(m.layers) == 1
    fill_layer = m.layers[0]
    assert fill_layer["id"] == "polygon"
    assert fill_layer["definition"]["type"] == "fill"
    assert fill_layer["definition"]["source"] == "polygon"
    assert fill_layer["definition"]["paint"]["fill-color"] == "#00ff00"
    assert fill_layer["definition"]["paint"]["fill-opacity"] == 0.6

    # Verify the HTML renders correctly
    html = m.render()
    assert "demotiles.maplibre.org/style.json" in html
    assert "fill" in html
    assert "#00ff00" in html
