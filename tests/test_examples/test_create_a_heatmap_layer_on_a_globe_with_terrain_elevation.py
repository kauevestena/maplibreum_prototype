"""Test port of the heatmap-on-globe MapLibre example."""

from maplibreum import Map, controls


def test_heatmap_globe_with_terrain():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-122.44, 37.76],
        zoom=5,
    )
    m.enable_globe(add_control=True)

    terrain_source = m.add_dem_source(
        "terrain-dem",
        url="https://demotiles.maplibre.org/terrain-tiles/tiles.json",
        tile_size=256,
    )
    m.set_terrain(terrain_source, exaggeration=1.5)
    m.add_control(controls.TerrainControl(source=terrain_source, exaggeration=1.5))

    earthquakes = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-122.44, 37.76]},
                "properties": {"mag": 4.5},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-122.3, 38.1]},
                "properties": {"mag": 3.7},
            },
        ],
    }

    m.add_source("earthquakes", {"type": "geojson", "data": earthquakes})
    m.add_heatmap_layer(
        "earthquakes-heatmap",
        source="earthquakes",
        paint={
            "heatmap-radius": 30,
            "heatmap-opacity": 0.8,
        },
    )

    html = m.render()
    assert '"type": "heatmap"' in html
    assert '"projection": "globe"' in html
    assert "map.addControl(new maplibregl.GlobeControl" in html
    assert "map.setTerrain" in html
    assert "earthquakes" in html
