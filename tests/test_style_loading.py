from maplibreum import Map


def test_load_style_url():
    m = Map()
    m.load_style("https://demotiles.maplibre.org/style.json")
    source = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
    m.add_circle_layer("points", source)
    html = m.render()
    assert "https://demotiles.maplibre.org/style.json" in html
    assert "\"points\"" in html


def test_load_style_object():
    style = {
        "version": 8,
        "sources": {},
        "layers": [
            {
                "id": "background",
                "type": "background",
                "paint": {"background-color": "#fff"},
            }
        ],
    }
    m = Map()
    m.load_style(style)
    source = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
    m.add_fill_layer("fills", source)
    html = m.render()
    assert "background-color" in html
    assert "\"fills\"" in html
