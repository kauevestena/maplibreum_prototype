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

    from maplibreum.layers import HTMLClusterLayer

    html_cluster = HTMLClusterLayer(
        id="earthquake_cluster_html",
        source="earthquakes",
        colors=['#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c'],
        properties=["mag1", "mag2", "mag3", "mag4", "mag5"],
    )
    map_instance.add_layer(html_cluster)

    source_lookup = {
        source["name"]: source["definition"] for source in map_instance.sources
    }
    assert source_lookup["earthquakes"]["cluster"] is True
    assert "clusterProperties" in source_lookup["earthquakes"]
    assert source_lookup["earthquakes"]["clusterProperties"]["mag3"][0] == "+"

    html = map_instance.render()
    assert "donutSegment" in html
    assert "map.querySourceFeatures(sourceId)" in html
    assert "clusterProperties" in html
