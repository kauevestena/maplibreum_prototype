from maplibreum.core import Map, Marker


def test_draggable_marker_updates_coordinates_and_js():
    m = Map()
    marker = Marker(coordinates=[0, 0], popup="Drag me", draggable=True)
    marker.add_to(m)

    # Draggable markers are stored separately from layers
    assert len(m.layers) == 0
    assert len(m.markers) == 1
    assert m.markers[0]["draggable"] is True
    assert marker.id == m.markers[0]["id"]

    html = m.render()
    assert '"draggable": true' in html

    # Simulate drag event
    Map._update_marker_coords(m.map_id, marker.id, 10, 20)
    assert marker.coordinates == [10, 20]
