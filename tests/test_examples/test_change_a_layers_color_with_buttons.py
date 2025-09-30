"""Recreate the change-a-layers-color-with-buttons example."""

from __future__ import annotations

import textwrap

from maplibreum import Map
from maplibreum.controls import LayerColorControl


def test_change_a_layers_color_with_buttons() -> None:
    """Allow users to switch fill colors for multiple layers via swatches."""

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

    map_instance.custom_css = textwrap.dedent(
        """
        .maplibreum-layer-overlay {
            font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
            position: absolute;
            top: 10px;
            left: 10px;
            width: 220px;
            background: #fff;
            padding: 12px;
            border-radius: 4px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
        }

        .maplibreum-layer-overlay label {
            font-weight: 600;
            display: block;
            margin-bottom: 6px;
        }

        .maplibreum-layer-overlay select {
            width: 100%;
            margin-bottom: 10px;
        }

        .maplibreum-layer-overlay .swatch-row {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .maplibreum-layer-overlay button.maplibreum-swatch {
            width: 32px;
            height: 20px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }

        .maplibreum-layer-overlay button.maplibreum-swatch:focus {
            outline: none;
        }
        """
    ).strip()

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

    controls_js = textwrap.dedent(
        """
        var overlay = document.createElement('div');
        overlay.id = 'maplibreum-layer-controls';
        overlay.className = 'maplibreum-layer-overlay';

        var label = document.createElement('label');
        label.htmlFor = 'maplibreum-layer-select';
        label.textContent = 'Select layer';
        overlay.appendChild(label);

        var select = document.createElement('select');
        select.id = 'maplibreum-layer-select';
        [
            { id: 'water', title: 'Water' },
            { id: 'building-top', title: 'Buildings' }
        ].forEach(function(entry) {
            var option = document.createElement('option');
            option.value = entry.id;
            option.textContent = entry.title;
            select.appendChild(option);
        });
        overlay.appendChild(select);

        var swatchLabel = document.createElement('label');
        swatchLabel.textContent = 'Choose a color';
        overlay.appendChild(swatchLabel);

        var swatchRow = document.createElement('div');
        swatchRow.className = 'swatch-row';
        overlay.appendChild(swatchRow);

        var colors = %s;

        colors.forEach(function(color) {
            var button = document.createElement('button');
            button.className = 'maplibreum-swatch';
            button.type = 'button';
            button.style.backgroundColor = color;
            button.addEventListener('click', function() {
                var targetLayer = select.value;
                map.setPaintProperty(targetLayer, 'fill-color', color);
            });
            swatchRow.appendChild(button);
        });

        map.getContainer().appendChild(overlay);
        """
    ) % textwrap.dedent(textwrap.indent(str(palette), ""))
    map_instance.add_on_load_js(controls_js.strip())

    assert len(map_instance.layers) == 2
    layer_definitions = {layer["id"]: layer["definition"] for layer in map_instance.layers}
    assert "water" in layer_definitions
    assert "building-top" in layer_definitions
    assert layer_definitions["water"]["filter"] == ["==", ["get", "category"], "water"]
    assert layer_definitions["building-top"]["filter"] == [
        "==",
        ["get", "category"],
        "building",
    ]

    assert map_instance._on_load_callbacks, "Expected on-load JavaScript for button wiring"
    on_load_js = "\n".join(map_instance._on_load_callbacks)
    assert "map.setPaintProperty" in on_load_js
    assert "maplibreum-layer-select" in on_load_js

    html = map_instance.render()
    assert "maplibreum-layer-overlay" in html
    for color in ("#fd8d3c", "#253494"):
        assert color in html


def test_change_a_layers_color_with_python_api() -> None:
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
