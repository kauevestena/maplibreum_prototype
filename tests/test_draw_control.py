import json
from maplibreum.core import Map


def test_draw_control_snippet():
    m = Map()
    m.add_draw_control()
    html = m.render()
    assert "mapbox-gl-draw.js" in html
    assert "new MapboxDraw" in html


def test_drawn_features_storage():
    m = Map()
    m.add_draw_control()
    sample = {"type": "FeatureCollection", "features": []}
    Map._store_drawn_features(m.map_id, json.dumps(sample))
    assert m.drawn_features == sample
