"""Test for style-lines-with-a-data-driven-property MapLibre example."""

from maplibreum import Map, layers


def test_style_lines_with_a_data_driven_property():
    """Validate that get expressions survive rendering."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-122.48369693756104, 37.83381888486939],
        zoom=14,
    )

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"color": "#ff5500"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-122.48369693756104, 37.83381888486939],
                        [-122.48348236083984, 37.83317489144141],
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {"color": "#33C9EB"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-122.48356819152832, 37.832056363179625],
                        [-122.48404026031496, 37.83114119107971],
                    ],
                },
            },
        ],
    }

    m.add_source("colored-lines", {"type": "geojson", "data": geojson})

    line_layer = layers.LineLayer(
        id="colored-lines",
        source="colored-lines",
        paint={"line-width": 3, "line-color": ["get", "color"]},
    )
    m.add_layer(line_layer.to_dict())

    html = m.render()
    assert '["get", "color"]' in html
    assert "colored-lines" in html
    assert len(m.layers) == 1
