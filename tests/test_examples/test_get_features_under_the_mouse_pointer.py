"""Parity test for the get-features-under-the-mouse-pointer example."""

from __future__ import annotations

import textwrap

from maplibreum.core import Map


def test_get_features_under_the_mouse_pointer() -> None:
    """Query rendered features and list their key properties while hovering."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-96, 37.8],
        zoom=3,
    )

    map_instance.custom_css = textwrap.dedent(
        f"""
        .maplibreum-feature-list {{
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            width: 50%;
            overflow: auto;
            background: rgba(255, 255, 255, 0.8);
        }}
        #{map_instance.map_id} canvas {{
            cursor: crosshair;
        }}
        """
    ).strip()

    setup_js = textwrap.dedent(
        """
        var featureList = document.createElement('pre');
        featureList.id = 'maplibreum-feature-list';
        featureList.className = 'maplibreum-feature-list';
        map.getContainer().appendChild(featureList);
        window._maplibreumFeatureList = featureList;
        """
    ).strip()

    map_instance.add_on_load_js(setup_js)

    move_js = textwrap.dedent(
        """
        var output = window._maplibreumFeatureList || document.getElementById('maplibreum-feature-list');
        if (!output) { return; }
        var features = map.queryRenderedFeatures(event.point);
        var displayProperties = ['type', 'properties', 'id', 'layer', 'source', 'sourceLayer', 'state'];
        var subset = features.map(function(feature) {
            var info = {};
            displayProperties.forEach(function(prop) {
                info[prop] = feature[prop];
            });
            return info;
        });
        output.innerHTML = JSON.stringify(subset, null, 2);
        """
    ).strip()

    map_instance.add_event_listener("mousemove", js=move_js)

    binding = map_instance.event_bindings[0]
    assert "queryRenderedFeatures" in binding.js
    assert "displayProperties" in binding.js

    html = map_instance.render()
    assert "maplibreum-feature-list" in html
    assert "queryRenderedFeatures" in html
