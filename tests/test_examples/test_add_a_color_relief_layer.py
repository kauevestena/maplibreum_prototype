"""Test for add-a-color-relief-layer MapLibre example."""

from maplibreum import Map, layers


COLOR_RELIEF_PAINT = {
    "color-relief-color": [
        "interpolate",
        ["linear"],
        ["elevation"],
        400,
        "rgb(4, 0, 108)",
        1129.41,
        "rgb(24, 69, 240)",
        2041.18,
        "rgb(160, 201, 4)",
        2588.24,
        "rgb(251, 194, 14)",
        3500,
        "rgb(215, 5, 13)",
    ]
}


def test_add_a_color_relief_layer():
    """Ensure the custom color relief style renders with correct tokens."""

    style = {
        "version": 8,
        "sources": {
            "terrainSource": {
                "type": "raster-dem",
                "url": "https://demotiles.maplibre.org/terrain-tiles/tiles.json",
                "tileSize": 256,
            }
        },
        "layers": [
            layers.ColorReliefLayer(
                id="color-relief",
                source="terrainSource",
                paint=COLOR_RELIEF_PAINT,
            ).to_dict()
        ],
    }

    m = Map(
        title="Color relief",
        map_style=style,
        center=[11.45, 47.2],
        zoom=10,
        map_options={"hash": True, "renderWorldCopies": False},
    )

    assert m.layers == []
    assert m.map_style["layers"][0]["type"] == "color-relief"

    html = m.render()
    assert "color-relief-color" in html
    assert "terrain-tiles" in html
    assert "interpolate" in html
