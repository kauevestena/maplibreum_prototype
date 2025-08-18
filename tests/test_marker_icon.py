from maplibreum.core import Map, Marker, Icon


def test_marker_with_icon_creates_symbol_layer_and_popup():
    m = Map()
    icon = Icon(icon_image="custom-icon", icon_size=2.0, icon_anchor="bottom")
    marker = Marker(coordinates=[-74.5, 40], popup="Icon marker", icon=icon)
    marker.add_to(m)

    assert m.layers[0]["definition"]["type"] == "symbol"
    layout = m.layers[0]["definition"]["layout"]
    assert layout["icon-image"] == "custom-icon"
    assert layout["icon-size"] == 2.0
    assert layout["icon-anchor"] == "bottom"

    assert len(m.popups) == 1
    assert m.popups[0]["html"] == "Icon marker"
    assert m.popups[0]["layer_id"] == m.layers[0]["id"]
