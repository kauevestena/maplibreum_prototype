"""Parity test for the sync-movement-of-multiple-maps example."""

from __future__ import annotations

import textwrap

from maplibreum.core import Map


def test_sync_movement_of_multiple_maps() -> None:
    """Instantiate three MapLibre maps and synchronise their viewpoints."""

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=1,
        map_options={"maplibreLogo": True},
        width="100%",
        height="500px",
    )

    map_instance.custom_css = textwrap.dedent(
        f"""
        html, body {{
            height: 100%;
        }}
        .maplibreum-sync-wrapper {{
            display: flex;
            width: 100%;
            height: 100%;
        }}
        .maplibreum-sync-wrapper > .maplibreum-sync-map {{
            flex: 1 1 0;
            height: 100%;
        }}
        #{map_instance.map_id} {{
            height: 100%;
        }}
        """
    ).strip()

    map_instance.add_external_script("https://unpkg.com/@mapbox/mapbox-gl-sync-move@0.3.1")

    sync_js = textwrap.dedent(
        f"""
        var primaryContainer = document.getElementById('{map_instance.map_id}');
        if (!primaryContainer) {{ return; }}

        var wrapper = document.createElement('div');
        wrapper.className = 'maplibreum-sync-wrapper';
        primaryContainer.parentNode.insertBefore(wrapper, primaryContainer);
        wrapper.appendChild(primaryContainer);
        primaryContainer.classList.add('maplibreum-sync-map');

        var mapIds = ['{map_instance.map_id}', '{map_instance.map_id}-secondary', '{map_instance.map_id}-tertiary'];
        for (var i = 1; i < mapIds.length; i++) {{
            var div = document.createElement('div');
            div.id = mapIds[i];
            div.className = 'maplibreum-sync-map';
            wrapper.appendChild(div);
        }}

        var map2 = new maplibregl.Map({{
            container: mapIds[1],
            style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
            center: [0, 0],
            zoom: 1,
            maplibreLogo: true
        }});

        var map3 = new maplibregl.Map({{
            container: mapIds[2],
            style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            center: [0, 0],
            zoom: 1,
            maplibreLogo: true
        }});

        if (typeof syncMaps === 'function') {{
            syncMaps(map, map2, map3);
        }}

        window._maplibreumSyncedMaps = [map, map2, map3];
        window._maplibreumSyncedCenter = map.getCenter();

        function updateCenter(sourceMap) {{
            window._maplibreumSyncedCenter = sourceMap.getCenter();
        }}

        map.on('move', function() {{ updateCenter(map); }});
        map2.on('move', function() {{ updateCenter(map2); }});
        map3.on('move', function() {{ updateCenter(map3); }});
        """
    ).strip()

    map_instance.add_on_load_js(sync_js)

    assert map_instance.center == [0, 0]
    assert map_instance.zoom == 1
    assert map_instance.additional_map_options["maplibreLogo"] is True

    html = map_instance.render()
    assert "syncMaps(map, map2, map3)" in html
    assert "mapbox-gl-sync-move" in html
    assert "window._maplibreumSyncedMaps" in html
