from maplibreum.core import Map


def test_maplibre_version_override():
    m = Map(maplibre_version="2.4.0")
    html = m.render()
    assert "maplibre-gl@2.4.0" in html
