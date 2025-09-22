"""Test for visualize-population-density MapLibre example."""

from maplibreum import Map, layers


def test_visualize_population_density():
    """Ensure nested let/var expressions survive serialization."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-96.7970, 32.7767],
        zoom=5,
    )

    counties = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"population": 2635516, "sq-km": 2357},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-97.1, 32.9],
                            [-96.4, 32.9],
                            [-96.4, 32.5],
                            [-97.1, 32.5],
                            [-97.1, 32.9],
                        ]
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {"population": 1341075, "sq-km": 906},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-96.8, 32.5],
                            [-96.2, 32.5],
                            [-96.2, 32.1],
                            [-96.8, 32.1],
                            [-96.8, 32.5],
                        ]
                    ],
                },
            },
        ],
    }

    m.add_source("population-density", {"type": "geojson", "data": counties})

    fill_color = [
        "let",
        "density",
        ["/", ["get", "population"], ["get", "sq-km"]],
        [
            "interpolate",
            ["linear"],
            ["zoom"],
            5,
            [
                "interpolate",
                ["linear"],
                ["var", "density"],
                274,
                ["to-color", "#edf8e9"],
                1551,
                ["to-color", "#006d2c"],
            ],
            7,
            [
                "interpolate",
                ["linear"],
                ["var", "density"],
                274,
                ["to-color", "#eff3ff"],
                1551,
                ["to-color", "#08519c"],
            ],
        ],
    ]

    density_layer = layers.FillLayer(
        id="population-density",
        source="population-density",
        paint={"fill-color": fill_color, "fill-opacity": 0.7},
    )
    m.add_layer(density_layer.to_dict())

    html = m.render()
    assert '"let"' in html
    assert '"var"' in html
    assert '"to-color"' in html
    assert len(m.layers) == 1
