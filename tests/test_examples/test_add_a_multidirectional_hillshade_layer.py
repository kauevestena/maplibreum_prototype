"""Test for add-a-multidirectional-hillshade-layer MapLibre example."""

from maplibreum import Map, layers


HILLSHADE_MULTIDIR_SOURCE = {
    "type": "raster-dem",
    "url": "https://demotiles.maplibre.org/terrain-tiles/tiles.json",
    "tileSize": 512,
}


def test_add_a_multidirectional_hillshade_layer():
    """Confirm multidirectional hillshade paint options render."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-113.57, 37.07],
        zoom=11,
    )
    m.add_source("terrain-dem", HILLSHADE_MULTIDIR_SOURCE)

    hillshade_layer = layers.HillshadeLayer(
        id="multidirectional-hillshade",
        source="terrain-dem",
        paint={
            "hillshade-exaggeration": 0.6,
            "hillshade-illumination-direction": 335,
            "hillshade-highlight-color": "#fff3b0",
            "hillshade-shadow-color": "#3d2b1f",
        },
    )
    m.add_layer(hillshade_layer.to_dict())

    html = m.render()
    assert "hillshade-illumination-direction" in html
    assert "hillshade-highlight-color" in html
    assert len(m.layers) == 1
