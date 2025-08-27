import pytest
from maplibreum.core import Map


def test_add_image_source():
    m = Map()
    coords = [[-1.0, 1.0], [1.0, 1.0], [1.0, -1.0], [-1.0, -1.0]]
    m.add_image_source("imgsrc", "https://example.com/image.png", coords, attribution="Demo")
    m.add_layer({"id": "img-layer", "type": "raster"}, source="imgsrc")

    assert any(src["name"] == "imgsrc" for src in m.sources)
    src_def = next(src["definition"] for src in m.sources if src["name"] == "imgsrc")
    assert src_def["type"] == "image"
    assert src_def["url"] == "https://example.com/image.png"
    assert src_def["coordinates"] == coords
    assert src_def["attribution"] == "Demo"
    html = m.render()
    assert 'map.addSource("imgsrc"' in html


def test_add_canvas_source():
    m = Map()
    coords = [[0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]
    m.add_canvas_source("cnvsrc", "mycanvas", coords, animate=True)
    m.add_layer({"id": "cnv-layer", "type": "raster"}, source="cnvsrc")

    src_def = next(src["definition"] for src in m.sources if src["name"] == "cnvsrc")
    assert src_def["type"] == "canvas"
    assert src_def["canvas"] == "mycanvas"
    assert src_def["coordinates"] == coords
    assert src_def["animate"] is True
    html = m.render()
    assert 'map.addSource("cnvsrc"' in html
    assert '<canvas id="mycanvas"' in html
