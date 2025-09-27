"""Parity test for the animate-a-point-along-a-route MapLibre example."""

import json

from maplibreum.core import Map
from maplibreum import layers
from maplibreum.animation import AnimationLoop


def test_animate_a_point_along_a_route():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-96, 37.8],
        zoom=3,
    )

    m.custom_css = """
    .maplibreum-animate-route-overlay {
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 1;
    }

    .maplibreum-animate-route-overlay button {
        font: 600 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
        background-color: #3386c0;
        color: #fff;
        display: inline-block;
        margin: 0;
        padding: 10px 20px;
        border: none;
        cursor: pointer;
        border-radius: 3px;
    }

    .maplibreum-animate-route-overlay button:hover {
        background-color: #4ea0da;
    }
    """.strip()

    m.add_external_script(
        "https://www.unpkg.com/turf@2.0.0/turf.min.js",
        attributes={"charset": "utf-8"},
    )

    route_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-122.414, 37.776], [-77.032, 38.913]],
                },
            }
        ],
    }

    point_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Point", "coordinates": [-122.414, 37.776]},
            }
        ],
    }

    m.add_source("route", {"type": "geojson", "data": route_data})
    m.add_source("point", {"type": "geojson", "data": point_data})

    m.add_layer(
        layers.LineLayer(
            id="route",
            source="route",
            paint={"line-width": 2, "line-color": "#007cbf"},
        ).to_dict()
    )

    m.add_layer(
        layers.SymbolLayer(
            id="point",
            source="point",
            layout={
                "icon-image": "airport",
                "icon-rotate": ["get", "bearing"],
                "icon-rotation-alignment": "map",
                "icon-overlap": "always",
                "icon-ignore-placement": True,
            },
        ).to_dict()
    )

    m.add_on_load_js(
        "\n".join(
            [
                "const overlay = document.createElement('div');",
                "overlay.className = 'maplibreum-animate-route-overlay';",
                "const button = document.createElement('button');",
                "button.id = 'replay';",
                "button.textContent = 'Replay';",
                "overlay.appendChild(button);",
                "map.getContainer().appendChild(overlay);",
            ]
        )
    )

    route_js = json.dumps(route_data)
    point_js = json.dumps(point_data)

    loop_setup = [
        f"const route = {route_js};",
        f"const point = {point_js};",
        "const steps = 500;",
        "const lineDistance = turf.lineDistance(route.features[0], 'kilometers');",
        "const arc = [];",
        "for (let i = 0; i < lineDistance; i += lineDistance / steps) {",
        "    const segment = turf.along(route.features[0], i, 'kilometers');",
        "    arc.push(segment.geometry.coordinates);",
        "}",
        "route.features[0].geometry.coordinates = arc;",
        "map.getSource('route').setData(route);",
        "map.getSource('point').setData(point);",
        "const replayButton = document.getElementById('replay');",
        "if (replayButton) {",
        "    replayButton.addEventListener('click', () => {",
        "        point.features[0].geometry.coordinates = route.features[0].geometry.coordinates[0];",
        "        map.getSource('point').setData(point);",
        "        counter = 0;",
        "        animate(0);",
        "    });",
        "}",
        "animate(0);",
    ]

    loop_body = [
        "point.features[0].geometry.coordinates =",
        "    route.features[0].geometry.coordinates[counter];",
        "point.features[0].properties.bearing = turf.bearing(",
        "    turf.point(",
        "        route.features[0].geometry.coordinates[",
        "            counter >= steps ? counter - 1 : counter",
        "        ]",
        "    ),",
        "    turf.point(",
        "        route.features[0].geometry.coordinates[",
        "            counter >= steps ? counter : counter + 1",
        "        ]",
        "    )",
        ");",
        "map.getSource('point').setData(point);",
        "if (counter < steps) {",
        "    requestAnimationFrame(animate);",
        "}",
        "counter = counter + 1;",
    ]

    m.add_animation(
        AnimationLoop(
            name="animate",
            variables={"counter": "0"},
            auto_schedule=False,
            start_immediately=False,
            setup=loop_setup,
            body=loop_body,
        )
    )

    html = m.render()

    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-96, 37.8]' in html
    assert '"zoom": 3' in html
    assert 'map.addSource("route"' in html
    assert 'map.addSource("point"' in html
    assert "turf.lineDistance" in html
    assert "turf.along" in html
    assert "requestAnimationFrame(animate);" in html
    assert "document.getElementById('replay')" in html
