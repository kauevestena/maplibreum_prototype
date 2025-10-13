
from maplibreum import Map


def test_display_globe_with_atmosphere():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=1.5,
    )
    m.enable_globe()
    m.add_sky_layer(paint={"sky-type": "atmosphere"})
    m.set_fog({"color": "#88c0ff", "high-color": "#ffffff"})

    html = m.render()
    assert '"type": "sky"' in html
    assert "map.setFog" in html
    assert '"projection": {"name": "globe"}' in html
