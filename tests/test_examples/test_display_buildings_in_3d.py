"""Test display buildings in 3D"""

from maplibreum import Map, layers
from maplibreum.sources import VectorSource


def test_display_buildings_in_3d():
    """Replicate the display-buildings-in-3d example."""
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-74.0066, 40.7135],
        zoom=15.5,
        pitch=45,
        bearing=-17.6,
    )

    m.add_source("openfreemap", VectorSource(url="https://tiles.openfreemap.org/planet"))

    fill_extrusion_layer = layers.Layer(
        id="3d-buildings",
        type="fill-extrusion",
        source="openfreemap",
        source_layer="building",
        minzoom=15,
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
                15,
                0,
                16,
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

    m.add_layer(fill_extrusion_layer, before="waterway_line_label")

    # Let the conftest fixture handle the rendering and validation.
    html = m.render()

    assert "waterway_line_label" in html
    assert "3d-buildings" in html
    assert '"fill-extrusion-height"' in html