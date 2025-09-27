from maplibreum import Map
from maplibreum.layers import SymbolLayer
from maplibreum.sources import GeoJSONSource


MISSING_ICON_JS = """
map.on('styleimagemissing', (e) => {
    const id = e.id;
    const prefix = 'square-rgb-';
    if (!id.startsWith(prefix)) {
        return;
    }
    const rgb = id.replace(prefix, '').split(',').map(Number);
    const width = 64;
    const bytesPerPixel = 4;
    const data = new Uint8Array(width * width * bytesPerPixel);
    for (let x = 0; x < width; x++) {
        for (let y = 0; y < width; y++) {
            const offset = (y * width + x) * bytesPerPixel;
            data[offset + 0] = rgb[0];
            data[offset + 1] = rgb[1];
            data[offset + 2] = rgb[2];
            data[offset + 3] = 255;
        }
    }
    map.addImage(id, { width, height: width, data });
});
"""


def test_generate_and_add_a_missing_icon_to_the_map():
    m = Map(map_style="https://demotiles.maplibre.org/style.json")

    points = GeoJSONSource(
        data={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {"color": "255,0,0"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [50, 0]},
                    "properties": {"color": "255,209,28"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-50, 0]},
                    "properties": {"color": "242,127,32"},
                },
            ],
        }
    )

    layer = SymbolLayer(
        id="points",
        source="points",
        layout={"icon-image": ["concat", "square-rgb-", ["get", "color"]]},
    )

    m.add_source("points", points)
    m.add_layer(layer)
    m.add_on_load_js(MISSING_ICON_JS)

    html = m.render()

    assert "styleimagemissing" in html
    assert "map.addImage(id" in html
    assert "square-rgb-" in html
    assert any(source["name"] == "points" for source in m.sources)
    assert any(layer_info["definition"]["layout"]["icon-image"][0] == "concat" for layer_info in m.layers)
