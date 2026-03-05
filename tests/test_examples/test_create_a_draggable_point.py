"""Parity test for the create-a-draggable-point MapLibre example."""

from __future__ import annotations

import json
import textwrap

from maplibreum.core import Map


def test_create_a_draggable_point() -> None:
    """Allow a circle feature to be dragged while updating its coordinates display."""

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
            }
        ],
    }

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=2,
    )

    map_instance.custom_css = textwrap.dedent(
        """
        .maplibreum-draggable-coordinates {
            background: rgba(0, 0, 0, 0.5);
            color: #fff;
            position: absolute;
            bottom: 40px;
            left: 10px;
            padding: 5px 10px;
            margin: 0;
            font-size: 11px;
            line-height: 18px;
            border-radius: 3px;
            display: none;
        }
        """
    ).strip()

    map_instance.add_source("point", {"type": "geojson", "data": geojson})
    map_instance.add_circle_layer(
        "point",
        "point",
        paint={"circle-radius": 10, "circle-color": "#3887be"},
    )

    map_instance.make_draggable(source_id="point", layer_id="point", geojson_data=geojson)

    source_lookup = {source["name"]: source["definition"] for source in map_instance.sources}
    assert "point" in source_lookup
    assert source_lookup["point"]["type"] == "geojson"
    assert source_lookup["point"]["data"] == geojson

    layer_definition = next(layer for layer in map_instance.layers if layer["id"] == "point")
    assert layer_definition["definition"]["type"] == "circle"
    assert layer_definition["definition"]["paint"]["circle-radius"] == 10
    assert layer_definition["definition"]["paint"]["circle-color"] == "#3887be"

    events = {binding.id: binding for binding in map_instance.event_bindings}
    assert "mouseenter@point" in events
    assert "mouseleave@point" in events
    assert "mousedown@point" in events
    assert "touchstart@point" in events
    assert "mousemove" in events
    assert "touchmove" in events
    assert "mouseup" in events
    assert "touchend" in events

    assert "setPaintProperty" in events["mouseenter@point"].js
    assert "details.active" in events["mousedown@point"].js
    assert "dragSource.setData" in events["mousemove"].js
    assert "details.element.style.display = 'block'" in events["mouseup"].js

    html = map_instance.render()
    assert "maplibreum-draggable-coordinates" in html
    assert "window._maplibreumDragDetails_point_point" in html
    assert "Longitude:" in html
