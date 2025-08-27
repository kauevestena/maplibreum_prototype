from maplibreum import Map, LatLngPopup


def test_lat_lng_popup_render():
    m = Map()
    LatLngPopup().add_to(m)
    html = m.render()
    assert "e.lngLat.lat" in html
    assert "Lat: " in html
