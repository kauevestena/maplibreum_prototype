"""Recreate the change-a-layers-color-with-buttons example."""

from __future__ import annotations

import textwrap

from maplibreum import Map
from maplibreum.controls import LayerColorControl


def test_change_a_layers_color_with_buttons() -> None:
    """Test the same functionality using Python API with LayerColorControl (Phase 2 improvement)."""
    
    features = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"category": "water"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [12.3325, 45.4375],
                            [12.3325, 45.4405],
                            [12.3395, 45.4405],
                            [12.3395, 45.4375],
                            [12.3325, 45.4375],
                        ]
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {"category": "building"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [12.3395, 45.4365],
                            [12.3395, 45.4395],
                            [12.3445, 45.4395],
                            [12.3445, 45.4365],
                            [12.3395, 45.4365],
                        ]
                    ],
                },
            },
        ],
    }

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[12.338, 45.4385],
        zoom=17.4,
    )

    map_instance.add_source("venice-landuse", {"type": "geojson", "data": features})

    map_instance.add_layer(
        {
            "id": "water",
            "type": "fill",
            "paint": {"fill-color": "#41b6c4", "fill-opacity": 0.65},
            "filter": ["==", ["get", "category"], "water"],
        },
        source="venice-landuse",
    )
    map_instance.add_layer(
        {
            "id": "building-top",
            "type": "fill",
            "paint": {"fill-color": "#feb24c", "fill-opacity": 0.85},
            "filter": ["==", ["get", "category"], "building"],
        },
        source="venice-landuse",
    )

    # Define color palette
    palette = [
        "#ffffcc",
        "#a1dab4",
        "#41b6c4",
        "#2c7fb8",
        "#253494",
        "#fed976",
        "#feb24c",
        "#fd8d3c",
        "#f03b20",
        "#bd0026",
    ]

    # Use the new LayerColorControl instead of JavaScript injection
    layer_color_control = LayerColorControl(
        layers={"water": "Water", "building-top": "Buildings"},
        colors=palette,
        position="top-left",
        title="Select layer"
    )
    map_instance.add_control(layer_color_control)

    html = map_instance.render()
    
    # Verify the control is rendered with proper structure
    assert "maplibreum-layer-color-ctrl" in html
    assert "Select layer" in html
    assert "Choose a color" in html
    assert "map.setPaintProperty" in html
    
    # Verify layer definitions are present
    assert "water" in html
    assert "building-top" in html
    
    # Verify colors are in the palette
    for color in ("#fd8d3c", "#253494", "#41b6c4"):
        assert color in html
