"""Exercise the filter-layer-symbols-using-global-state example."""

from __future__ import annotations

import textwrap

from maplibreum import Map


def test_filter_layer_symbols_using_global_state() -> None:
    """Toggle symbol visibility based on a select element and global state."""

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[9.0679, 45.8822],
        zoom=9,
    )

    map_instance.add_source(
        "railways_and_lifts",
        {
            "type": "geojson",
            "data": "https://maplibre.org/maplibre-gl-js/docs/assets/funicolares-and-funivias-como.json",
        },
    )

    filter_expression = [
        "case",
        ["==", ["to-string", ["global-state", "type"]], ""],
        True,
        ["==", ["get", "type"], ["global-state", "type"]],
    ]

    map_instance.add_layer(
        {
            "id": "railways_and_lifts_labels",
            "type": "symbol",
            "layout": {
                "text-field": "{name}",
                "text-font": ["Open Sans Semibold"],
                "text-offset": [0, 1],
                "text-anchor": "top",
            },
            "paint": {
                "text-color": "#000000",
                "text-halo-color": "#ffffff",
                "text-halo-width": 2,
            },
            "filter": filter_expression,
        },
        source="railways_and_lifts",
    )
    map_instance.add_layer(
        {
            "id": "railways_and_lifts_points",
            "type": "circle",
            "paint": {
                "circle-radius": 5,
                "circle-color": "#000000",
            },
            "filter": filter_expression,
        },
        source="railways_and_lifts",
    )

    map_instance.custom_css = textwrap.dedent(
        """
        .maplibreum-type-filter {
            position: absolute;
            top: 10px;
            left: 10px;
            background: #fff;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
            font: 13px/18px 'Helvetica Neue', Arial, sans-serif;
        }
        """
    ).strip()

    control_js = textwrap.dedent(
        """
        var fieldset = document.createElement('fieldset');
        fieldset.className = 'maplibreum-type-filter';
        var label = document.createElement('label');
        label.textContent = 'Filter by type';
        fieldset.appendChild(label);
        var select = document.createElement('select');
        select.name = 'type';
        ['All', 'lift', 'railway'].forEach(function(optionValue, index) {
            var option = document.createElement('option');
            option.value = index === 0 ? '' : optionValue;
            option.textContent = index === 0 ? 'All' : optionValue.replace('-', ' ');
            if (index === 0) {
                option.selected = true;
            }
            select.appendChild(option);
        });
        fieldset.appendChild(select);
        map.getContainer().appendChild(fieldset);
        map.setGlobalStateProperty('type', select.value);
        select.addEventListener('change', function(event) {
            map.setGlobalStateProperty('type', event.target.value);
        });
        """
    ).strip()
    map_instance.add_on_load_js(control_js)

    assert len(map_instance.layers) == 2
    for layer in map_instance.layers:
        assert layer["definition"]["filter"] == filter_expression

    joined_js = "\n".join(map_instance._on_load_callbacks)
    assert "setGlobalStateProperty" in joined_js

    html = map_instance.render()
    assert "maplibreum-type-filter" in html
    assert "global-state" in html
