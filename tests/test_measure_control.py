import json
from maplibreum.core import Map


def test_measure_control_snippet():
    m = Map()
    m.add_measure_control()
    html = m.render()
    assert "maplibre-gl-measures.js" in html
    assert "mapbox-gl-draw.css" in html
    assert "new maplibreGLMeasures" in html


def test_measure_features_storage():
    m = Map()
    m.add_measure_control()
    sample = {"type": "FeatureCollection", "features": []}
    Map._store_drawn_features(m.map_id, json.dumps(sample))
    assert m.drawn_features == sample
