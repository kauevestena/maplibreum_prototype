"""Port the filter-symbols-by-text-input example to pytest."""

from __future__ import annotations

import textwrap

from maplibreum import Map
from maplibreum.controls import TextFilterControl


PLACES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"icon": "theatre"},
            "geometry": {"type": "Point", "coordinates": [-77.038659, 38.931567]},
        },
        {
            "type": "Feature",
            "properties": {"icon": "theatre"},
            "geometry": {"type": "Point", "coordinates": [-77.003168, 38.894651]},
        },
        {
            "type": "Feature",
            "properties": {"icon": "bar"},
            "geometry": {"type": "Point", "coordinates": [-77.090372, 38.881189]},
        },
        {
            "type": "Feature",
            "properties": {"icon": "bicycle"},
            "geometry": {"type": "Point", "coordinates": [-77.052477, 38.943951]},
        },
        {
            "type": "Feature",
            "properties": {"icon": "music"},
            "geometry": {"type": "Point", "coordinates": [-77.031706, 38.914581]},
        },
        {
            "type": "Feature",
            "properties": {"icon": "music"},
            "geometry": {"type": "Point", "coordinates": [-77.020945, 38.878241]},
        },
        {
            "type": "Feature",
            "properties": {"icon": "music"},
            "geometry": {"type": "Point", "coordinates": [-77.007481, 38.876516]},
        },
    ],
}


def test_filter_symbols_by_text_input() -> None:
    """Test the same functionality using Python API with TextFilterControl (Phase 2 improvement)."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-77.04, 38.907],
        zoom=11.15,
    )

    map_instance.add_source("places", {"type": "geojson", "data": PLACES})

    unique_icons = sorted({feature["properties"]["icon"] for feature in PLACES["features"]})
    layer_ids = []
    for icon_name in unique_icons:
        layer_id = f"poi-{icon_name}"
        layer_ids.append(layer_id)
        map_instance.add_layer(
            {
                "id": layer_id,
                "type": "symbol",
                "layout": {
                    "icon-image": f"{icon_name}_11",
                    "icon-overlap": "always",
                    "text-field": icon_name,
                    "text-font": ["Noto Sans Regular"],
                    "text-size": 11,
                    "text-transform": "uppercase",
                    "text-letter-spacing": 0.05,
                    "text-offset": [0, 1.5],
                },
                "paint": {
                    "text-color": "#202",
                    "text-halo-color": "#fff",
                    "text-halo-width": 2,
                },
                "filter": ["==", ["get", "icon"], icon_name],
            },
            source="places",
        )

    # Use the new TextFilterControl instead of JavaScript injection
    text_filter = TextFilterControl(
        layer_ids=layer_ids,
        placeholder="Filter by name",
        position="top-right",
        match_mode="contains"
    )
    map_instance.add_control(text_filter)

    html = map_instance.render()
    
    # Verify the control is rendered with proper structure
    assert "maplibreum-text-filter" in html
    assert "Filter by name" in html
    assert "map.setLayoutProperty" in html
    
    # Verify layer IDs are passed to the control
    for layer_id in layer_ids:
        assert layer_id in html
    
    # Verify match mode logic is present
    assert "matchMode" in html or "contains" in html
