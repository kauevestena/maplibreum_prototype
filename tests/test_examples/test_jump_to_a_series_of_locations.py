"""Parity test for the jump-to-a-series-of-locations example."""

import json

from maplibreum.core import Map


def test_jump_to_a_series_of_locations():
    cities = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [100.507, 13.745]}},
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [98.993, 18.793]}},
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [99.838, 19.924]}},
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [102.812, 17.408]}},
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [100.458, 7.001]}},
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [100.905, 12.935]}},
        ],
    }

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[100.507, 13.745],
        zoom=9,
    )

    cities_js = json.dumps(cities)

    m.add_on_load_js(
        "\n".join(
            [
                f"const cities = {cities_js};",
                "cities.features.forEach((city, index) => {",
                "    setTimeout(() => {",
                "        map.jumpTo({center: city.geometry.coordinates});",
                "    }, 2000 * index);",
                "});",
            ]
        )
    )

    html = m.render()

    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [100.507, 13.745]' in html
    assert '"zoom": 9' in html
    assert "setTimeout(() => {" in html
    assert "map.jumpTo({center: city.geometry.coordinates});" in html


def test_jump_to_a_series_of_locations_with_python_api():
    locations = [
        [100.507, 13.745],
        [98.993, 18.793],
        [99.838, 19.924],
        [102.812, 17.408],
        [100.458, 7.001],
        [100.905, 12.935],
    ]

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[100.507, 13.745],
        zoom=9,
    )

    m.jump_to_sequence(locations, interval=1500)

    html = m.render()

    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [100.507, 13.745]' in html
    assert '"zoom": 9' in html
    assert "setTimeout(() => {" in html
    assert "map.jumpTo({center: location});" in html
    assert "}, 1500 * index);" in html
