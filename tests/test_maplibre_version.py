import pytest

from maplibreum.core import MAPLIBRE_VERSION, Map


def test_maplibre_6_is_the_default():
    m = Map()
    html = m.render()
    assert MAPLIBRE_VERSION == "6.0.0"
    assert "maplibre-gl@6.0.0" in html
    assert "dist/maplibre-gl.mjs" in html
    assert "module.getVersion?.()" in html


def test_maplibre_version_override_accepts_newer_versions():
    html = Map(maplibre_version="6.2.0").render()
    assert "maplibre-gl@6.2.0" in html


@pytest.mark.parametrize("version", ["2.4.0", "3.4.0", "5.7.1", "latest"])
def test_maplibre_version_override_rejects_unsupported_versions(version):
    with pytest.raises(ValueError, match="6 or newer"):
        Map(maplibre_version=version)


def test_raw_geojson_is_normalised_to_a_maplibre_source():
    geojson = {
        "type": "Feature",
        "properties": {"name": "test"},
        "geometry": {"type": "Point", "coordinates": [0, 0]},
    }
    map_ = Map()
    map_.add_source("point", geojson)

    assert map_.sources == [
        {
            "name": "point",
            "definition": {"type": "geojson", "data": geojson},
        }
    ]
