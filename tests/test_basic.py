import pytest
from maplibreum.core import Map, GeoJson, Legend


@pytest.fixture
def map_instance():
    """Provide a fresh Map instance for each test."""
    return Map()


def test_map_creation_defaults(map_instance):
    assert map_instance.center == [0, 0]
    assert map_instance.zoom == 2
    assert map_instance.layers == []
    assert map_instance.popups == []


def test_map_render_contains_style(map_instance):
    html = map_instance.render()
    assert isinstance(html, str)
    assert map_instance.map_style in html
    assert '<div id="map"' in html


def test_add_tile_layer(map_instance):
    source = {
        "type": "raster",
        "tiles": ["https://example.com/{z}/{x}/{y}.png"],
        "tileSize": 256,
    }
    layer = {"id": "raster", "type": "raster"}
    map_instance.add_layer(layer, source=source)
    assert map_instance.layers[0]["definition"]["type"] == "raster"
    assert (
        map_instance.sources[0]["definition"]["tiles"][0]
        == "https://example.com/{z}/{x}/{y}.png"
    )


def test_add_wms_layer(map_instance):
    map_instance.add_wms_layer("https://example.com/wms", layers="basic")
    tiles_url = map_instance.sources[0]["definition"]["tiles"][0]
    assert "service=WMS" in tiles_url
    assert "layers=basic" in tiles_url
    assert "bbox={bbox-epsg-3857}" in tiles_url
    assert map_instance.layers[0]["definition"]["type"] == "raster"


def test_add_layer_control(map_instance):
    map_instance.add_control("navigation", "top-left")
    assert map_instance.controls == [
        {"type": "navigation", "position": "top-left", "options": {}}
    ]


def test_shape_layers(map_instance):
    source = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
    map_instance.add_circle_layer("circle", source)
    map_instance.add_line_layer("line", source)
    map_instance.add_fill_layer("fill", source)
    types = [layer["definition"]["type"] for layer in map_instance.layers]
    assert types == ["circle", "line", "fill"]


def test_fill_extrusion_layer(map_instance):
    source = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
    map_instance.add_fill_extrusion_layer("extrusion", source)
    layer = map_instance.layers[0]["definition"]
    assert layer["type"] == "fill-extrusion"
    assert layer["paint"]["fill-extrusion-height"] == 10
    assert layer["paint"]["fill-extrusion-color"] == "#007cbf"


def test_heatmap_layer(map_instance):
    source = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
    map_instance.add_heatmap_layer("heat", source)
    layer = map_instance.layers[0]["definition"]
    assert layer["type"] == "heatmap"
    assert layer["paint"]["heatmap-radius"] == 20

    map_instance.add_heatmap_layer("heat_custom", source, paint={"heatmap-radius": 5})
    custom = map_instance.layers[1]["definition"]
    assert custom["paint"]["heatmap-radius"] == 5
    assert custom["paint"]["heatmap-opacity"] == 1


def test_popups(map_instance):
    map_instance.add_popup("<b>Hi</b>", coordinates=[1, 2])
    assert len(map_instance.popups) == 1
    popup = map_instance.popups[0]
    assert popup["html"] == "<b>Hi</b>"
    assert popup["coordinates"] == [1, 2]


def test_geojson_styling(map_instance):
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
                },
            }
        ],
    }

    def style_fn(feature):
        return {"fillColor": "blue", "fillOpacity": 0.5}

    GeoJson(geojson, style_function=style_fn).add_to(map_instance)
    props = map_instance.sources[0]["definition"]["data"]["features"][0]["properties"]
    assert props["fillColor"] == "blue"
    assert props["fillOpacity"] == 0.5
    paint = map_instance.layers[0]["definition"]["paint"]
    assert paint["fill-color"] == ["get", "fillColor", ["properties"]]
    assert paint["fill-opacity"] == ["get", "fillOpacity", ["properties"]]


def test_legend_rendering():
    m = Map()
    legend = Legend([("A", "#ff0000"), ("B", "#00ff00")])
    legend.add_to(m)
    html = m.render()
    assert "maplibreum-legend" in html
    assert "#ff0000" in html
    assert "A" in html
