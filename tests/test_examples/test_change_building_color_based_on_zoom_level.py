"""Test for change-building-color-based-on-zoom-level MapLibre example."""

from maplibreum import Map, layers


def test_change_building_color_based_on_zoom_level():
    """Use zoom-based expressions to tint building extrusions."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-73.985664, 40.748514],
        zoom=15,
    )

    buildings = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"render_height": 80, "render_min_height": 0},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-73.9861, 40.7482],
                    [-73.9852, 40.7482],
                    [-73.9852, 40.7488],
                    [-73.9861, 40.7488],
                    [-73.9861, 40.7482],
                ]],
            },
        }],
    }
    m.add_source("buildings", buildings)

    building_layer = layers.FillExtrusionLayer(
        id="3d-buildings",
        source="buildings",
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
    m.add_layer(building_layer.to_dict(), before="geolines-label")

    html = m.render()
    assert "fill-extrusion-color" in html
    assert '"zoom"' in html
    assert "render_height" in html
    assert len(m.layers) == 1
