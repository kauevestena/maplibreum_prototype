"""Test replicating the change-the-case-of-labels example."""

from __future__ import annotations

from maplibreum import Map


def test_change_the_case_of_labels() -> None:
    """Use upcase and downcase expressions for symbol labels."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-116.231, 43.604],
        zoom=11,
    )

    boise_dog_parks = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "FacilityName": "Together Treasure Valley Dog Island",
                    "Comments": "Large off-leash park",
                },
                "geometry": {"type": "Point", "coordinates": [-116.246, 43.62]},
            },
            {
                "type": "Feature",
                "properties": {
                    "FacilityName": "Morris Hill Park",
                    "Comments": "Shaded agility area",
                },
                "geometry": {"type": "Point", "coordinates": [-116.22, 43.6]},
            },
        ],
    }

    map_instance.add_source("off-leash-areas", {"type": "geojson", "data": boise_dog_parks})
    map_instance.add_layer(
        {
            "id": "off-leash-areas",
            "type": "symbol",
            "layout": {
                "icon-image": "dog_park",
                "text-field": [
                    "format",
                    ["upcase", ["get", "FacilityName"]],
                    {"font-scale": 0.8},
                    "\n",
                    {},
                    ["downcase", ["get", "Comments"]],
                    {"font-scale": 0.6},
                ],
                "text-font": ["Noto Sans Regular"],
                "text-offset": [0, 0.6],
                "text-anchor": "top",
            },
        },
        source="off-leash-areas",
    )

    assert len(map_instance.layers) == 1
    layer_definition = map_instance.layers[0]["definition"]
    assert layer_definition["layout"]["text-field"][0] == "format"
    assert ["upcase", ["get", "FacilityName"]] in layer_definition["layout"]["text-field"]
    assert ["downcase", ["get", "Comments"]] in layer_definition["layout"]["text-field"]

    html = map_instance.render()
    assert "FacilityName" in html
    assert "upcase" in html
    assert "downcase" in html
