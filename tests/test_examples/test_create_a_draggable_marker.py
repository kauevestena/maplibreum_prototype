"""Test for the create-a-draggable-marker MapLibre example."""

from maplibreum.core import Map


def test_create_a_draggable_marker():
    """Create a default marker that can be dragged on the map."""
    m = Map(center=[0, 0], zoom=2)
    marker = m.add_marker(coordinates=[0, 0], draggable=True)

    assert marker.draggable is True
    html = m.render()
    assert '"draggable": true' in html
