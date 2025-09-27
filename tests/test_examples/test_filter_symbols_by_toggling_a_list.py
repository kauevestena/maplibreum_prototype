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

    map_instance.custom_css = textwrap.dedent(
        """
        .maplibreum-filter-group {
            font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
            font-weight: 600;
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1;
            border-radius: 3px;
            width: 140px;
            color: #fff;
        }

        .maplibreum-filter-group input[type='checkbox'] {
            display: none;
        }

        .maplibreum-filter-group input[type='checkbox'] + label {
            background-color: #3386c0;
            display: block;
            cursor: pointer;
            padding: 10px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.25);
            text-transform: capitalize;
        }

        .maplibreum-filter-group input[type='checkbox']:first-child + label {
            border-radius: 3px 3px 0 0;
        }

        .maplibreum-filter-group label:last-child {
            border-radius: 0 0 3px 3px;
            border: none;
        }

        .maplibreum-filter-group input[type='checkbox']:checked + label,
        .maplibreum-filter-group input[type='checkbox'] + label:hover {
            background-color: #4ea0da;
        }

        .maplibreum-filter-group input[type='checkbox']:checked + label:before {
            content: '✔';
            margin-right: 5px;
        }
        """
    ).strip()

    control_js = textwrap.dedent(
        """
        var container = document.createElement('nav');
        container.id = 'maplibreum-filter-group';
        container.className = 'maplibreum-filter-group';
        var layers = %s;
        layers.forEach(function(layerId, index) {
            var checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = layerId;
            checkbox.checked = true;
            container.appendChild(checkbox);

            var label = document.createElement('label');
            label.setAttribute('for', layerId);
            label.textContent = layerId.replace('poi-', '');
            container.appendChild(label);

            checkbox.addEventListener('change', function(event) {
                map.setLayoutProperty(
                    layerId,
                    'visibility',
                    event.target.checked ? 'visible' : 'none'
                );
            });
        });
        map.getContainer().appendChild(container);
        """
    ) % textwrap.dedent(textwrap.indent(str([f"poi-{icon}" for icon in unique_icons]), ""))
    map_instance.add_on_load_js(control_js.strip())

    assert len(map_instance.layers) == len(unique_icons)
    for layer in map_instance.layers:
        assert layer["definition"]["filter"] == ["==", "icon", layer["id"].replace("poi-", "")]

    joined_js = "\n".join(map_instance._on_load_callbacks)
    assert "map.setLayoutProperty" in joined_js
    assert "checkbox" in joined_js

    html = map_instance.render()
    assert "maplibreum-filter-group" in html
    for icon in unique_icons:
        assert icon in html
