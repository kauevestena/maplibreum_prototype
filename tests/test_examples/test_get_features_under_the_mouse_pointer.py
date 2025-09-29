"""Parity test for the get-features-under-the-mouse-pointer example."""

from __future__ import annotations

import textwrap

from maplibreum.core import Map


def test_get_features_under_the_mouse_pointer() -> None:
    """Query rendered features and list their key properties while hovering (original)."""

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


def test_get_features_with_python_api() -> None:
    """Query features using improved Python API (Phase 1 improvement)."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-96, 37.8],
        zoom=3,
    )

    # Same styling
    map_instance.custom_css = textwrap.dedent(
        f"""
        .maplibreum-features-display {{
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            width: 50%;
            overflow: auto;
            background: rgba(255, 255, 255, 0.8);
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
        }}
        #{map_instance.map_id} canvas {{
            cursor: crosshair;
        }}
        """
    ).strip()

    # Setup display element
    setup_js = textwrap.dedent(
        """
        var featuresDisplay = document.createElement('div');
        featuresDisplay.id = 'features-display';
        featuresDisplay.className = 'maplibreum-features-display';
        featuresDisplay.innerHTML = 'Hover over the map to see features';
        map.getContainer().appendChild(featuresDisplay);
        """
    ).strip()

    map_instance.add_on_load_js(setup_js)

    # Use the new helper method for cleaner feature querying
    query_js = map_instance.query_rendered_features_at_point("event.point")
    
    feature_display_js = textwrap.dedent(
        f"""
        var display = document.getElementById('features-display');
        if (!display) return;
        
        var features = {query_js};
        
        if (features.length === 0) {{
            display.innerHTML = 'No features found at this location';
            return;
        }}
        
        var displayProperties = ['type', 'properties', 'id', 'layer', 'source', 'sourceLayer'];
        var featureInfo = features.map(function(feature, index) {{
            var info = {{}};
            displayProperties.forEach(function(prop) {{
                if (feature[prop] !== undefined) {{
                    info[prop] = feature[prop];
                }}
            }});
            return 'Feature ' + (index + 1) + ':\\n' + JSON.stringify(info, null, 2);
        }});
        
        display.innerHTML = '<strong>Found ' + features.length + ' feature(s):</strong>\\n\\n' + 
                           featureInfo.join('\\n\\n');
        """
    ).strip()

    # Use the mousemove convenience method
    map_instance.add_event_listener("mousemove", js=feature_display_js)

    html = map_instance.render()
    
    # Verify the Python API generated the correct JavaScript
    assert "queryRenderedFeatures(event.point)" in html
    assert "features-display" in html
    assert "Found ' + features.length + ' feature(s)" in html


def test_get_features_with_layer_filter() -> None:
    """Test feature querying with layer filtering (advanced usage)."""
    
    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-96, 37.8],
        zoom=3,
    )

    # Use the helper method with layer filtering
    # This shows how to query only specific layers
    query_specific_layers_js = map_instance.query_rendered_features_at_point(
        "event.point", 
        layers=["water", "landuse", "admin"]
    )
    
    display_js = f"""
        var features = {query_specific_layers_js};
        console.log('Found features in specific layers:', features);
    """
    
    map_instance.add_event_listener("mousemove", js=display_js)
    
    html = map_instance.render()
    
    # Verify the layer filtering is applied
    assert 'queryRenderedFeatures(event.point, {"layers": ["water", "landuse", "admin"]})' in html


def test_get_features_with_callback() -> None:
    """Test feature querying with Python callbacks (future enhancement demo)."""
    
    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-96, 37.8],
        zoom=3,
    )

    # This demonstrates how Python callbacks could work with feature data
    def feature_callback(event_data):
        """Handle feature query results in Python."""
        # In a real Jupyter environment, this would process the features
        if 'features' in event_data:
            print(f"Found {len(event_data['features'])} features")
        
    # Register a callback that includes feature data
    # This shows the potential for Python-side feature processing
    feature_query_js = textwrap.dedent(
        """
        var features = map.queryRenderedFeatures(event.point);
        data.features = features;
        data.feature_count = features.length;
        """
    ).strip()
    
    callback_id = map_instance.on("mousemove", feature_callback, js=feature_query_js)
    
    # Verify callback registration
    assert callback_id in map_instance._event_callbacks.get(map_instance.map_id, {})
    
    html = map_instance.render()
    assert "queryRenderedFeatures(event.point)" in html
    assert "data.features = features" in html
