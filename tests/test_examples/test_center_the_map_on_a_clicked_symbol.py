"""Parity test for the center-the-map-on-a-clicked-symbol example."""

from maplibreum.core import Map
from maplibreum import layers


def test_center_the_map_on_a_clicked_symbol():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-90.96, -0.47],
        zoom=7.5,
    )

    m.add_image(
        "custom-marker",
        url="https://maplibre.org/maplibre-gl-js/docs/assets/custom_marker.png",
    )

    m.add_source(
        "points",
        {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-91.395263671875, -0.9145729757782163],
                        },
                    },
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-90.32958984375, -0.6344474832838974],
                        },
                    },
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-91.34033203125, 0.01647949196029245],
                        },
                    },
                ],
            },
        },
    )

    m.add_layer(
        layers.SymbolLayer(
            id="symbols",
            source="points",
            layout={"icon-image": "custom-marker"},
        ).to_dict()
    )

    m.add_event_listener(
        "click",
        layer_id="symbols",
        js="\n".join(
            [
                "map.flyTo({",
                "    center: event.features[0].geometry.coordinates",
                "});",
            ]
        ),
    )

    m.add_event_listener(
        "mouseenter",
        layer_id="symbols",
        js="map.getCanvas().style.cursor = 'pointer';",
    )

    m.add_event_listener(
        "mouseleave",
        layer_id="symbols",
        js="map.getCanvas().style.cursor = '';",
    )

    html = m.render()

    assert '"style": "https://demotiles.maplibre.org/style.json"' in html
    assert '"center": [-90.96, -0.47]' in html
    assert '"zoom": 7.5' in html
    assert "custom_marker.png" in html
    assert 'map.addSource("points"' in html
    assert "map.flyTo({" in html
    assert "map.getCanvas().style.cursor = 'pointer';" in html
