"""Test the variable-label-placement gallery example."""

from __future__ import annotations

from maplibreum import Map


PLACES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"description": "Ford's Theater", "icon": "theatre"},
            "geometry": {"type": "Point", "coordinates": [-77.038659, 38.931567]},
        },
        {
            "type": "Feature",
            "properties": {"description": "The Gaslight", "icon": "theatre"},
            "geometry": {"type": "Point", "coordinates": [-77.003168, 38.894651]},
        },
        {
            "type": "Feature",
            "properties": {"description": "Horrible Harry's", "icon": "bar"},
            "geometry": {"type": "Point", "coordinates": [-77.090372, 38.881189]},
        },
        {
            "type": "Feature",
            "properties": {"description": "Bike Party", "icon": "bicycle"},
            "geometry": {"type": "Point", "coordinates": [-77.052477, 38.943951]},
        },
        {
            "type": "Feature",
            "properties": {"description": "Rockabilly Rockstars", "icon": "music"},
            "geometry": {"type": "Point", "coordinates": [-77.031706, 38.914581]},
        },
        {
            "type": "Feature",
            "properties": {"description": "District Drum Tribe", "icon": "music"},
            "geometry": {"type": "Point", "coordinates": [-77.020945, 38.878241]},
        },
        {
            "type": "Feature",
            "properties": {"description": "Motown Memories", "icon": "music"},
            "geometry": {"type": "Point", "coordinates": [-77.007481, 38.876516]},
        },
    ],
}


def test_variable_label_placement() -> None:
    """Allow labels to shift using text-variable-anchor and animate the camera."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-77.04, 38.907],
        zoom=11.15,
    )

    map_instance.add_source("places", {"type": "geojson", "data": PLACES})
    map_instance.add_layer(
        {
            "id": "poi-labels",
            "type": "symbol",
            "layout": {
                "text-field": ["get", "description"],
                "text-font": ["Noto Sans Regular"],
                "text-variable-anchor": ["top", "bottom", "left", "right"],
                "text-radial-offset": 0.5,
                "text-justify": "auto",
                "icon-image": ["get", "icon"],
            },
        },
        source="places",
    )

    map_instance.add_on_load_js("map.rotateTo(180, {duration: 10000});")

    assert len(map_instance.layers) == 1
    layout = map_instance.layers[0]["definition"]["layout"]
    assert layout["text-field"] == ["get", "description"]
    assert layout["text-variable-anchor"] == ["top", "bottom", "left", "right"]
    assert layout["text-radial-offset"] == 0.5
    assert ["get", "icon"] == layout["icon-image"]

    html = map_instance.render()
    assert "text-variable-anchor" in html
    assert "map.rotateTo(180" in html