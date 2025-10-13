
from maplibreum import Map
from maplibreum import controls


def test_sky_fog_terrain_configuration():
    """Ensure terrain, fog, sky, and globe helpers emit the expected HTML."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[11.39, 47.28],
        zoom=12,
        pitch=70,
    )

    terrain_source = m.add_dem_source(
        "terrainSource",
        url="https://demotiles.maplibre.org/terrain-tiles/tiles.json",
        tile_size=256,
    )
    m.set_terrain(terrain_source, exaggeration=1.0)
    m.add_sky_layer(
        paint={
            "sky-type": "atmosphere",
            "sky-atmosphere-sun": [0.0, 0.0],
            "sky-atmosphere-color": "#88c0ff",
            "sky-atmosphere-halo-color": "#ffffff",
        }
    )
    m.set_fog(
        {
            "range": [0.8, 5.0],
            "horizon-blend": 0.2,
            "color": "#88c0ff",
            "high-color": "#245bde",
            "space-color": "#000000",
        }
    )
    m.add_control(
        controls.NavigationControl(
            visualizePitch=True,
            showZoom=True,
            showCompass=True,
        )
    )
    m.add_control(controls.TerrainControl(source=terrain_source, exaggeration=1.0))
    m.enable_globe(add_control=True)

    html = m.render()
    assert "map.setTerrain" in html
    assert '"source": "terrainSource"' in html
    assert "map.setFog" in html
    assert '"type": "sky"' in html
    assert "map.addControl(new maplibregl.TerrainControl" in html
    assert "map.addControl(new maplibregl.GlobeControl" in html
    assert '"projection": {"name": "globe"}' in html
