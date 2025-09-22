"""Test for the add-a-cog-raster-source MapLibre example."""

from maplibreum import Map, layers, sources


def test_add_a_cog_raster_source():
    """Serialize a COG raster source while noting runtime protocol limits.

    The upstream demo registers the ``cog://`` protocol in JavaScript. Within the
    notebook renderer we only ensure the source dictionary matches the MapLibre
    API so that consumers can attach the required protocol shim in front-end
    code.
    """

    m = Map()
    cog_source = sources.RasterSource(
        url="cog://https://maplibre.org/maplibre-gl-js/docs/assets/cog.tif",
        tile_size=256,
        bounds=[-123.0, 36.0, -121.0, 38.0],
    )
    m.add_source("cogSource", cog_source)
    m.add_layer(layers.RasterLayer(id="cog-layer", source="cogSource").to_dict())

    html = m.render()
    assert "cog://" in html
    definition = m.sources[0]["definition"]
    assert definition["url"].startswith("cog://")
    assert definition["bounds"] == [-123.0, 36.0, -121.0, 38.0]
