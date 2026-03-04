import json
from maplibreum.core import Map


def test_measure_control_snippet():
    m = Map()
    m.add_measure_control()
    html = m.render()
    assert "maplibre-gl-measures.js" in html
    assert "mapbox-gl-draw.css" in html
    assert "new maplibreGLMeasures" in html


def test_measure_features_storage():
    m = Map()
    m.add_measure_control()
    sample = {"type": "FeatureCollection", "features": []}
    Map._store_drawn_features(m.map_id, json.dumps(sample))
    assert m.drawn_features == sample


def test_measurement_tool_haversine_distance():
    from maplibreum.controls import MeasurementTool
    import pytest

    tool_km = MeasurementTool(units="kilometers")
    coords = [[0, 0], [0, 1]] # 1 degree latitude is approx 111.195 km
    dist_km = tool_km._calculate_haversine_distance(coords)
    assert 111.0 < dist_km < 111.5

    tool_mi = MeasurementTool(units="miles")
    dist_mi = tool_mi._calculate_haversine_distance(coords)
    assert 68.0 < dist_mi < 70.0

    tool_m = MeasurementTool(units="meters")
    dist_m = tool_m._calculate_haversine_distance(coords)
    assert 111000.0 < dist_m < 111500.0

    with pytest.warns(UserWarning, match="At least two coordinates are required"):
        assert tool_km._calculate_haversine_distance([[0, 0]]) == 0.0

    with pytest.warns(UserWarning, match="At least two coordinates are required"):
        assert tool_km._calculate_haversine_distance([]) == 0.0


def test_measurement_tool_layer_configs():
    from maplibreum.controls import MeasurementTool

    tool = MeasurementTool()

    initial_data = tool.get_initial_data()
    assert initial_data == {"type": "FeatureCollection", "features": []}

    points_config = tool.get_points_layer_config()
    assert points_config["id"] == "measure-points"
    assert points_config["type"] == "circle"

    lines_config = tool.get_lines_layer_config()
    assert lines_config["id"] == "measure-lines"
    assert lines_config["type"] == "line"


def test_measurement_tool_to_css_and_js():
    from maplibreum.controls import MeasurementTool

    tool = MeasurementTool(units="miles")

    css = tool.to_css()
    assert ".maplibreum-distance-container" in css

    js = tool.to_js()
    assert "distanceContainer.className = 'maplibreum-distance-container';" in js
    assert "units: 'miles'" in js
    assert "unitLabel: 'mi'" in js
