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
