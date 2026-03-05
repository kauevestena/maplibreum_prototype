"""Implement the filter-symbols-by-toggling-a-list gallery example."""

from __future__ import annotations

import textwrap

from maplibreum import Map


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


def test_filter_symbols_by_toggling_a_list() -> None:
    """Replicate checkbox toggles that control symbol visibility by category."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-77.04, 38.907],
        zoom=11.15,
    )

    map_instance.add_source("places", {"type": "geojson", "data": PLACES})

    unique_icons = sorted({feature["properties"]["icon"] for feature in PLACES["features"]})
    for icon_name in unique_icons:
        map_instance.add_layer(
            {
                "id": f"poi-{icon_name}",
                "type": "symbol",
                "layout": {
                    "icon-image": f"{icon_name}_11",
                    "icon-overlap": "always",
                },
                "filter": ["==", "icon", icon_name],
            },
            source="places",
        )

    from maplibreum.controls import LayerFilterControl

    layer_ids = [f"poi-{icon}" for icon in unique_icons]

    filter_control = LayerFilterControl(
        layers=layer_ids,
        position="top-right",
        css_class="maplibreum-filter-group"
    )

    map_instance.add_control(filter_control)

    assert len(map_instance.layers) == len(unique_icons)
    for layer in map_instance.layers:
        assert layer["definition"]["filter"] == ["==", "icon", layer["id"].replace("poi-", "")]

    html = map_instance.render()
    assert "map.setLayoutProperty(" in html
    assert "checkbox" in html
    assert "maplibreum-filter-group" in html
    for icon in unique_icons:
        assert icon in html
