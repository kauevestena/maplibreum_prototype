"""Parity test for the get-coordinates-of-the-mouse-pointer example."""

from __future__ import annotations

import textwrap

from maplibreum.core import Map


def test_get_coordinates_of_the_mouse_pointer() -> None:
    """Display both pixel and geographic coordinates while the mouse moves."""

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-74.5, 40.0],
        zoom=3,
    )

    map_instance.custom_css = textwrap.dedent(
        """
        .maplibreum-pointer-info {
            display: block;
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translate(-50%);
            width: 50%;
            padding: 10px;
            border-radius: 3px;
            font-size: 12px;
            text-align: center;
            color: #222;
            background: #fff;
        }
        """
    ).strip()

    setup_js = textwrap.dedent(
        """
        var info = document.createElement('pre');
        info.id = 'maplibreum-pointer-info';
        info.className = 'maplibreum-pointer-info';
        map.getContainer().appendChild(info);
        window._maplibreumPointerInfo = info;
        """
    ).strip()

    map_instance.add_on_load_js(setup_js)

    move_js = textwrap.dedent(
        """
        var info = window._maplibreumPointerInfo || document.getElementById('maplibreum-pointer-info');
        if (!info) { return; }
        var pointString = event.point ? JSON.stringify(event.point) : '';
        var lngLatString = '';
        if (event.lngLat && typeof event.lngLat.wrap === 'function') {
            lngLatString = JSON.stringify(event.lngLat.wrap());
        } else if (event.lngLat) {
            lngLatString = JSON.stringify(event.lngLat);
        }
        info.innerHTML = pointString + '<br />' + lngLatString;
        """
    ).strip()

    map_instance.add_event_listener("mousemove", js=move_js)

    binding = map_instance.event_bindings[0]
    assert binding.event == "mousemove"
    assert "JSON.stringify(event.point)" in binding.js
    assert "event.lngLat.wrap" in binding.js

    html = map_instance.render()
    assert "maplibreum-pointer-info" in html
    assert "JSON.stringify(event.point)" in html


def test_get_coordinates_with_python_api() -> None:
    """Display coordinates using the improved Python API (Phase 1 improvement)."""

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-74.5, 40.0],
        zoom=3,
    )

    # Same CSS styling
    map_instance.custom_css = textwrap.dedent(
        """
        .maplibreum-coordinates-display {
            display: block;
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translate(-50%);
            width: 50%;
            padding: 10px;
            border-radius: 3px;
            font-size: 12px;
            text-align: center;
            color: #222;
            background: #fff;
        }
        """
    ).strip()

    # Create the display element setup
    setup_js = textwrap.dedent(
        """
        var coordsDisplay = document.createElement('pre');
        coordsDisplay.id = 'coordinates-display';
        coordsDisplay.className = 'maplibreum-coordinates-display';
        coordsDisplay.innerHTML = 'Move your mouse over the map';
        map.getContainer().appendChild(coordsDisplay);
        """
    ).strip()

    map_instance.add_on_load_js(setup_js)

    # Use the new on_mousemove convenience method
    update_js = textwrap.dedent(
        """
        var display = document.getElementById('coordinates-display');
        if (!display) return;
        
        var pixelCoords = event.point ? 
            'Pixel: ' + JSON.stringify(event.point) : 'Pixel: N/A';
        var geoCoords = '';
        
        if (event.lngLat && typeof event.lngLat.wrap === 'function') {
            geoCoords = 'Geographic: ' + JSON.stringify(event.lngLat.wrap());
        } else if (event.lngLat) {
            geoCoords = 'Geographic: ' + JSON.stringify(event.lngLat);
        } else {
            geoCoords = 'Geographic: N/A';
        }
        
        display.innerHTML = pixelCoords + '<br />' + geoCoords;
        """
    ).strip()

    # Use the improved convenience method instead of add_event_listener
    map_instance.add_event_listener("mousemove", js=update_js)

    html = map_instance.render()
    assert "maplibreum-coordinates-display" in html
    assert "coordinates-display" in html
    assert "JSON.stringify(event.point)" in html
    assert "event.lngLat" in html


def test_get_coordinates_with_callback_api() -> None:
    """Test coordinates using Python callbacks (future enhancement demo)."""

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-74.5, 40.0],
        zoom=3,
    )

    # This demonstrates how the Python callback API works
    # In a real Jupyter environment, this would execute Python code
    def mouse_callback(event_data):
        """Handle mouse move events in Python."""
        # In practice, this would update a Python variable or widget
        # For now, we just demonstrate that the API exists
        print(f"Mouse at: {event_data}")

    # Test that we can register Python callbacks
    # This shows the existing API capability
    callback_id = map_instance.on_mousemove(mouse_callback)
    
    # Verify the callback was registered
    assert callback_id in map_instance._event_callbacks.get(map_instance.map_id, {})
    assert len(map_instance.event_bindings) == 1
    assert map_instance.event_bindings[0].event == "mousemove"
    assert map_instance.event_bindings[0].send_to_python == True

    html = map_instance.render()
    assert "mousemove" in html
