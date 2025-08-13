import json
import re

from maplibreum.core import Map, FeatureGroup, LayerControl


def test_feature_groups_toggle_independently():
    m = Map()

    source1 = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
    layer1 = {"id": "cities", "type": "circle"}
    fg1 = FeatureGroup("Cities")
    fg1.add_layer(layer1, source=source1)
    fg1.add_to(m)

    source2 = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
    layer2 = {"id": "lakes", "type": "circle"}
    fg2 = FeatureGroup("Lakes")
    fg2.add_layer(layer2, source=source2)
    fg2.add_to(m)

    assert m.overlay_groups == {"Cities": ["cities"], "Lakes": ["lakes"]}

    LayerControl().add_to(m)
    html = m.render()

    match = re.search(r"var overlayGroups = (\[.*?\]);", html, re.S)
    assert match is not None
    text = re.sub(r',\s*]', ']', match.group(1))
    text = re.sub(r'name:', '"name":', text)
    text = re.sub(r'layers:', '"layers":', text)
    groups = json.loads(text)
    assert len(groups) == 2
    assert any(g["name"] == "Cities" and g["layers"] == ["cities"] for g in groups)
    assert any(g["name"] == "Lakes" and g["layers"] == ["lakes"] for g in groups)

