import pytest

from maplibreum.core import Map
from maplibreum.choropleth import Choropleth


@pytest.fixture
def sample_geojson():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "A",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
                },
            },
            {
                "type": "Feature",
                "id": "B",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]],
                },
            },
        ],
    }


def test_choropleth_color_assignment(sample_geojson):
    m = Map()
    data = {"A": 1, "B": 3}
    Choropleth(sample_geojson, data, colors=["#ff0000", "#00ff00"], legend_title="Test").add_to(m)
    features = m.sources[0]["definition"]["data"]["features"]
    assert features[0]["properties"]["fillColor"] == "#ff0000"
    assert features[1]["properties"]["fillColor"] == "#00ff00"
    paint = m.layers[0]["definition"]["paint"]
    assert paint["fill-color"] == ["get", "fillColor", ["properties"]]


def test_choropleth_legend_rendered(sample_geojson):
    m = Map()
    data = {"A": 1, "B": 3}
    Choropleth(sample_geojson, data, colors=["#ff0000", "#00ff00"], legend_title="My Legend").add_to(m)
    html = m.render()
    assert "maplibreum-legend" in html
    assert "My Legend" in html
