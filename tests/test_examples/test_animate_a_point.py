"""Parity test for the animate-a-point MapLibre example."""

from maplibreum.core import Map
from maplibreum import layers
from maplibreum.animation import AnimationLoop


def test_animate_a_point():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=2,
    )

    m.add_source(
        "point",
        {
            "type": "geojson",
            "data": {
                "type": "Point",
                "coordinates": [20, 0],
            },
        },
    )

    m.add_layer(
        layers.CircleLayer(
            id="point",
            source="point",
            paint={"circle-radius": 10, "circle-color": "#007cbf"},
        ).to_dict()
    )

    point_loop = AnimationLoop(
        name="animateMarker",
        auto_schedule=False,
        start_immediately=False,
        setup=[
            "const radius = 20;",
            "function pointOnCircle(angle) {",
            "    return {",
            "        'type': 'Point',",
            "        'coordinates': [Math.cos(angle) * radius, Math.sin(angle) * radius]",
            "    };",
            "}",
            "animateMarker(0);",
        ],
        body=[
            "map.getSource('point').setData(pointOnCircle(timestamp / 1000));",
            "requestAnimationFrame(animateMarker);",
        ],
    )

    m.add_animation(point_loop)

    html = m.render()

    assert '"style": "https://demotiles.maplibre.org/style.json"' in html
    assert '"center": [0, 0]' in html
    assert '"zoom": 2' in html
    assert 'map.addSource("point"' in html
    assert 'map.addLayer({"id": "point"' in html
    assert "function pointOnCircle" in html
    assert "map.getSource('point').setData(pointOnCircle" in html
