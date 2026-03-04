"""Manual Playwright checks for rendered MapLibreum controls.

These tests exercise the generated HTML in a browser. They are intentionally excluded from the default pytest run
(``pyproject.toml`` limits automated discovery to the ``tests`` package) so they can
be executed on demand when browser-level validation is required.
"""

from __future__ import annotations

import os
import threading
import tempfile
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

import pytest

pytest.importorskip("pytest_playwright")
pytest.importorskip("playwright")


def test_measurement_tool_e2e(page):
    """End-to-end test for MeasurementTool using Playwright.
    Verifies that points can be clicked and a distance is calculated.
    """
    from maplibreum.core import Map
    from maplibreum.controls import MeasurementTool

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
