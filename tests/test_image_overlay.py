import pytest
from maplibreum.core import Map, ImageOverlay


def test_image_overlay_bounds_and_opacity():
    m = Map()
    image_url = "https://example.com/image.png"
    bounds = [-1.0, -2.0, 3.0, 4.0]
    overlay = ImageOverlay(image_url, bounds=bounds, opacity=0.6, attribution="Demo")
    overlay.add_to(m)

    assert len(m.sources) == 1
    src_def = m.sources[0]["definition"]
    assert src_def["type"] == "image"
    expected_coords = [
        [bounds[0], bounds[3]],
        [bounds[2], bounds[3]],
        [bounds[2], bounds[1]],
        [bounds[0], bounds[1]],
    ]
    assert src_def["coordinates"] == expected_coords
    assert src_def["attribution"] == "Demo"

    assert len(m.layers) == 1
    layer_def = m.layers[0]["definition"]
    assert layer_def["type"] == "raster"
    assert layer_def["paint"]["raster-opacity"] == 0.6

