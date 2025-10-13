
from maplibreum import Map
from maplibreum import layers


def test_display_a_globe_with_a_fill_extrusion_layer():
    """Confirm globe projection and extrusion paint appear in HTML."""

    m = Map(
        title="Globe extrusion",
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=1.2,
        map_options={"projection": "globe"},
    )

    features = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"height": 150000, "color": "#ff0044"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-120.0, 10.0],
                            [120.0, 10.0],
                            [120.0, -10.0],
                            [-120.0, -10.0],
                            [-120.0, 10.0],
                        ]
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {"height": 450000, "color": "#22ff44"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [10.0, 50.0],
                            [20.0, 50.0],
                            [20.0, 40.0],
                            [10.0, 40.0],
                            [10.0, 50.0],
                        ]
                    ],
                },
            },
        ],
    }

    m.add_source("extrude-polygons", {"type": "geojson", "data": features})

    extrusion_layer = layers.FillExtrusionLayer(
        id="extrude-polygons",
        source="extrude-polygons",
        paint={
            "fill-extrusion-color": ["get", "color"],
            "fill-extrusion-height": ["get", "height"],
            "fill-extrusion-opacity": 0.9,
        },
    )
    m.add_layer(extrusion_layer.to_dict())

    html = m.render()
    assert '"projection": {"name": "globe"}' in html
    assert "fill-extrusion-color" in html
    assert "fill-extrusion-height" in html
