"""Test for change-building-color-based-on-zoom-level MapLibre example."""

from maplibreum import Map, layers


def test_change_building_color_based_on_zoom_level():
    """Use zoom-based expressions to tint building extrusions."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-73.985664, 40.748514],
        zoom=15,
    )

    building_layer = layers.FillExtrusionLayer(
        id="3d-buildings",
        source="composite",
        source_layer="building",
        minzoom=15,
        paint={
            "fill-extrusion-color": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                "#aaa",
                16,
                "#f08",
                17,
                "#ffb703",
            ],
            "fill-extrusion-height": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                0,
                17,
                ["get", "render_height"],
            ],
            "fill-extrusion-base": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                0,
                17,
                ["get", "render_min_height"],
            ],
            "fill-extrusion-opacity": 0.8,
        },
    )
    m.add_layer(building_layer.to_dict(), before="waterway-label")

    html = m.render()
    assert "fill-extrusion-color" in html
    assert '"zoom"' in html
    assert "render_height" in html
    assert len(m.layers) == 1
