from maplibreum import Map
from maplibreum.expressions import get, interpolate
from maplibreum.layers import FillExtrusionLayer

MAP_STYLE = {
    "version": 8,
    "sources": {
        "openfreemap": {
            "url": "https://tiles.openfreemap.org/planet",
            "type": "vector",
        }
    },
    "layers": [],
}


def test_set_center_point_above_ground():
    m = Map(
        map_style=MAP_STYLE,
        center=[-74.01318, 40.713],
        zoom=15.5,
        pitch=85,
        bearing=-17.6,
        center_clamped_to_ground=False,
        elevation=541,
        map_options={"maxPitch": 105, "minZoom": 13},
    )

    buildings_layer = FillExtrusionLayer(
        id="3d-buildings",
        source="openfreemap",
        source_layer="building",
        min_zoom=13,
        filter=["!=", ["get", "hide_3d"], True],
        paint={
            "fill-extrusion-color": [
                "interpolate",
                ["linear"],
                ["get", "render_height"],
                0,
                "lightgray",
                200,
                "royalblue",
                400,
                "lightblue",
            ],
            "fill-extrusion-height": [
                "interpolate",
                ["linear"],
                ["zoom"],
                13,
                0,
                14,
                ["get", "render_height"],
            ],
            "fill-extrusion-base": [
                "case",
                [">=", ["get", "zoom"], 16],
                ["get", "render_min_height"],
                0,
            ],
        },
    )

    m.add_layer(buildings_layer)

    html_data = m.render()
    assert '"centerClampedToGround": false' in html_data
    assert '"elevation": 541' in html_data