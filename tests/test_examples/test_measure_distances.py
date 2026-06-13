"""Parity test for the measure-distances MapLibre example."""

from __future__ import annotations

import json
import textwrap

from maplibreum.core import Map


def test_measure_distances() -> None:
    """Test measurement tool using improved Python API (Phase 2 improvement).

    This version eliminates JavaScript injection by:
    1. Using MeasurementTool class instead of manual setup
    2. Implementing Haversine distance calculation in Python (also generated in JS)
    3. Eliminating Turf.js dependency
    4. Providing a clean Python API for measurement configuration
    """
    from maplibreum.controls import MeasurementTool

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[2.3399, 48.8555],
        zoom=12,
    )

    # Create measurement tool with Python API
    measure_tool = MeasurementTool(
        source_id="measurements",
        points_layer_id="measure-points",
        lines_layer_id="measure-lines",
        units="kilometers",
        point_color="#000",
        line_color="#000",
        point_radius=5,
        line_width=2.5,
    )

    # Add source with initial data
    map_instance.add_source(
        measure_tool.source_id,
        {"type": "geojson", "data": measure_tool.get_initial_data()},
    )

    # Add layers using tool configuration
    map_instance.add_layer(measure_tool.get_points_layer_config())
    map_instance.add_layer(measure_tool.get_lines_layer_config())

    # Add CSS and JavaScript
    map_instance.custom_css = measure_tool.to_css()
    map_instance.add_on_load_js(measure_tool.to_js())

    html = map_instance.render()

    # Verify Python API usage
    assert '"center": [2.3399, 48.8555]' in html
    assert '"zoom": 12' in html
    assert 'map.addSource("measurements"' in html

    # Verify MeasurementTool is present
    assert "maplibreum-distance-container" in html
    assert "Total distance:" in html

    # Verify distance calculation (Haversine)
    assert "haversineDistance" in html
    assert "calculateLineDistance" in html

    # Verify no Turf.js dependency
    assert "@turf/turf" not in html
    assert "turf.length" not in html

    # Verify event handling
    assert "map.on('click'" in html
    assert "map.on('mousemove'" in html
    assert "queryRenderedFeatures" in html

    # Verify cursor change logic
    assert "cursor" in html
    assert "crosshair" in html

    # Verify layers are configured
    assert "measure-points" in html
    assert "measure-lines" in html
