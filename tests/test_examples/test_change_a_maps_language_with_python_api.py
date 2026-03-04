"""Reproduce the change-a-maps-language example."""

from __future__ import annotations

import textwrap

from maplibreum import Map


COUNTRY_FEATURES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name:en": "Austria",
                "name:fr": "Autriche",
                "name:ru": "Австрия",
                "name:de": "Österreich",
                "name:es": "Austria",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [16.05, 48.2],
            },
        },
        {
            "type": "Feature",
            "properties": {
                "name:en": "Hungary",
                "name:fr": "Hongrie",
                "name:ru": "Венгрия",
                "name:de": "Ungarn",
                "name:es": "Hungría",
            },
            "geometry": {"type": "Point", "coordinates": [19.05, 47.5]},
        },
        {
            "type": "Feature",
            "properties": {
                "name:en": "Germany",
                "name:fr": "Allemagne",
                "name:ru": "Германия",
                "name:de": "Deutschland",
                "name:es": "Alemania",
            },
            "geometry": {"type": "Point", "coordinates": [13.4, 52.52]},
        },
    ],
}


LANGUAGE_CODES = ["fr", "ru", "de", "es"]


def _base_label_layer(layer_id: str) -> dict:
    return {
        "id": layer_id,
        "type": "symbol",
        "layout": {
            "text-field": ["get", "name:en"],
            "text-font": ["Noto Sans Regular"],
            "text-size": 13,
        },
        "paint": {"text-color": "#333", "text-halo-color": "#fff", "text-halo-width": 1},
    }


def test_change_a_maps_language_with_python_api() -> None:
    """Dynamically toggle label languages using a button strip."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[16.05, 48.0],
        zoom=3.0,
    )
    map_instance.add_source("countries", {"type": "geojson", "data": COUNTRY_FEATURES})

    for index in range(1, 4):
        layer_id = f"label_country_{index}"
        definition = _base_label_layer(layer_id)
        map_instance.add_layer(definition, source="countries")

    from maplibreum.controls import LanguageControl
    language_ctrl = LanguageControl(
        languages=LANGUAGE_CODES,
        layers=["label_country_1", "label_country_2", "label_country_3"]
    )
    map_instance.add_control(language_ctrl)

    # Render the map
    html = map_instance.render()

    assert len(map_instance.layers) == 3
    text_fields = {
        layer["id"]: layer["definition"]["layout"]["text-field"]
        for layer in map_instance.layers
    }
    for key in ("label_country_1", "label_country_2", "label_country_3"):
        assert text_fields[key] == ["get", "name:en"]

    assert "maplibreum-language-buttons" in html
    for code in ("fr", "ru", "de", "es"):
        assert f"'{code}'" in html or f'"{code}"' in html
