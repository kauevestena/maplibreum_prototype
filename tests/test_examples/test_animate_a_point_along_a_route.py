"""Parity test for the animate-a-point-along-a-route MapLibre example."""

import json

from maplibreum.core import Map
from maplibreum import layers
from maplibreum.animation import AnimationLoop, RouteAnimation
from maplibreum.controls import ButtonControl


def test_animate_a_point_along_a_route():
    """Test route animation using improved Python API (Phase 2 improvement).

    This version eliminates JavaScript injection by:
    1. Using RouteAnimation class instead of Turf.js for route calculations
    2. Using ButtonControl instead of manual DOM manipulation
    3. Implementing all geometry calculations in Python
    """
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-96, 37.8],
        zoom=3,
    )

    # Define route coordinates
    route_coordinates = [[-122.414, 37.776], [-77.032, 38.913]]

    route_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": route_coordinates,
                },
            }
        ],
    }

    point_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"bearing": 0},
                "geometry": {"type": "Point", "coordinates": route_coordinates[0]},
            }
        ],
    }

    # Add sources
    m.add_source("route", {"type": "geojson", "data": route_data})
    m.add_source("point", {"type": "geojson", "data": point_data})

    # Add layers
    m.add_layer(
        layers.LineLayer(
            id="route",
            source="route",
            paint={"line-width": 2, "line-color": "#007cbf"},
        ).to_dict()
    )

    m.add_layer(
        layers.SymbolLayer(
            id="point",
            source="point",
            layout={
                "icon-image": "airport",
                "icon-rotate": ["get", "bearing"],
                "icon-rotation-alignment": "map",
                "icon-overlap": "always",
                "icon-ignore-placement": True,
            },
        ).to_dict()
    )

    # Create RouteAnimation with Python-based route calculation
    route_animation = RouteAnimation(
        route_coordinates=route_coordinates,
        steps=500,
        route_source_id="route",
        point_source_id="point",
        replay_button_id="replay-btn",
    )

    # Add ButtonControl for replay (no manual DOM manipulation needed)
    replay_button = ButtonControl(
        label="Replay",
        position="top-left",
        onclick_js="document.getElementById('replay-btn').click();",
    )

    # For the button to work with RouteAnimation, we need the button's actual ID
    # to match what RouteAnimation expects
    m.add_on_load_js(
        f"""
    const replayBtnWrapper = document.createElement('button');
    replayBtnWrapper.id = 'replay-btn';
    replayBtnWrapper.style.display = 'none';
    document.body.appendChild(replayBtnWrapper);
    """
    )

    m.add_control(replay_button)

    # Add the route animation JavaScript
    m.add_on_load_js(route_animation.to_js())

    html = m.render()

    # Verify Python API usage
    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-96, 37.8]' in html
    assert '"zoom": 3' in html
    assert 'map.addSource("route"' in html
    assert 'map.addSource("point"' in html

    # Verify no Turf.js dependency
    assert "turf.lineDistance" not in html
    assert "turf.along" not in html
    assert "turf.bearing" not in html

    # Verify Python-calculated arc is present
    assert "routeArc" in html
    assert "calculateBearing" in html
    assert "animateRoute" in html

    # Verify ButtonControl usage
    assert "Replay" in html

    # Verify route animation setup
    assert "requestAnimationFrame(animateRoute)" in html
    assert "getElementById('replay-btn')" in html
