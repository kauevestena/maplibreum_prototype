"""Test for add-a-hillshade-layer MapLibre example."""

from maplibreum import Map, layers


HILLSHADE_SOURCE = {
    "type": "raster-dem",
    "url": "https://demotiles.maplibre.org/terrain-tiles/tiles.json",
    "tileSize": 512,
}


def test_add_a_hillshade_layer():
    """Render hillshade styling with paint/layout options."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[11.39, 47.27],
        zoom=12,
    )
    m.add_source("hillshadeSource", HILLSHADE_SOURCE)

    hillshade_layer = layers.HillshadeLayer(
        id="hillshade",
        source="hillshadeSource",
        layout={"visibility": "visible"},
        paint={
            "hillshade-shadow-color": "#473B24",
            "hillshade-exaggeration": 0.5,
        },
    )
    m.add_layer(hillshade_layer.to_dict())

    assert len(m.layers) == 1
    assert m.layers[0]["definition"]["type"] == "hillshade"

    html = m.render()
    assert "hillshade-shadow-color" in html
    assert "hillshade-exaggeration" in html
    assert "terrain-tiles" in html
