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


def test_change_a_maps_language() -> None:
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

    map_instance.custom_css = textwrap.dedent(
        """
        .maplibreum-language-buttons {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 8px;
            padding: 6px 10px;
            list-style: none;
            background: rgba(0, 0, 0, 0.65);
            border-radius: 999px;
            color: #fff;
            font: 12px/18px 'Helvetica Neue', Arial, sans-serif;
        }

        .maplibreum-language-buttons button {
            border: none;
            background: transparent;
            color: inherit;
            cursor: pointer;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 14px;
        }

        .maplibreum-language-buttons button:hover,
        .maplibreum-language-buttons button.is-active {
            background: #ee8a65;
        }
        """
    ).strip()

    buttons_js = textwrap.dedent(
        """
        var container = document.createElement('ul');
        container.id = 'maplibreum-language-buttons';
        container.className = 'maplibreum-language-buttons';

        var languages = %s;

        languages.forEach(function(code, index) {
            var item = document.createElement('li');
            var button = document.createElement('button');
            button.type = 'button';
            button.dataset.language = code;
            button.textContent = code.toUpperCase();
            if (index === 0) {
                button.classList.add('is-active');
            }
            item.appendChild(button);
            container.appendChild(item);
        });

        container.addEventListener('click', function(event) {
            var target = event.target;
            if (!target || !target.dataset || !target.dataset.language) {
                return;
            }
            var language = target.dataset.language;
            container.querySelectorAll('button').forEach(function(btn) {
                btn.classList.toggle('is-active', btn === target);
            });
            ['label_country_1', 'label_country_2', 'label_country_3'].forEach(function(layerId) {
                map.setLayoutProperty(layerId, 'text-field', ['get', 'name:' + language]);
            });
        });

        map.getContainer().appendChild(container);
        """
    ) % textwrap.dedent(textwrap.indent(str(LANGUAGE_CODES), ""))
    map_instance.add_on_load_js(buttons_js.strip())

    assert len(map_instance.layers) == 3
    text_fields = {
        layer["id"]: layer["definition"]["layout"]["text-field"]
        for layer in map_instance.layers
    }
    for key in ("label_country_1", "label_country_2", "label_country_3"):
        assert text_fields[key] == ["get", "name:en"]

    joined_js = "\n".join(map_instance._on_load_callbacks)
    assert "map.setLayoutProperty" in joined_js
    assert "name:" in joined_js

    html = map_instance.render()
    assert "maplibreum-language-buttons" in html
    for code in ("fr", "ru", "de", "es"):
        assert f"'" + code + "'" in html or f'\"{code}\"' in html
