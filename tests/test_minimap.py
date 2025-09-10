import pytest

from maplibreum.core import Map, MiniMapControl, MAP_STYLES


def test_minimap_rendering():
    m = Map()
    m.add_control(MiniMapControl(style="basic", zoom_level=7))
    html = m.render()
    assert "maplibregl-minimap/dist/minimap-control.js" in html
    assert "new MinimapControl" in html
    ctrl = next(c for c in m.controls if c["type"] == "minimap")
    assert ctrl["options"]["style"] == MAP_STYLES["basic"]
    assert ctrl["options"]["zoomLevelOffset"] == 7


def test_minimap_toggle():
    m = Map()
    html_without = m.render()
    assert "maplibregl-minimap" not in html_without
    m.add_control(MiniMapControl())
    html_with = m.render()
    assert "maplibregl-minimap/dist/minimap-control.js" in html_with
