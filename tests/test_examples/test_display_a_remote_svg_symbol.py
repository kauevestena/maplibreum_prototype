from maplibreum import Map, layers


def test_display_a_remote_svg_symbol():
    """Remote SVG icons should be loaded via map.loadImage before usage."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=1,
    )

    m.add_image(
        "maplibre-logo",
        url="https://maplibre.org/maplibre-gl-js/docs/assets/logo.svg",
    )

    m.add_source(
        "point",
        {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [0, 0]},
                    }
                ],
            },
        },
    )

    symbol_layer = layers.SymbolLayer(
        id="svg-symbol",
        source="point",
        layout={
            "icon-image": "maplibre-logo",
            "icon-overlap": "always",
            "text-overlap": "always",
        },
    )
    m.add_layer(symbol_layer.to_dict())

    html = m.render()

    assert "map.loadImage" in html
    assert "logo.svg" in html
    assert "svg-symbol" in html
    assert len(m.layers) == 1
