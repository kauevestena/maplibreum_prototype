import pytest
from maplibreum.core import Map


@pytest.fixture
def map_instance():
    return Map()


def test_terrain(map_instance):
    map_instance.add_dem_source("terrain", "https://example.com/dem.png")
    map_instance.set_terrain("terrain", exaggeration=1.2)
    html = map_instance.render()
    source = next(s for s in map_instance.sources if s["name"] == "terrain")
    assert source["definition"]["type"] == "raster-dem"
    assert "setTerrain" in html
    assert '"source": "terrain"' in html


def test_sky_layer(map_instance):
    map_instance.add_sky_layer(
        paint={
            "sky-atmosphere-color": "#88c0ff",
            "sky-atmosphere-halo-color": "#ffffff",
        }
    )
    html = map_instance.render()
    assert not any(l["definition"]["type"] == "sky" for l in map_instance.layers)
    assert "map.setSky" in html
    assert '"sky-color": "#88c0ff"' in html
    assert '"horizon-color": "#ffffff"' in html


def test_fog(map_instance):
    map_instance.set_fog({"color": "#88c0ff", "horizon-blend": 0.2})
    html = map_instance.render()
    assert "map.setSky" in html
    assert "setFog" not in html
    assert '"fog-color": "#88c0ff"' in html
    assert '"horizon-fog-blend": 0.2' in html

