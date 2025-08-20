import pytest
from maplibreum.core import Map, GeoJson


def test_fit_bounds_renders_fitBounds():
    m = Map()
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Point", "coordinates": [0, 0]},
            }
        ],
    }
    GeoJson(geojson).add_to(m)
    m.fit_bounds([[-10, -10], [10, 10]], padding=20)
    html = m.render()
    assert "map.fitBounds" in html
