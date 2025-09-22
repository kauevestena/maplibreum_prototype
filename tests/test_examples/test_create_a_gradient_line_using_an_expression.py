"""Test for create-a-gradient-line-using-an-expression MapLibre example."""

from maplibreum import Map, layers


LINE_COORDS = [
    [-122.48369693756104, 37.83381888486939],
    [-122.48348236083984, 37.83317489144141],
    [-122.48339653015138, 37.83270036637107],
    [-122.48356819152832, 37.832056363179625],
    [-122.48404026031496, 37.83114119107971],
    [-122.48404026031496, 37.83049717427869],
]


def test_create_a_gradient_line_using_an_expression():
    """Verify line-gradient expressions and line metrics."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-122.48369693756104, 37.83381888486939],
        zoom=14,
    )

    source_definition = {
        "type": "geojson",
        "lineMetrics": True,
        "data": {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": LINE_COORDS},
        },
    }
    m.add_source("line", source_definition)

    gradient_layer = layers.LineLayer(
        id="gradient-line",
        source="line",
        layout={"line-cap": "round", "line-join": "round"},
        paint={
            "line-width": 14,
            "line-color": "red",
            "line-gradient": [
                "interpolate",
                ["linear"],
                ["line-progress"],
                0,
                "blue",
                0.5,
                "lime",
                1,
                "red",
            ],
        },
    )
    m.add_layer(gradient_layer.to_dict())

    html = m.render()
    assert "line-gradient" in html
    assert "line-progress" in html
    assert "lineMetrics" in html
    assert len(m.layers) == 1
