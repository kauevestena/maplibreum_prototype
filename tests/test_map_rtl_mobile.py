"""Regression tests for RTL plugin, mobile flags, and projection options."""

from maplibreum import Map


def test_enable_rtl_text_plugin_injects_script():
    m = Map()
    url = "https://example.com/maplibre-gl-rtl-text.js"
    m.enable_rtl_text_plugin(url, lazy=True)

    html = m.render()

    assert "maplibregl.setRTLTextPlugin" in html
    assert "getRTLTextPluginStatus" in html
    assert url in html
    assert "rtlPluginUrl,\n                        null,\n                        true" in html


def test_mobile_behavior_flags_serialised():
    m = Map()
    m.set_mobile_behavior(
        cooperative_gestures=True,
        touch_zoom_rotate=False,
        touch_pitch=False,
        pitch_with_rotate=True,
    )

    html = m.render()

    assert '"cooperativeGestures": true' in html
    assert '"touchZoomRotate": false' in html
    assert '"touchPitch": false' in html
    assert '"pitchWithRotate": true' in html


def test_custom_projection_mapping_serialised():
    projection = {
        "name": "albers",
        "center": [-96, 37.8],
        "parallels": [29.5, 45.5],
    }
    m = Map(map_options={"projection": projection})

    html = m.render()

    assert '"projection": {"name": "albers"' in html
    assert '"parallels": [29.5, 45.5]' in html
    assert '"center": [-96, 37.8]' in html
