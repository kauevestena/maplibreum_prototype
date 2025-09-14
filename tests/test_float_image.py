import pytest
from maplibreum.core import Map


@pytest.mark.parametrize(
    "position, css_rules",
    [
        ("top-left", ("top: 0px", "left: 0px")),
        ("top-right", ("top: 0px", "right: 0px")),
        ("bottom-left", ("bottom: 0px", "left: 0px")),
        ("bottom-right", ("bottom: 0px", "right: 0px")),
    ],
)
def test_float_image_positions(position, css_rules):
    m = Map()
    image_url = "https://example.com/image.png"
    m.add_float_image(image_url, position=position)

    assert len(m.float_images) == 1

    html = m.render()
    assert image_url in html
    for rule in css_rules:
        assert rule in html

