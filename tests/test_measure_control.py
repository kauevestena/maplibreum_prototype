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


def test_measurement_tool_e2e(page):
    """End-to-end test for MeasurementTool using Playwright.
    Verifies that points can be clicked and a distance is calculated.
    """
    import os
    import threading
    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
    from maplibreum.core import Map
    from maplibreum.controls import MeasurementTool
    import tempfile

    # Create map with measurement tool
    m = Map(center=[0, 0], zoom=2)
    tool = MeasurementTool()
    m.add_control(tool)

    # Save to a temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "map.html")
        m.save(file_path)

        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=tmpdir, **kwargs)

        # Setup local HTTP server
        server = TCPServer(("", 0), Handler)
        port = server.server_address[1]

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        try:
            # Navigate to the map
            page.goto(f"http://localhost:{port}/map.html")

            # Wait for map to load
            page.wait_for_selector(".maplibregl-canvas")
            page.wait_for_selector(".maplibreum-distance-container", state="attached")

            # The tool should have added a distance container
            container = page.locator(".maplibreum-distance-container")

            # Initially, there should be no distance text
            assert container.inner_text().strip() == ""

            # Simulate clicking two points on the map
            # Use mouse.click to send raw events that mapbox-gl picks up
            map_canvas = page.locator(".maplibregl-canvas")
            box = map_canvas.bounding_box()
            assert box is not None

            # Click point 1
            page.mouse.click(box["x"] + box["width"] / 2 - 50, box["y"] + box["height"] / 2)
            page.wait_for_timeout(200) # give it time to process the first click

            # Click point 2
            page.mouse.click(box["x"] + box["width"] / 2 + 50, box["y"] + box["height"] / 2)
            page.wait_for_timeout(200) # time to calculate distance and update UI

            # Now the distance container should display "Total distance: <something> km"
            text = container.inner_text().strip()
            assert "Total distance:" in text
            assert "km" in text

        finally:
            server.shutdown()
            server.server_close()
