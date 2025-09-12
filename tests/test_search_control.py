import pytest

from maplibreum.core import Map, SearchControl


def test_search_control_rendering():
    m = Map()
    m.add_search_control(SearchControl(provider="maptiler", api_key="KEY"))
    html = m.render()
    assert "maplibre-gl-geocoder" in html
    assert "new MaplibreGeocoder" in html
    ctrl = next(c for c in m.controls if c["type"] == "search")
    assert ctrl["options"]["provider"] == "maptiler"
    assert ctrl["options"]["apiKey"] == "KEY"


def test_search_control_store_result():
    m = Map()
    m.add_search_control()
    Map._store_search_result(m.map_id, 10, 20)
    assert m.search_result == [10, 20]
