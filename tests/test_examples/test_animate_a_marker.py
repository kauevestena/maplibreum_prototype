"""Parity test for the animate-a-marker MapLibre example."""

from maplibreum.core import Map
from maplibreum.animation import AnimationLoop


def test_animate_a_marker():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=2,
    )

    marker_loop = AnimationLoop(
        name="animateMarker",
        auto_schedule=False,
        start_immediately=False,
        setup=[
            "const marker = new maplibregl.Marker();",
            "const radius = 20;",
            "requestAnimationFrame(animateMarker);",
        ],
        body=[
            "marker.setLngLat([",
            "    Math.cos(timestamp / 1000) * radius,",
            "    Math.sin(timestamp / 1000) * radius",
            "]);",
            "marker.addTo(map);",
            "requestAnimationFrame(animateMarker);",
        ],
    )

    m.add_animation(marker_loop)

    html = m.render()

    assert '"style": "https://demotiles.maplibre.org/style.json"' in html
    assert '"center": [0, 0]' in html
    assert '"zoom": 2' in html
    assert "new maplibregl.Marker()" in html
    assert "Math.cos(timestamp / 1000) * radius" in html
    assert "requestAnimationFrame(animateMarker);" in html
