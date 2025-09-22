"""Test for add-a-vector-tile-source MapLibre example."""

from maplibreum import Map, layers, sources


def test_add_a_vector_tile_source():
    """Attach a vector tile source and style it with a line layer."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-77.0323, 38.9131],
        zoom=12,
    )

    vector_source = sources.VectorSource(
        tiles="https://demotiles.maplibre.org/tiles/{z}/{x}/{y}.pbf",
        min_zoom=0,
        max_zoom=14,
        attribution="Demo",
    )
    m.add_source("custom-vector", vector_source)

    vector_layer = layers.LineLayer(
        id="vector-rivers",
        source="custom-vector",
        source_layer="waterway",
        layout={"line-join": "round", "line-cap": "round"},
        paint={"line-color": "#ff69b4", "line-width": 1.2},
    )
    m.add_layer(vector_layer.to_dict())

    html = m.render()
    assert '"type": "vector"' in html
    assert "ff69b4" in html
    assert "tiles" in html
    assert len(m.layers) == 1
    definition = m.sources[0]["definition"]
    assert definition["attribution"] == "Demo"
