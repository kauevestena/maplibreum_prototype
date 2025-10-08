"""Parity test for the measure-distances MapLibre example."""

from __future__ import annotations

import json
import textwrap

from maplibreum.core import Map


def test_measure_distances() -> None:
    """Allow users to measure distances by clicking points on the map."""

    measurement_data = {"type": "FeatureCollection", "features": []}

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[2.3399, 48.8555],
        zoom=12,
    )

    map_instance.custom_css = textwrap.dedent(
        """
        .maplibreum-distance-container {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1;
        }

        .maplibreum-distance-container > * {
            background-color: rgba(0, 0, 0, 0.5);
            color: #fff;
            font-size: 11px;
            line-height: 18px;
            display: block;
            margin: 0;
            padding: 5px 10px;
            border-radius: 3px;
        }
        """
    ).strip()

    map_instance.add_external_script(
        "https://cdn.jsdelivr.net/npm/@turf/turf@7/turf.min.js"
    )

    map_instance.add_source(
        "measurements", {"type": "geojson", "data": measurement_data}
    )

    map_instance.add_circle_layer(
        "measure-points",
        "measurements",
        paint={"circle-radius": 5, "circle-color": "#000"},
        filter=["in", "$type", "Point"],
    )

    map_instance.add_layer(
        {
            "id": "measure-lines",
            "type": "line",
            "source": "measurements",
            "layout": {"line-cap": "round", "line-join": "round"},
            "paint": {"line-color": "#000", "line-width": 2.5},
            "filter": ["in", "$type", "LineString"],
        }
    )

    setup_js = textwrap.dedent(
        f"""
        var distanceContainer = document.createElement('div');
        distanceContainer.id = 'maplibreum-distance';
        distanceContainer.className = 'maplibreum-distance-container';
        map.getContainer().appendChild(distanceContainer);

        window._maplibreumMeasure = {{
            container: distanceContainer,
            geojson: {json.dumps(measurement_data)},
            line: {{
                type: 'Feature',
                geometry: {{ type: 'LineString', coordinates: [] }}
            }}
        }};

        var measureSource = map.getSource('measurements');
        if (measureSource) {{
            measureSource.setData(window._maplibreumMeasure.geojson);
        }}
        """
    ).strip()

    map_instance.add_on_load_js(setup_js)

    click_js = textwrap.dedent(
        """
        var measure = window._maplibreumMeasure;
        if (!measure) { return; }
        var geojson = measure.geojson;
        var clickedFeatures = map.queryRenderedFeatures(event.point, { layers: ['measure-points'] });

        if (geojson.features.length > 1) {
            geojson.features.pop();
        }

        measure.container.innerHTML = '';

        if (clickedFeatures.length) {
            var targetId = clickedFeatures[0].properties && clickedFeatures[0].properties.id;
            geojson.features = geojson.features.filter(function(point) {
                return point.properties && point.properties.id !== targetId;
            });
        } else if (event.lngLat) {
            geojson.features.push({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [event.lngLat.lng, event.lngLat.lat] },
                properties: { id: String(Date.now()) }
            });
        }

        if (geojson.features.length > 1) {
            measure.line.geometry.coordinates = geojson.features.map(function(point) {
                return point.geometry.coordinates;
            });
            geojson.features.push(measure.line);
            var value = document.createElement('pre');
            if (typeof turf !== 'undefined' && turf.length) {
                var km = turf.length(measure.line);
                value.textContent = 'Total distance: ' + km.toLocaleString() + 'km';
            } else {
                value.textContent = 'Total distance: unavailable';
            }
            measure.container.appendChild(value);
        }

        var source = map.getSource('measurements');
        if (source) {
            source.setData(geojson);
        }
        """
    ).strip()

    map_instance.add_event_listener("click", js=click_js)

    cursor_js = textwrap.dedent(
        """
        var features = map.queryRenderedFeatures(event.point, { layers: ['measure-points'] });
        map.getCanvas().style.cursor = features.length ? 'pointer' : 'crosshair';
        """
    ).strip()

    map_instance.add_event_listener("mousemove", js=cursor_js)

    assert any(
        script["src"] == "https://cdn.jsdelivr.net/npm/@turf/turf@7/turf.min.js"
        for script in map_instance.external_scripts
    )

    bindings = {binding.id: binding for binding in map_instance.event_bindings}
    assert "click" in bindings
    assert "queryRenderedFeatures" in bindings["click"].js
    assert "turf.length" in bindings["click"].js
    assert "cursor" in bindings["mousemove"].js

    html = map_instance.render()
    assert "Total distance:" in html
    assert "@turf/turf" in html


def test_measure_distances_with_python_api() -> None:
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
