"""Parity test for the animate-a-series-of-images MapLibre example."""

from maplibreum.core import Map
from maplibreum import layers


def test_animate_a_series_of_images():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-75.789, 41.874],
        zoom=5,
        map_options={"minZoom": 4, "maxZoom": 5.99},
    )

    m.add_source(
        "radar",
        {
            "type": "image",
            "url": "https://maplibre.org/maplibre-gl-js/docs/assets/radar0.gif",
            "coordinates": [
                [-80.425, 46.437],
                [-71.516, 46.437],
                [-71.516, 37.936],
                [-80.425, 37.936],
            ],
        },
    )

    m.add_layer(
        layers.RasterLayer(
            id="radar-layer",
            source="radar",
            paint={"raster-fade-duration": 0},
        ).to_dict()
    )

    animation_script = "\n".join(
        [
            "const frameCount = 5;",
            "let currentImage = 0;",
            "function getPath() {",
            "    return `https://maplibre.org/maplibre-gl-js/docs/assets/radar${currentImage}.gif`;",
            "}",
            "setInterval(() => {",
            "    currentImage = (currentImage + 1) % frameCount;",
            "    map.getSource('radar').updateImage({url: getPath()});",
            "}, 200);",
        ]
    )

    m.add_animation(animation_script)

    html = m.render()

    assert '"style": "https://demotiles.maplibre.org/style.json"' in html
    assert '"center": [-75.789, 41.874]' in html
    assert '"zoom": 5' in html
    assert '"minZoom": 4' in html
    assert '"maxZoom": 5.99' in html
    assert 'map.addSource("radar"' in html
    assert "map.getSource('radar').updateImage({url: getPath()});" in html
    assert "setInterval(() => {" in html
