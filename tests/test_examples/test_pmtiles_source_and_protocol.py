from maplibreum import Map, PMTilesProtocol, PMTilesSource

PMTILES_ARCHIVE = "https://pmtiles.io/protomaps(vector)ODbL_firenze.pmtiles"


def test_pmtiles_source_and_protocol():
    # 1. Initialize map with basic style
    m = Map(
        center=[11.255, 43.7696],
        zoom=12,
    )

    # 2. Register PMTiles protocol
    protocol = PMTilesProtocol()
    protocol.register(m)

    # 3. Create PMTiles source
    source = PMTilesSource(
        url="pmtiles://" + PMTILES_ARCHIVE,
        attribution='© <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>'
    )
    m.add_source("example_source", source)

    # 4. Add layers using the PMTiles source
    m.add_layer({
        "id": "buildings",
        "type": "fill",
        "source": "example_source",
        "source-layer": "landuse",
        "paint": {"fill-color": "steelblue"},
    })

    m.add_layer({
        "id": "roads",
        "type": "line",
        "source": "example_source",
        "source-layer": "roads",
        "paint": {"line-color": "black"},
    })

    m.add_layer({
        "id": "mask",
        "type": "fill",
        "source": "example_source",
        "source-layer": "mask",
        "paint": {"fill-color": "white"},
    })

    html = m.render()

    # Assertions
    assert "https://unpkg.com/pmtiles@3.2.0/dist/pmtiles.js" in html
    assert "pmtiles.Protocol" in html
    assert "maplibregl.addProtocol('pmtiles'" in html
    assert f"pmtiles://{PMTILES_ARCHIVE}" in html
    assert '"example_source"' in html
    assert '"source-layer": "landuse"' in html.replace("\n", "")
    assert '"source-layer": "roads"' in html.replace("\n", "")
