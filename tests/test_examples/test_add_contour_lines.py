from maplibreum import Map, layers


def test_add_contour_lines():
    """Ensure multi-layer contour styling is preserved in the rendered HTML."""

    style = {
        "version": 8,
        "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
        "sources": {
            "hillshadeSource": {
                "type": "raster-dem",
                "tiles": [
                    "https://demotiles.maplibre.org/terrain-tiles/{z}/{x}/{y}.png"
                ],
                "tileSize": 512,
                "maxzoom": 12,
            },
            "contourSourceFeet": {
                "type": "vector",
                "tiles": [
                    "https://demotiles.maplibre.org/contours/{z}/{x}/{y}.mvt"
                ],
                "maxzoom": 15,
            },
        },
        "layers": [
            layers.HillshadeLayer(
                id="hills",
                source="hillshadeSource",
                layout={"visibility": "visible"},
                paint={"hillshade-exaggeration": 0.25},
            ).to_dict(),
            layers.LineLayer(
                id="contours",
                source="contourSourceFeet",
                source_layer="contours",
                paint={
                    "line-opacity": 0.5,
                    "line-width": [
                        "match",
                        ["get", "level"],
                        1,
                        1,
                        0.5,
                    ],
                },
            ).to_dict(),
            layers.SymbolLayer(
                id="contour-text",
                source="contourSourceFeet",
                source_layer="contours",
                filter=[">", ["get", "level"], 0],
                paint={
                    "text-halo-color": "white",
                    "text-halo-width": 1,
                },
                layout={
                    "symbol-placement": "line",
                    "text-size": 10,
                    "text-field": [
                        "concat",
                        ["number-format", ["get", "ele"], {}],
                        "'",
                    ],
                    "text-font": ["Noto Sans Bold"],
                },
            ).to_dict(),
        ],
    }

    m = Map(
        map_style=style,
        center=[11.3229, 47.2738],
        zoom=13,
        map_options={"hash": True},
    )

    html = m.render()

    assert m.layers == []
    assert "contourSourceFeet" in html
    assert "hillshade-exaggeration" in html
    assert "line-width" in html and "match" in html
    assert "text-field" in html and "number-format" in html
