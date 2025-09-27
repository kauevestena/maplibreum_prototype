"""Mimic the display-html-clusters-with-custom-properties example."""

from __future__ import annotations

import textwrap

from maplibreum import Map


def test_display_html_clusters_with_custom_properties() -> None:
    """Create clustered layers and HTML donut markers that mirror the example."""

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 20],
        zoom=0.3,
    )
    map_instance.add_control("navigation")

    earthquakes_source = {
        "type": "geojson",
        "data": "https://maplibre.org/maplibre-gl-js/docs/assets/earthquakes.geojson",
        "cluster": True,
        "clusterRadius": 80,
        "clusterProperties": {
            "mag1": ["+", ["case", ["<", ["get", "mag"], 2], 1, 0]],
            "mag2": [
                "+",
                [
                    "case",
                    ["all", [">=", ["get", "mag"], 2], ["<", ["get", "mag"], 3]],
                    1,
                    0,
                ],
            ],
            "mag3": [
                "+",
                [
                    "case",
                    ["all", [">=", ["get", "mag"], 3], ["<", ["get", "mag"], 4]],
                    1,
                    0,
                ],
            ],
            "mag4": [
                "+",
                [
                    "case",
                    ["all", [">=", ["get", "mag"], 4], ["<", ["get", "mag"], 5]],
                    1,
                    0,
                ],
            ],
            "mag5": [
                "+",
                ["case", [">=", ["get", "mag"], 5], 1, 0],
            ],
        },
    }
    map_instance.add_source("earthquakes", earthquakes_source)

    map_instance.add_layer(
        {
            "id": "earthquake_circle",
            "type": "circle",
            "paint": {
                "circle-color": [
                    "case",
                    ["<", ["get", "mag"], 2],
                    "#fed976",
                    ["all", [">=", ["get", "mag"], 2], ["<", ["get", "mag"], 3]],
                    "#feb24c",
                    ["all", [">=", ["get", "mag"], 3], ["<", ["get", "mag"], 4]],
                    "#fd8d3c",
                    ["all", [">=", ["get", "mag"], 4], ["<", ["get", "mag"], 5]],
                    "#fc4e2a",
                    "#e31a1c",
                ],
                "circle-opacity": 0.6,
                "circle-radius": 12,
            },
            "filter": ["!=", "cluster", True],
        },
        source="earthquakes",
    )
    map_instance.add_layer(
        {
            "id": "earthquake_label",
            "type": "symbol",
            "layout": {
                "text-field": [
                    "number-format",
                    ["get", "mag"],
                    {"min-fraction-digits": 1, "max-fraction-digits": 1},
                ],
                "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
                "text-size": 10,
            },
            "paint": {
                "text-color": [
                    "case",
                    ["<", ["get", "mag"], 3],
                    "black",
                    "white",
                ]
            },
            "filter": ["!=", "cluster", True],
        },
        source="earthquakes",
    )

    donut_js = textwrap.dedent(
        """
        var donutColors = ['#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c'];
        var markers = {};
        var markersOnScreen = {};

        function updateMarkers() {
            var newMarkers = {};
            var features = map.querySourceFeatures('earthquakes');
            for (var i = 0; i < features.length; i++) {
                var feature = features[i];
                if (!feature.properties.cluster) { continue; }
                var id = feature.properties.cluster_id;
                var marker = markers[id];
                if (!marker) {
                    var element = createDonutChart(feature.properties);
                    marker = markers[id] = new maplibregl.Marker({ element: element }).setLngLat(feature.geometry.coordinates);
                }
                newMarkers[id] = marker;
                if (!markersOnScreen[id]) {
                    marker.addTo(map);
                }
            }
            for (var existingId in markersOnScreen) {
                if (!newMarkers[existingId]) {
                    markersOnScreen[existingId].remove();
                }
            }
            markersOnScreen = newMarkers;
        }

        map.on('data', function(event) {
            if (event.sourceId !== 'earthquakes' || !event.isSourceLoaded) {
                return;
            }
            map.on('move', updateMarkers);
            map.on('moveend', updateMarkers);
            updateMarkers();
        });

        function createDonutChart(properties) {
            var counts = [properties.mag1, properties.mag2, properties.mag3, properties.mag4, properties.mag5];
            var offsets = [];
            var total = 0;
            for (var i = 0; i < counts.length; i++) {
                offsets.push(total);
                total += counts[i];
            }
            var fontSize = total >= 1000 ? 22 : total >= 100 ? 20 : total >= 10 ? 18 : 16;
            var radius = total >= 1000 ? 50 : total >= 100 ? 32 : total >= 10 ? 24 : 18;
            var inner = Math.round(radius * 0.6);
            var width = radius * 2;
            var svg = '<div><svg width="' + width + '" height="' + width + '" viewBox="0 0 ' + width + ' ' + width + '" text-anchor="middle" style="font: ' + fontSize + 'px sans-serif; display: block">';
            for (var j = 0; j < counts.length; j++) {
                svg += donutSegment(offsets[j] / total, (offsets[j] + counts[j]) / total, radius, inner, donutColors[j]);
            }
            svg += '<circle cx="' + radius + '" cy="' + radius + '" r="' + inner + '" fill="white" />';
            svg += '<text dominant-baseline="central" transform="translate(' + radius + ', ' + radius + ')">' + total + '</text>';
            svg += '</svg></div>';
            var container = document.createElement('div');
            container.innerHTML = svg;
            return container.firstChild;
        }

        function donutSegment(start, end, radius, innerRadius, color) {
            if (end - start === 0) {
                return '';
            }
            var a0 = 2 * Math.PI * (start - 0.25);
            var a1 = 2 * Math.PI * (end - 0.25);
            var x0 = Math.cos(a0), y0 = Math.sin(a0);
            var x1 = Math.cos(a1), y1 = Math.sin(a1);
            var largeArc = end - start > 0.5 ? 1 : 0;
            return '<path d="M ' + radius * x0 + ' ' + radius * y0 + ' A ' + radius + ' ' + radius + ' 0 ' + largeArc + ' 1 ' + radius * x1 + ' ' + radius * y1 + ' L ' + innerRadius * x1 + ' ' + innerRadius * y1 + ' A ' + innerRadius + ' ' + innerRadius + ' 0 ' + largeArc + ' 0 ' + innerRadius * x0 + ' ' + innerRadius * y0 + ' Z" fill="' + color + '" />';
        }
        """
    ).strip()
    map_instance.add_on_load_js(donut_js)

    source_lookup = {
        source["name"]: source["definition"] for source in map_instance.sources
    }
    assert source_lookup["earthquakes"]["cluster"] is True
    assert "clusterProperties" in source_lookup["earthquakes"]
    assert source_lookup["earthquakes"]["clusterProperties"]["mag3"][0] == "+"

    html = map_instance.render()
    assert "donutSegment" in html
    assert "map.querySourceFeatures('earthquakes')" in html
    assert "clusterProperties" in html
