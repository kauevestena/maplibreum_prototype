from maplibreum.core import Map, ImageOverlay


def test_image_overlay_bounds_and_opacity():
    m = Map()
    bounds = [[-1, -1], [1, 1]]
    overlay = ImageOverlay(
        "https://example.com/overlay.png",
        bounds=bounds,
        opacity=0.5,
        attribution="Test Image",
    )
    overlay.add_to(m)

    assert len(m.sources) == 1
    source = m.sources[0]["definition"]
    assert source["type"] == "raster"
    assert source["url"] == "https://example.com/overlay.png"
    assert source["coordinates"] == [[-1, 1], [1, 1], [1, -1], [-1, -1]]
    assert source["attribution"] == "Test Image"

    assert len(m.layers) == 1
    layer = m.layers[0]["definition"]
    assert layer["type"] == "raster"
    assert layer["paint"]["raster-opacity"] == 0.5
