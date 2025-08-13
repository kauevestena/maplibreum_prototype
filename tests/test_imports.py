from maplibreum import Map, Circle, CircleMarker, PolyLine, LayerControl


def test_circle_import():
    m = Map()
    Circle([0, 0], radius=1000).add_to(m)
    assert len(m.layers) == 1


def test_circle_marker_import():
    m = Map()
    CircleMarker([0, 0], radius=5).add_to(m)
    assert len(m.layers) == 1


def test_polyline_import():
    m = Map()
    PolyLine([[0, 0], [1, 1]]).add_to(m)
    assert len(m.layers) == 1


def test_layer_control_import():
    m = Map()
    LayerControl().add_to(m)
    assert m.layer_control

