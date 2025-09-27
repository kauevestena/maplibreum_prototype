"""Parity test for the create-a-hover-effect MapLibre example."""

from __future__ import annotations

import textwrap

from maplibreum.core import Map


def test_create_a_hover_effect() -> None:
    """Toggle feature state for hovered polygons using a GeoJSON source."""

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-100.486052, 37.830348],
        zoom=2,
    )

    map_instance.add_source(
        "states",
        {
            "type": "geojson",
            "data": "https://maplibre.org/maplibre-gl-js/docs/assets/us_states.geojson",
        },
    )

    map_instance.add_fill_layer(
        "state-fills",
        "states",
        paint={
            "fill-color": "#627BC1",
            "fill-opacity": [
                "case",
                ["boolean", ["feature-state", "hover"], False],
                1,
                0.5,
            ],
        },
    )

    map_instance.add_layer(
        {
            "id": "state-borders",
            "type": "line",
            "source": "states",
            "layout": {},
            "paint": {"line-color": "#627BC1", "line-width": 2},
        }
    )

    map_instance.add_on_load_js("window._maplibreumHoverStateId = null;")

    move_js = textwrap.dedent(
        """
        var hoveredStateId = window._maplibreumHoverStateId;
        var features = event.features || [];
        if (!features.length) { return; }
        var nextStateId = features[0].id;
        if (hoveredStateId !== null && hoveredStateId !== undefined && hoveredStateId !== nextStateId) {
            map.setFeatureState({ source: 'states', id: hoveredStateId }, { hover: false });
        }
        window._maplibreumHoverStateId = nextStateId;
        map.setFeatureState({ source: 'states', id: nextStateId }, { hover: true });
        """
    ).strip()

    map_instance.add_event_listener(
        "mousemove",
        layer_id="state-fills",
        js=move_js,
    )

    leave_js = textwrap.dedent(
        """
        var hoveredStateId = window._maplibreumHoverStateId;
        if (hoveredStateId !== null && hoveredStateId !== undefined) {
            map.setFeatureState({ source: 'states', id: hoveredStateId }, { hover: false });
        }
        window._maplibreumHoverStateId = null;
        """
    ).strip()

    map_instance.add_event_listener(
        "mouseleave",
        layer_id="state-fills",
        js=leave_js,
    )

    source_lookup = {source["name"]: source["definition"] for source in map_instance.sources}
    assert source_lookup["states"]["data"].endswith("us_states.geojson")

    fill_layer = next(layer for layer in map_instance.layers if layer["id"] == "state-fills")
    assert fill_layer["definition"]["type"] == "fill"
    assert fill_layer["definition"]["paint"]["fill-color"] == "#627BC1"
    assert fill_layer["definition"]["paint"]["fill-opacity"][0] == "case"

    border_layer = next(layer for layer in map_instance.layers if layer["id"] == "state-borders")
    assert border_layer["definition"]["type"] == "line"
    assert border_layer["definition"]["paint"]["line-width"] == 2

    bindings = {binding.id: binding for binding in map_instance.event_bindings}
    assert "mousemove@state-fills" in bindings
    assert "mouseleave@state-fills" in bindings
    assert "setFeatureState" in bindings["mousemove@state-fills"].js
    assert "window._maplibreumHoverStateId" in bindings["mouseleave@state-fills"].js

    html = map_instance.render()
    assert "window._maplibreumHoverStateId" in html
    assert "setFeatureState" in html
