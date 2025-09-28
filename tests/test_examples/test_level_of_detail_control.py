from maplibreum import Map


def test_level_of_detail_control():
    style = {
        "version": 8,
        "sources": {
            "numbers": {
                "type": "raster",
                "url": "https://demotiles.maplibre.org/debug-tiles/number/tiles.json",
                "tileSize": 256,
                "maxzoom": 19,
            }
        },
        "layers": [
            {
                "id": "numbers",
                "type": "raster",
                "source": "numbers",
            }
        ],
    }

    m = Map(
        map_style=style,
        center=[0, 0],
        zoom=12,
        pitch=77,
        map_options={
            "hash": True,
            "maxZoom": 22,
            "maxPitch": 85,
        },
    )

    m.set_source_tile_lod_params(9.0, 3.0)

    html = m.render()
    assert "map.setSourceTileLodParams(9.0, 3.0);" in html