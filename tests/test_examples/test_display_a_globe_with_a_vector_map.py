
from maplibreum import Map


def test_display_globe_vector_map():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=1.2,
    )
    m.enable_globe(add_control=True)
    html = m.render()
    assert '"projection": {"name": "globe"}' in html
    assert "map.addControl(new maplibregl.GlobeControl" in html
