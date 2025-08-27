import pytest
from maplibreum.core import Map


def test_set_paint_property_after_render():
    m = Map()
    source = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
    layer = {"id": "fill", "type": "fill", "paint": {"fill-color": "red"}}
    m.add_layer(layer, source=source)
    m.render()
    m.set_paint_property("fill", "fill-color", "blue")
    assert m.layers[0]["definition"]["paint"]["fill-color"] == "blue"
    html = m.render()
    assert "fill-color\": \"blue\"" in html


def test_set_layout_property_after_render():
    m = Map()
    source = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
    layer = {"id": "symbol", "type": "symbol", "layout": {"icon-image": "marker-15"}}
    m.add_layer(layer, source=source)
    m.render()
    m.set_layout_property("symbol", "visibility", "none")
    assert m.layers[0]["definition"]["layout"]["visibility"] == "none"
    html = m.render()
    assert "visibility\": \"none\"" in html


def test_template_includes_update_functions():
    m = Map()
    html = m.render()
    assert "function setPaintProperty" in html
    assert "function setLayoutProperty" in html
