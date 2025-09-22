"""Test for add-a-raster-tile-source MapLibre example."""

from maplibreum import Map, layers, sources


def test_add_a_raster_tile_source():
    """Add a raster tile source and ensure paint/layout survive."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-122.447303, 37.753574],
        zoom=11,
    )

    raster_source = sources.RasterSource(
        tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
        tile_size=256,
        max_zoom=16,
    )
    m.add_source("terrain-tiles", raster_source)

    raster_layer = layers.RasterLayer(id="terrain-tiles", source="terrain-tiles")
    m.add_layer(raster_layer.to_dict())

    html = m.render()
    assert '"type": "raster"' in html
    assert "terrain" in html
    assert len(m.layers) == 1
    definition = m.sources[0]["definition"]
    assert definition["maxzoom"] == 16
