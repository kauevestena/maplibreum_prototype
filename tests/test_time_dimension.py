from maplibreum.core import Map
from maplibreum.timedimension import TimeDimension


def _timestamped_geojson():
    """Return a simple GeoJSON with time-stamped features."""
    return {
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


def test_time_dimension_wrapper_rendering():
    data = _timestamped_geojson()
    m = Map()
    TimeDimension(data, {"interval": 500}).add_to(m)
    html = m.render()
    assert "leaflet.timedimension.min.js" in html
    assert "2020-01-01T00:00:00Z" in html
    assert "setInterval(tdStep" in html


def test_time_dimension_helper():
    data = _timestamped_geojson()
    m = Map()
    m.add_time_dimension(data, {"interval": 500})
    html = m.render()
    assert "2020-01-01T01:00:00Z" in html


def test_time_dimension_not_included():
    m = Map()
    html = m.render()
    assert "leaflet.timedimension.min.js" not in html

