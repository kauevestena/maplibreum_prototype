from maplibreum import Map, controls, sources, layers

def test_3d_terrain():
    m = Map(
        map_style={
            "version": 8,
            "sources": {
                "osm": sources.RasterSource(
                    tiles=["https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"],
                    tileSize=256,
                    attribution="&copy; OpenStreetMap Contributors",
                    maxzoom=19,
                ).__dict__,
                "terrainSource": sources.RasterDemSource(
                    url="https://demotiles.maplibre.org/terrain-tiles/tiles.json",
                    tileSize=256,
                ).__dict__,
                "hillshadeSource": sources.RasterDemSource(
                    url="https://demotiles.maplibre.org/terrain-tiles/tiles.json",
                    tileSize=256,
                ).__dict__,
            },
            "layers": [
                layers.RasterLayer(id="osm", source="osm").to_dict(),
                layers.HillshadeLayer(
                    id="hills",
                    source="hillshadeSource",
                    layout={"visibility": "visible"},
                    paint={"hillshade-shadow-color": "#473B24"},
                ).to_dict(),
            ],
            "terrain": {"source": "terrainSource", "exaggeration": 1},
            "sky": {},
        },
        center=[11.39085, 47.27574],
        zoom=12,
        pitch=70,
        map_options={
            "hash": True,
            "maxZoom": 18,
            "maxPitch": 85,
        },
    )
    m.add_control(
        controls.NavigationControl(
            visualizePitch=True,
            showZoom=True,
            showCompass=True,
        )
    )
    m.add_control(controls.TerrainControl(source="terrainSource", exaggeration=1))
