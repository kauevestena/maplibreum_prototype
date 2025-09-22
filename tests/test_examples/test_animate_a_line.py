"""Test coverage for the animate-a-line MapLibre example."""

import json

from maplibreum import Map, layers
from maplibreum.animation import AnimationLoop


def test_animate_a_line_loop():
    m = Map(center=[0, 0], zoom=3)

    line_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": []},
                "properties": {},
            }
        ],
    }

    m.add_source("travel", {"type": "geojson", "data": line_geojson})
    m.add_layer(
        layers.LineLayer(
            id="travel",
            source="travel",
            layout={"line-cap": "round", "line-join": "round"},
            paint={"line-color": "#ed6498", "line-width": 5, "line-opacity": 0.8},
        ).to_dict()
    )

    loop = AnimationLoop(
        name="animateLine",
        variables={"startTime": "performance.now()", "progress": "0"},
        setup=[
            "const speedFactor = 30;",
            f"const geojson = {json.dumps(line_geojson)};",
            "const source = map.getSource('travel');",
            "source.setData(geojson);",
        ],
        body=[
            "progress = performance.now() - startTime;",
            "if (progress > speedFactor * 180) {",
            "    startTime = performance.now();",
            "    geojson.features[0].geometry.coordinates = [];",
            "}",
            "const x = progress / speedFactor;",
            "const y = Math.sin((x * Math.PI) / 90) * 40;",
            "geojson.features[0].geometry.coordinates.push([x, y]);",
            "source.setData(geojson);",
        ],
        handle_name="animation",
        visibility_reset=[
            "startTime = performance.now();",
            "progress = 0;",
        ],
    )

    m.add_animation(loop)
    html = m.render()

    assert "function animateLine" in html
    assert "requestAnimationFrame(animateLine" in html
    assert "map.getSource('travel')" in html
    assert "document.addEventListener('visibilitychange'" in html
