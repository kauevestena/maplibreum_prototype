"""Validate the display-and-style-rich-text-labels example."""

from __future__ import annotations

from maplibreum import Map


COUNTRY_POINTS = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name_en": "Italy", "name": "Italia"},
            "geometry": {"type": "Point", "coordinates": [12.4964, 41.9028]},
        },
        {
            "type": "Feature",
            "properties": {"name_en": "Spain", "name": "España"},
            "geometry": {"type": "Point", "coordinates": [-3.7038, 40.4168]},
        },
    ],
}


def test_display_and_style_rich_text_labels() -> None:
    """Apply format expressions with mixed font scales and RTL plugin."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[17.49, 40.01],
        zoom=4,
    )

    map_instance.enable_rtl_text_plugin(
        "https://unpkg.com/@mapbox/mapbox-gl-rtl-text@0.3.0/dist/mapbox-gl-rtl-text.js"
    )

    map_instance.add_source("countries", {"type": "geojson", "data": COUNTRY_POINTS})
    map_instance.add_layer(
        {
            "id": "label_country",
            "type": "symbol",
            "layout": {
                "text-field": [
                    "format",
                    ["get", "name_en"],
                    {"font-scale": 1.2},
                    "\n",
                    {},
                    ["get", "name"],
                    {
                        "font-scale": 0.8,
                        "text-font": ["literal", ["Noto Sans Regular"]],
                    },
                ],
                "text-font": ["Noto Sans Regular"],
                "text-size": 16,
                "text-anchor": "center",
            },
        },
        source="countries",
    )

    assert map_instance.rtl_text_plugin is not None
    assert (
        map_instance.rtl_text_plugin["url"]
        == "https://unpkg.com/@mapbox/mapbox-gl-rtl-text@0.3.0/dist/mapbox-gl-rtl-text.js"
    )

    layer_definition = map_instance.layers[0]["definition"]
    text_field = layer_definition["layout"]["text-field"]
    assert text_field[0] == "format"
    assert ["get", "name_en"] in text_field
    assert ["get", "name"] in text_field

    html = map_instance.render()
    assert "name_en" in html
    assert "font-scale" in html
    assert "rtl-text" in html
