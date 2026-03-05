from maplibreum import Map
from maplibreum.layers import SymbolLayer
from maplibreum.sources import GeoJSONSource


def test_generate_and_add_a_missing_icon_to_the_map():
    m = Map(map_style="https://demotiles.maplibre.org/style.json")

    points = GeoJSONSource(
        data={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {"color": "255,0,0"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [50, 0]},
                    "properties": {"color": "255,209,28"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-50, 0]},
                    "properties": {"color": "242,127,32"},
                },
            ],
        }
    )

    layer = SymbolLayer(
        id="points",
        source="points",
        layout={"icon-image": ["concat", "square-rgb-", ["get", "color"]]},
    )

    m.add_source("points", points)
    m.add_layer(layer)
    m.add_dynamic_color_icons("square-rgb-")

    html = m.render()

    assert "styleimagemissing" in html
    assert "map.addImage(id" in html
    assert "square-rgb-" in html
    assert any(source["name"] == "points" for source in m.sources)
    assert any(layer_info["definition"]["layout"]["icon-image"][0] == "concat" for layer_info in m.layers)
