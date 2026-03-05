from pathlib import Path

from maplibreum import Map, layers, sources
from maplibreum.experimental import GeoJSONFilePicker


def test_view_local_geojson():
    geojson_path = Path(__file__).parent / "data/sample.geojson"
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-8.3226655, 53.7654751],
        zoom=8,
    )
    source = sources.GeoJSONSource.from_file(geojson_path)
    m.add_source("local-geojson-source", source)
    layer = layers.FillLayer(
        id="local-geojson-layer",
        source="local-geojson-source",
        paint={"fill-color": "red", "fill-opacity": 0.5},
    )
    m.add_layer(layer)
    html = m.render()
    assert '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-8.5,53.5],[-8.0,53.5],[-8.0,54.0],[-8.5,54.0],[-8.5,53.5]]]}}]}' in html.replace(
        " ", ""
    ).replace(
        "\\n", ""
    )


def test_view_local_geojson_experimental_with_python_api():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-8.3226655, 53.7654751],
        zoom=8,
    )
    picker = GeoJSONFilePicker(
        button_id="viewbutton",
        source_id="local-geojson-source",
        layer_id="local-geojson-layer",
        paint={"fill-color": "red", "fill-opacity": 0.5},
    )
    picker.add_to(m)

    html = m.render()

    assert "maplibreum-geojson-picker-button" in html
    assert "showOpenFilePicker" in html
    assert "map.addSource('local-geojson-source'" in html
    assert '"id": "local-geojson-layer"' in html
    assert "Your browser does not support File System Access API" in html
