from maplibreum.core import Map, Marker, FeatureGroup, LayerControl

def test_feature_group_toggles_layers_together():
    m = Map()
    fg = FeatureGroup(name="group1")
    Marker([0, 0]).add_to(fg)
    Marker([1, 1]).add_to(fg)
    fg.add_to(m)
    lc = LayerControl()
    lc.add_overlay(fg, "Group 1")
    lc.add_to(m)
    assert m.overlays[0]["layers"] == fg.layer_ids
    html = m.render()
    for lid in fg.layer_ids:
        assert lid in html
    assert "ol.layers.forEach" in html
