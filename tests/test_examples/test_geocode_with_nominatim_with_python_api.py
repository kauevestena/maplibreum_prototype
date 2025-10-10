from maplibreum import Map
from maplibreum.controls import GeocodingControl


def test_geocode_with_nominatim_with_python_api():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-87.61694, 41.86625],
        zoom=15.99,
        pitch=40,
        bearing=20,
    )

    m.add_control(GeocodingControl())

    html = m.render()

    assert "maplibre-gl-geocoder.css" in html
    assert "maplibre-gl-geocoder.min.js" in html
    assert "new MaplibreGeocoder" in html
    assert "forwardGeocode" in html