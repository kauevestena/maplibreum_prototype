"""Parity test for the animate-symbol-to-follow-the-mouse example."""

from maplibreum.core import Map
from maplibreum import layers


def test_animate_symbol_to_follow_the_mouse():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=2,
        map_options={"projection": {"type": "globe"}},
    )

    m.add_control("globe")

    m.add_source(
        "point",
        {
            "type": "geojson",
            "data": {"type": "Point", "coordinates": [0, 0]},
        },
    )

    m.add_layer(
        layers.CircleLayer(
            id="point",
            source="point",
            paint={"circle-radius": 10, "circle-color": "#007cbf"},
        ).to_dict()
    )

    m.add_event_listener(
        "mousemove",
        js="\n".join(
            [
                "const lngLat = event.lngLat.wrap();",
                "const pointSource = map.getSource('point');",
                "if (pointSource && lngLat.lng && lngLat.lat) {",
                "    pointSource.setData({",
                "        'type': 'Point',",
                "        'coordinates': [lngLat.lng, lngLat.lat]",
                "    });",
                "}",
            ]
        ),
    )

    html = m.render()

    assert '"projection": {"type": "globe"}' in html
    assert '"center": [0, 0]' in html
    assert '"zoom": 2' in html
    assert 'map.addSource("point"' in html
    assert "map.getSource('point')" in html
    assert "event.lngLat.wrap" in html
