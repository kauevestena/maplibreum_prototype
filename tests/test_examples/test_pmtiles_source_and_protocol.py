from maplibreum import Map

PMTILES_ARCHIVE = "https://pmtiles.io/protomaps(vector)ODbL_firenze.pmtiles"
PMTILES_SCRIPT = "https://unpkg.com/pmtiles@3.2.0/dist/pmtiles.js"


PROTOCOL_JS = """
const protocol = new pmtiles.Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);
const archive = new pmtiles.PMTiles('https://pmtiles.io/protomaps(vector)ODbL_firenze.pmtiles');
protocol.add(archive);
"""


STYLE = {
    "version": 8,
    "sources": {
        "example_source": {
            "type": "vector",
            "url": "pmtiles://" + PMTILES_ARCHIVE,
            "attribution": '© <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
        }
    },
    "layers": [
        {
            "id": "buildings",
            "type": "fill",
            "source": "example_source",
            "source-layer": "landuse",
            "paint": {"fill-color": "steelblue"},
        },
        {
            "id": "roads",
            "type": "line",
            "source": "example_source",
            "source-layer": "roads",
            "paint": {"line-color": "black"},
        },
        {
            "id": "mask",
            "type": "fill",
            "source": "example_source",
            "source-layer": "mask",
            "paint": {"fill-color": "white"},
        },
    ],
}


def test_pmtiles_source_and_protocol():
    m = Map(
        map_style=STYLE,
        center=[11.255, 43.7696],
        zoom=12,
    )

    m.add_external_script(PMTILES_SCRIPT)
    m.add_on_load_js(PROTOCOL_JS)

    html = m.render()

    assert PMTILES_SCRIPT in html
    assert "pmtiles.Protocol" in html
    assert "maplibregl.addProtocol('pmtiles'" in html
    assert f"pmtiles://{PMTILES_ARCHIVE}" in html
    assert '"example_source"' in html
    assert '"source-layer": "landuse"' in html.replace("\n", "")
    assert '"source-layer": "roads"' in html.replace("\n", "")
