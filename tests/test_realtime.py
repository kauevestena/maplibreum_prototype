import requests_mock
from maplibreum.realtime import RealTimeDataSource

def test_realtime_datasource_init():
    data = {"type": "FeatureCollection", "features": []}
    source = RealTimeDataSource(data=data)

    assert source.type == "geojson"
    assert source.data == data
    assert source.to_dict() == {"type": "geojson", "data": data}

def test_realtime_datasource_from_url():
    url = "https://example.com/data.json"
    data = {"type": "FeatureCollection", "features": []}

    with requests_mock.Mocker() as m:
        m.get(url, json=data)

        source = RealTimeDataSource.from_url(url=url, attribution="Test Attribution")

        assert source.type == "geojson"
        assert source.data == data
        # Check if kwargs are passed correctly
        assert source.options["attribution"] == "Test Attribution"
        assert source.to_dict() == {"type": "geojson", "data": data, "attribution": "Test Attribution"}
