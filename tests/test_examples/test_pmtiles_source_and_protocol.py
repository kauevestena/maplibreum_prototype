from maplibreum import Map
from maplibreum.protocols import PMTilesProtocol, PMTilesSource

PMTILES_ARCHIVE = "https://pmtiles.io/protomaps(vector)ODbL_firenze.pmtiles"
PMTILES_SCRIPT = "https://unpkg.com/pmtiles@3.2.0/dist/pmtiles.js"


STYLE = {
    "version": 8,
    "sources": {
        "example_source": {
            "type": "vector",
            "url": "pmtiles://" + PMTILES_ARCHIVE, # TODO: check whether is this the best way to define an url
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


LEGACY_PROTOCOL_JS = """
const protocol = new pmtiles.Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);
const archive = new pmtiles.PMTiles('https://pmtiles.io/protomaps(vector)ODbL_firenze.pmtiles');
protocol.add(archive);
"""


def test_pmtiles_helpers_register_protocol_and_source():
    m = Map(
        center=[11.255, 43.7696],
        zoom=12,
    )

    protocol = PMTilesProtocol(credentials="include")
    m.add_pmtiles_protocol(protocol)
    m.add_pmtiles_source(PMTilesSource(archive_url=PMTILES_ARCHIVE, protocol=protocol.name))

    html = m.render()

    assert PMTILES_SCRIPT in html
    assert html.count(PMTILES_SCRIPT) == 1
    assert "pmtiles.Protocol" in html
    assert f"maplibregl.addProtocol('{protocol.name}'" in html
    assert "credentials" in html
    assert PMTILES_ARCHIVE in html


def test_pmtiles_manual_injection_still_supported():
    m = Map(
        map_style=STYLE,
        center=[11.255, 43.7696],
        zoom=12,
    )

    m.add_external_script(PMTILES_SCRIPT)
    m.add_on_load_js(LEGACY_PROTOCOL_JS)

    html = m.render()

    assert PMTILES_SCRIPT in html
    assert "pmtiles.Protocol" in html
    assert "maplibregl.addProtocol('pmtiles'" in html
    assert f"pmtiles://{PMTILES_ARCHIVE}" in html
