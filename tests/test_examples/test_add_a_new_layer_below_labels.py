"""Test for add-a-new-layer-below-labels MapLibre example."""

from maplibreum import Map, layers


def test_add_a_new_layer_below_labels():
    """Insert a symbol layer before the built-in label layer."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-77.0323, 38.9131],
        zoom=13,
    )

    landmarks = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Lincoln Memorial"},
                "geometry": {"type": "Point", "coordinates": [-77.050, 38.889]},
            },
            {
                "type": "Feature",
                "properties": {"name": "Washington Monument"},
                "geometry": {"type": "Point", "coordinates": [-77.035, 38.8895]},
            },
        ],
    }

    m.add_source("landmarks", {"type": "geojson", "data": landmarks})

    symbol_layer = layers.SymbolLayer(
        id="landmarks",
        source="landmarks",
        layout={
            "icon-image": "star-15",
            "icon-allow-overlap": True,
            "text-field": ["get", "name"],
            "text-offset": [0, 1.25],
        },
        paint={"text-color": "#202", "text-halo-color": "#fff"},
    )
    m.add_layer(symbol_layer.to_dict(), before="waterway-label")

    assert m.layers[0]["before"] == "waterway-label"

    html = m.render()
    assert "waterway-label" in html
    assert "icon-image" in html
    assert "text-field" in html
