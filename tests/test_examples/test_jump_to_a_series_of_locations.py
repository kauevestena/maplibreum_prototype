"""Parity test for the jump-to-a-series-of-locations example."""

import json

from maplibreum.core import Map


def test_jump_to_a_series_of_locations():
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
