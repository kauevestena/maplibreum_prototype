from maplibreum import Map
from maplibreum.layers import SymbolLayer
from maplibreum.sources import GeoJSONSource


def test_use_a_fallback_image():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-77, 38.75],
        zoom=5,
    )

    points = GeoJSONSource(
        data={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-77.03238901390978, 38.913188059745586]},
                    "properties": {"title": "Washington DC", "icon": "monument"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-79.9959, 40.4406]},
                    "properties": {"title": "Pittsburgh", "icon": "bridges"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-76.2859, 36.8508]},
                    "properties": {"title": "Norfolk", "icon": "harbor"},
                },
            ],
        }
    )

    layer = SymbolLayer(
        id="points",
        source="points",
        layout={
            "icon-image": [
                "coalesce",
                ["image", ["concat", ["get", "icon"], "_11"]],
                ["image", "marker_11"],
            ],
            "text-field": ["get", "title"],
            "text-font": ["Noto Sans Regular"],
            "text-offset": [0, 0.6],
            "text-anchor": "top",
        },
    )

    m.add_source("points", points)
    m.add_layer(layer)

    html = m.render()

    assert any(source["name"] == "points" for source in m.sources)
    assert any(layer_info["definition"]["layout"]["icon-image"][0] == "coalesce" for layer_info in m.layers)
    assert "\"coalesce\"" in html
    assert "marker_11" in html
