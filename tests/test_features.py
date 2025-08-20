import pytest
from maplibreum.core import (
    Map,
    Marker,
    GeoJson,
    Circle,
    CircleMarker,
    PolyLine,
    Polygon,
    Rectangle,
    LayerControl,
)


def test_map_style():
    m = Map(map_style="streets")
    assert (
        m.map_style
        == "https://api.maptiler.com/maps/streets/style.json?key=YOUR_API_KEY"
    )


def test_marker():
    m = Map()
    marker = Marker(coordinates=[-74.5, 40], popup="A marker!", color="red")
    marker.add_to(m)
    assert len(m.layers) == 1
    assert len(m.popups) == 1
    assert m.layers[0]["definition"]["paint"]["circle-color"] == "red"


def test_add_marker_wrapper():
    m = Map()
    m.add_marker(coordinates=[-74.5, 40], popup="Wrapper marker", color="green")
    assert len(m.layers) == 1
    assert len(m.popups) == 1
    assert m.layers[0]["definition"]["paint"]["circle-color"] == "green"


def test_geojson():
    m = Map()
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-74.6, 40.1],
                            [-74.6, 39.9],
                            [-74.4, 39.9],
                            [-74.4, 40.1],
                            [-74.6, 40.1],
                        ]
                    ],
                },
            }
        ],
    }

    def style_function(feature):
        return {"fillColor": "blue", "fillOpacity": 0.5}

    geojson_layer = GeoJson(geojson_data, style_function=style_function)
    geojson_layer.add_to(m)
    assert geojson_data["features"][0]["properties"]["fillColor"] == "blue"
    assert geojson_data["features"][0]["properties"]["fillOpacity"] == 0.5
    assert len(m.layers) == 1
    assert m.layers[0]["definition"]["type"] == "fill"
    assert m.layers[0]["definition"]["paint"]["fill-color"] == [
        "get",
        "fillColor",
        ["properties"],
    ]


def test_geojson_line_and_point():
    m = Map()
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[0, 0], [1, 1]],
                },
            },
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Point", "coordinates": [2, 2]},
            },
        ],
    }

    def style_function(feature):
        return {
            "color": "green",
            "weight": 5,
            "opacity": 0.7,
            "fillColor": "yellow",
            "fillOpacity": 0.4,
        }

    geojson_layer = GeoJson(geojson_data, style_function=style_function)
    geojson_layer.add_to(m)

    assert geojson_data["features"][0]["properties"]["color"] == "green"
    assert geojson_data["features"][0]["properties"]["weight"] == 5
    assert geojson_data["features"][0]["properties"]["opacity"] == 0.7
    assert geojson_data["features"][1]["properties"]["fillColor"] == "yellow"
    assert geojson_data["features"][1]["properties"]["fillOpacity"] == 0.4

    layer_types = {layer["definition"]["type"] for layer in m.layers}
    assert "line" in layer_types
    assert "circle" in layer_types

    line_layer = next(l for l in m.layers if l["definition"]["type"] == "line")
    assert line_layer["definition"]["paint"]["line-color"] == [
        "get",
        "color",
        ["properties"],
    ]
    assert line_layer["definition"]["paint"]["line-width"] == [
        "get",
        "weight",
        ["properties"],
    ]

    circle_layer = next(l for l in m.layers if l["definition"]["type"] == "circle")
    assert circle_layer["definition"]["paint"]["circle-color"] == [
        "get",
        "fillColor",
        ["properties"],
    ]
    assert circle_layer["definition"]["paint"]["circle-stroke-width"] == [
        "get",
        "weight",
        ["properties"],
    ]


def test_tile_layer_and_control():
    m = Map()
    m.add_tile_layer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        name="OSM",
        attribution="© OpenStreetMap contributors",
        subdomains=["a", "b", "c"],
    )
    html_no_control = m.render()
    assert "OSM" in html_no_control
    assert "layer-control" not in html_no_control

    LayerControl().add_to(m)
    html_with_control = m.render()
    assert "layer-control" in html_with_control
    assert len(m.tile_layers) == 1
    assert m.layer_control


def test_tile_layer_subdomains():
    m = Map()
    m.add_tile_layer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        name="OSM",
        attribution="© OpenStreetMap contributors",
        subdomains=["a", "b", "c"],
    )
    tiles = m.sources[0]["definition"]["tiles"]
    assert len(tiles) == 3
    assert (
        "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png" in tiles
        and "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png" in tiles
        and "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png" in tiles
    )
    html = m.render()
    assert "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png" in html
    assert "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png" in html
    assert "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png" in html

def test_overlay_layer_control():
    m = Map()
    m.add_tile_layer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        name="OSM",
        attribution="© OpenStreetMap contributors",
        subdomains=["a", "b", "c"],
    )

    source = {
        "type": "geojson",
        "data": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        },
    }
    layer_id = m.add_layer(
        {
            "id": "points",
            "type": "circle",
            "paint": {"circle-radius": 5, "circle-color": "red"},
        },
        source=source,
    )
    lc = LayerControl()
    lc.add_overlay(layer_id, "Points")
    lc.add_to(m)
    html = m.render()
    assert "overlayLayers" in html
    assert "Points" in html
    assert "checkbox" in html
    assert "setLayoutProperty(ol.id" in html


def test_shapes():
    m = Map()
    Circle([0, 0], radius=1000).add_to(m)
    CircleMarker([1, 1], radius=5).add_to(m)
    PolyLine([[0, 0], [1, 1]]).add_to(m)
    Polygon([[0, 0], [0, 1], [1, 1], [1, 0]], color="red", weight=3, fill_color="blue").add_to(m)
    assert len(m.layers) == 5
    polygon_fill = next(
        l
        for l in m.layers
        if l["definition"]["id"].startswith("polygon_")
        and l["definition"]["type"] == "fill"
    )
    polygon_outline = next(
        l
        for l in m.layers
        if l["definition"]["id"].startswith("polygon_")
        and l["definition"]["type"] == "line"
    )
    assert polygon_fill["definition"]["paint"]["fill-color"] == "blue"
    assert polygon_outline["definition"]["paint"]["line-color"] == "red"
    assert polygon_outline["definition"]["paint"]["line-width"] == 3


def test_rectangle():
    m = Map()
    Rectangle([0, 0], [1, 1], color="red", weight=3, fill_color="blue").add_to(m)
    assert len(m.layers) == 2
    rect_fill = next(
        l
        for l in m.layers
        if l["definition"]["id"].startswith("polygon_")
        and l["definition"]["type"] == "fill"
    )
    rect_outline = next(
        l
        for l in m.layers
        if l["definition"]["type"] == "line"
    )
    assert (
        rect_outline["definition"]["id"]
        == f"{rect_fill['definition']['id']}_outline"
    )
    assert rect_fill["definition"]["paint"]["fill-color"] == "blue"
    assert rect_outline["definition"]["paint"]["line-color"] == "red"


def test_circle_opacity():
    m = Map()
    Circle([0, 0], radius=1000, fill_opacity=0.3).add_to(m)
    layer = m.layers[0]
    assert layer["definition"]["paint"]["fill-opacity"] == 0.3


def test_circlemarker_opacity():
    m = Map()
    CircleMarker([1, 1], radius=5, fill_opacity=0.7).add_to(m)
    layer = m.layers[0]
    assert layer["definition"]["paint"]["circle-opacity"] == 0.7

