from maplibreum.core import Map, Marker, Circle, Tooltip


def test_marker_tooltip_render():
    m = Map()
    Marker([0, 0], tooltip=Tooltip("Marker tip")).add_to(m)
    assert len(m.tooltips) == 1
    html = m.render()
    assert "Marker tip" in html
    assert "tooltip_1" in html
    assert '"closeButton": false' in html


def test_circle_tooltip_render():
    m = Map()
    Circle([0, 0], tooltip=Tooltip("Circle tip")).add_to(m)
    html = m.render()
    assert "Circle tip" in html
