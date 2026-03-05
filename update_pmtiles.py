content = open('tests/test_examples/test_pmtiles_source_and_protocol.py').read()
if "test_pmtiles_manual_injection_still_supported" in content and "def test_pmtiles_with_python_api():" not in content:
    with open('tests/test_examples/test_pmtiles_source_and_protocol.py', 'w') as f:
        f.write(content + """

def test_pmtiles_with_python_api():
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
""")
