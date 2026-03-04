import pytest
from maplibreum.core import GeoJson
from maplibreum.sources import GeoJSONSource
from maplibreum.choropleth import Choropleth
from maplibreum.cluster import ClusteredGeoJson
from maplibreum.utils import get_geojson_dict

geopandas = pytest.importorskip("geopandas")
from shapely.geometry import Point


@pytest.fixture
def sample_gdf():
    d = {'name': ['A', 'B'], 'value': [1, 2]}
    geometry = [Point(0, 0), Point(1, 1)]
    gdf = geopandas.GeoDataFrame(d, geometry=geometry)
    return gdf


def test_get_geojson_dict(sample_gdf):
    result = get_geojson_dict(sample_gdf)
    assert isinstance(result, dict)
    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) == 2
    assert result["features"][0]["properties"]["name"] == "A"


def test_geojson_with_geodataframe(sample_gdf):
    g = GeoJson(sample_gdf)
    assert isinstance(g.data, dict)
    assert g.data["type"] == "FeatureCollection"
    assert len(g.data["features"]) == 2


def test_geojsonsource_with_geodataframe(sample_gdf):
    s = GeoJSONSource(data=sample_gdf)
    assert isinstance(s.data, dict)
    assert s.data["type"] == "FeatureCollection"


def test_choropleth_with_geodataframe(sample_gdf):
    c = Choropleth(
        geojson=sample_gdf,
        data={'A': 10, 'B': 20},
        key_on="name",
    )
    assert isinstance(c.geojson, dict)
    assert c.geojson["type"] == "FeatureCollection"


def test_clustered_geojson_with_geodataframe(sample_gdf):
    c = ClusteredGeoJson(sample_gdf)
    assert isinstance(c.data, dict)
    assert c.data["type"] == "FeatureCollection"
