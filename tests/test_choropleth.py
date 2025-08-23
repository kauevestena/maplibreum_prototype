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


def test_choropleth_quantile_bins():
    features = []
    for i, fid in enumerate(["A", "B", "C", "D"]):
        coords = [
            [i, i],
            [i, i + 1],
            [i + 1, i + 1],
            [i + 1, i],
            [i, i],
        ]
        features.append(
            {
                "type": "Feature",
                "id": fid,
                "properties": {},
                "geometry": {"type": "Polygon", "coordinates": [coords]},
            }
        )

    geojson = {"type": "FeatureCollection", "features": features}
    m = Map()
    data = {"A": 1, "B": 2, "C": 3, "D": 100}
    colors = ["#111111", "#222222", "#333333", "#444444"]
    Choropleth(geojson, data, colors=colors, color_scale="quantile").add_to(m)

    feature_colors = {
        f["id"]: f["properties"]["fillColor"]
        for f in m.sources[0]["definition"]["data"]["features"]
    }
    assert feature_colors["A"] == "#111111"
    assert feature_colors["B"] == "#222222"
    assert feature_colors["C"] == "#333333"
    assert feature_colors["D"] == "#444444"
