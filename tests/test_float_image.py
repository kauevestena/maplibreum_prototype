import pytest
from maplibreum.core import Map, FloatImage

def test_float_image():
    m = Map()
    image_url = "https://example.com/image.png"
    float_image = FloatImage(image_url, bottom=10, left=10, width=100)
    float_image.add_to(m)

    assert len(m.float_images) == 1
    assert m.float_images[0] == float_image

    html = m.render()
    assert image_url in html
    assert "bottom: 10px" in html
    assert "left: 10px" in html
    assert "width: 100px" in html
