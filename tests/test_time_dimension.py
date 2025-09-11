import pytest
from maplibreum.core import Map


def test_time_dimension_rendering():
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {"time": "2020-01-01T00:00:00Z"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1, 1]},
                "properties": {"time": "2020-01-01T01:00:00Z"},
            },
        ],
    }

    m = Map()
    m.add_time_dimension(data, {"interval": 500})
    html = m.render()
    assert "leaflet.timedimension.min.js" in html
    assert "2020-01-01T00:00:00Z" in html
    assert "setInterval(tdStep" in html


def test_time_dimension_not_included():
    m = Map()
    html = m.render()
    assert "leaflet.timedimension.min.js" not in html
