"""Port the filter-symbols-by-text-input example to pytest."""

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


def test_filter_symbols_by_text_input() -> None:
    """Toggle layer visibility when users type icon names into a search input."""

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

    map_instance.custom_css = textwrap.dedent(
        """
        .maplibreum-filter-ctrl {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1;
        }

        .maplibreum-filter-ctrl input[type='search'] {
            font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
            border: 0;
            background-color: #fff;
            margin: 0;
            color: rgba(0, 0, 0, 0.6);
            padding: 10px;
            box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
            border-radius: 3px;
            width: 200px;
        }
        """
    ).strip()

    control_js = textwrap.dedent(
        """
        var container = document.createElement('div');
        container.className = 'maplibreum-filter-ctrl';
        var input = document.createElement('input');
        input.type = 'search';
        input.id = 'maplibreum-filter-input';
        input.placeholder = 'Filter by name';
        container.appendChild(input);
        map.getContainer().appendChild(container);

        var layerIDs = %s;
        input.addEventListener('keyup', function(event) {
            var value = event.target.value.trim().toLowerCase();
            layerIDs.forEach(function(layerId) {
                map.setLayoutProperty(
                    layerId,
                    'visibility',
                    layerId.indexOf(value) > -1 ? 'visible' : 'none'
                );
            });
        });
        """
    ) % textwrap.dedent(textwrap.indent(str([f"poi-{icon}" for icon in unique_icons]), ""))
    map_instance.add_on_load_js(control_js.strip())

    assert len(map_instance.layers) == len(unique_icons)
    for layer in map_instance.layers:
        assert layer["definition"]["filter"] == ["==", ["get", "icon"], layer["id"].split("poi-")[1]]

    on_load_js = "\n".join(map_instance._on_load_callbacks)
    assert "map.setLayoutProperty" in on_load_js
    assert "layerIDs" in on_load_js

    html = map_instance.render()
    assert "maplibreum-filter-ctrl" in html
    assert "Filter by name" in html
