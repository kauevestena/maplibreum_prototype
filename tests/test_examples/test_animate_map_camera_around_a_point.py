"""Parity test for the animate-map-camera-around-a-point example."""

from maplibreum.core import Map
from maplibreum.animation import AnimationLoop


def test_animate_map_camera_around_a_point():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/liberty",
        center=[-87.62712, 41.89033],
        zoom=15.5,
        pitch=45,
    )

    m.add_on_load_js(
        "\n".join(
            [
                "const layers = map.getStyle().layers;",
                "for (let i = 0; i < layers.length; i++) {",
                "    if (layers[i].type === 'symbol' && layers[i].layout && layers[i].layout['text-field']) {",
                "        map.removeLayer(layers[i].id);",
                "    }",
                "}",
            ]
        )
    )

    m.add_animation(
        AnimationLoop(
            name="rotateCamera",
            body="map.rotateTo((timestamp / 100) % 360, {duration: 0});",
        )
    )

    html = m.render()

    assert '"style": "https://tiles.openfreemap.org/styles/liberty"' in html
    assert '"center": [-87.62712, 41.89033]' in html
    assert '"zoom": 15.5' in html
    assert '"pitch": 45' in html
    assert "map.rotateTo((timestamp / 100) % 360, {duration: 0});" in html
    assert "map.removeLayer(layers[i].id);" in html


def test_animate_map_camera_around_a_point_with_python_api():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/liberty",
        center=[-87.62712, 41.89033],
        zoom=15.5,
        pitch=45,
    )
    m.animate_camera_around()
    html = m.render()

    assert '"style": "https://tiles.openfreemap.org/styles/liberty"' in html
    assert '"center": [-87.62712, 41.89033]' in html
    assert '"zoom": 15.5' in html
    assert '"pitch": 45' in html
    assert "function rotateCamera(timestamp)" in html
    assert "map.rotateTo((timestamp * 360 / 36000) % 360, {duration: 0});" in html
