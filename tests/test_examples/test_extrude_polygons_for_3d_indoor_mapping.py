"""Test for extrude-polygons-for-3d-indoor-mapping example."""
from maplibreum import Map
from maplibreum.layers import FillExtrusionLayer
from maplibreum.sources import GeoJSONSource

URL = "https://maplibre.org/maplibre-gl-js/docs/assets/indoor-3d-map.geojson"


def test_extrude_polygons_for_3d_indoor_mapping():
    """Test recreating the 'extrude-polygons-for-3d-indoor-mapping' MapLibre example."""
    map_options = dict(
        center=[-87.61694, 41.86625],
        zoom=15.99,
        pitch=40,
        bearing=20,
    )

    style = {
        "id": "raster",
        "version": 8,
        "name": "Raster tiles",
        "center": [0, 0],
        "zoom": 0,
        "sources": {
            "raster-tiles": {
                "type": "raster",
                "tiles": ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                "tileSize": 256,
                "minzoom": 0,
                "maxzoom": 19,
            }
        },
        "layers": [
            {"id": "background", "type": "background", "paint": {"background-color": "#e0dfdf"}},
            {"id": "simple-tiles", "type": "raster", "source": "raster-tiles"},
        ],
    }

    m = Map(map_style=style, **map_options)

    source = GeoJSONSource(data=URL)
    m.add_source("floorplan", source)

    layer = FillExtrusionLayer(
        id="room-extrusion",
        source="floorplan",
        paint={
            "fill-extrusion-color": ["get", "color"],
            "fill-extrusion-height": ["get", "height"],
            "fill-extrusion-base": ["get", "base_height"],
            "fill-extrusion-opacity": 0.5,
        },
    )
    m.add_layer(layer)

    # Verify map properties
    assert m.center == [-87.61694, 41.86625]
    assert m.zoom == 15.99
    assert m.pitch == 40
    assert m.bearing == 20

    # Verify source
    assert len(m.sources) == 1
    floorplan_source = m.sources[0]
    assert floorplan_source["name"] == "floorplan"
    assert floorplan_source["definition"]["type"] == "geojson"
    assert floorplan_source["definition"]["data"] == URL

    # Verify layer
    assert len(m.layers) == 1
    extrusion_layer = m.layers[0]
    assert extrusion_layer["definition"]["id"] == "room-extrusion"
    assert extrusion_layer["definition"]["type"] == "fill-extrusion"
    assert extrusion_layer["definition"]["source"] == "floorplan"
    paint = extrusion_layer["definition"]["paint"]
    assert paint["fill-extrusion-color"] == ["get", "color"]
    assert paint["fill-extrusion-height"] == ["get", "height"]
    assert paint["fill-extrusion-base"] == ["get", "base_height"]
    assert paint["fill-extrusion-opacity"] == 0.5

    # Render and verify HTML
    html = m.render()
    assert "room-extrusion" in html
    assert "fill-extrusion" in html
    assert "indoor-3d-map.geojson" in html