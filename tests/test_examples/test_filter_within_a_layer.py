from maplibreum import Map, layers


def test_filter_within_a_layer():
    """Verify circle layer filter expressions are serialized into the template."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-117, 32],
        zoom=3,
    )

    m.add_source(
        "earthquakes",
        {
            "type": "geojson",
            "data": "https://maplibre.org/maplibre-gl-js/docs/assets/earthquakes.geojson",
        },
    )

    circle_layer = layers.CircleLayer(
        id="earthquakes",
        source="earthquakes",
        paint={"circle-color": "#ff0000"},
        filter=[
            "all",
            [">", ["get", "mag"], 4],
            [">=", ["get", "felt"], 10],
        ],
    )
    m.add_layer(circle_layer.to_dict())

    html = m.render()

    assert "earthquakes.geojson" in html
    assert "\"circle-color\": \"#ff0000\"" in html
    assert "\"filter\": [\"all\"" in html
    assert "\"get\", \"mag\"" in html
    assert len(m.layers) == 1
