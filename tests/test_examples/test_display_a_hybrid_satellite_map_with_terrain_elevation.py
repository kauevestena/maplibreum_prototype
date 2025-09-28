from maplibreum import Map
from maplibreum.layers import Layer
from maplibreum.controls import NavigationControl, GlobeControl, TerrainControl
from maplibreum.sources import RasterSource, RasterDemSource

def test_display_a_hybrid_satellite_map_with_terrain_elevation():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[11.39085, 47.27574],
        zoom=12,
        pitch=70,
        map_options={"maxPitch": 95},
    )

    m.set_projection({"name": "globe"})

    m.add_source(
        "satelliteSource",
        RasterSource(
            tiles=["https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg"],
            tile_size=256,
        ),
    )

    m.add_dem_source(
        "terrainSource",
        url="https://demotiles.maplibre.org/terrain-tiles/tiles.json",
        tile_size=256,
    )

    m.add_dem_source(
        "hillshadeSource",
        url="https://demotiles.maplibre.org/terrain-tiles/tiles.json",
        tile_size=256,
    )

    m.set_terrain(source_name="terrainSource", exaggeration=1)

    m.set_fog({
        'atmosphere-blend': [
            'interpolate',
            ['linear'],
            ['zoom'],
            0, 1,
            2, 0
        ],
    })

    m.add_layer(
        Layer(
            id="hills",
            type="hillshade",
            source="hillshadeSource",
            layout={"visibility": "visible"},
            paint={"hillshade-shadow-color": "#473B24"},
        )
    )

    satellite_layer = Layer(
        id="satellite",
        type="raster",
        source="satelliteSource",
        layout={"visibility": "visible"},
        paint={"raster-opacity": 1},
    )

    m.add_layer(satellite_layer, before="landuse")


    m.add_control(NavigationControl(visualizePitch=True, showZoom=True, showCompass=True))
    m.add_control(GlobeControl())
    m.add_control(TerrainControl(source="terrainSource", exaggeration=1))

    output_str = m.render()
    output_str_no_spaces = output_str.replace(" ", "")
    assert '"projection":{"name":"globe"}' in output_str_no_spaces
    assert "satelliteSource" in output_str
    assert "terrainSource" in output_str
    assert "hillshadeSource" in output_str
    assert 'map.setTerrain' in output_str
    assert '"id":"hills"' in output_str_no_spaces
    assert '"id":"satellite"' in output_str_no_spaces
    assert '},"landuse");' in output_str_no_spaces
    assert "atmosphere-blend" in output_str