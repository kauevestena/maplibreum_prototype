
def test_enable_rtl_text_plugin_defaults():
    from maplibreum.core import DEFAULT_RTL_PLUGIN_URL, Map

    m = Map()
    m.enable_rtl_text_plugin()

    html = m.render()

    assert "maplibregl.setRTLTextPlugin" in html
    assert DEFAULT_RTL_PLUGIN_URL in html
    assert f'"{DEFAULT_RTL_PLUGIN_URL}"' in html
