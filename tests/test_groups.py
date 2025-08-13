from maplibreum.core import Map, Circle, CircleMarker, FeatureGroup, LayerControl


def test_feature_group_render_and_toggle():
    m = Map()
    fg = FeatureGroup("TestGroup")
    fg.add_layer(Circle([0, 0], radius=1000))
    fg.add_layer(CircleMarker([1, 1], radius=5))
    fg.add_to(m)
    LayerControl().add_to(m)

    html = m.render()

    # group name should be present in rendered HTML
    assert "TestGroup" in html
    assert "layerGroups" in html

    # all layer ids belonging to the group should appear in the layerGroups mapping
    for layer_id in m.layer_groups["TestGroup"]:
        assert layer_id in html

