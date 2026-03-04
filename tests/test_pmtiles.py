"""Tests for PMTiles integration."""

import pytest
from maplibreum.pmtiles import PMTilesSource, PMTilesProtocol
from maplibreum.core import Map

def test_pmtiles_source_init_basic():
    """Test basic initialization of PMTilesSource."""
    url = "pmtiles://https://example.com/data.pmtiles"
    source = PMTilesSource(url=url)

    assert source.type == "vector"
    assert source.options["url"] == url

def test_pmtiles_source_auto_prefix():
    """Test PMTilesSource automatically prefixes pmtiles:// for .pmtiles extensions."""
    # Local file without protocol
    url = "data.pmtiles"
    source = PMTilesSource(url=url)
    assert source.options["url"] == "pmtiles://data.pmtiles"

    # URL without protocol but with .pmtiles extension
    url2 = "example.com/data.pmtiles"
    source2 = PMTilesSource(url=url2)
    assert source2.options["url"] == "pmtiles://example.com/data.pmtiles"

def test_pmtiles_source_no_prefix_https():
    """Test PMTilesSource doesn't prefix if starts with https://."""
    url = "https://example.com/data.pmtiles"
    source = PMTilesSource(url=url)
    assert source.options["url"] == url

def test_pmtiles_source_kwargs():
    """Test PMTilesSource with additional arguments."""
    url = "pmtiles://data.pmtiles"
    source = PMTilesSource(
        url=url,
        attribution="Test Attribution",
        min_zoom=0,
        max_zoom=14,
        promote_id="test_id"
    )

    assert source.options["attribution"] == "Test Attribution"
    assert source.options["minzoom"] == 0
    assert source.options["maxzoom"] == 14
    assert source.options["promote_id"] == "test_id"

def test_pmtiles_source_to_dict():
    """Test PMTilesSource serialization to dictionary."""
    url = "pmtiles://data.pmtiles"
    source = PMTilesSource(url=url, attribution="Test", min_zoom=1)

    result = source.to_dict()
    assert result == {
        "type": "vector",
        "url": url,
        "attribution": "Test",
        "minzoom": 1
    }

def test_pmtiles_protocol_init():
    """Test PMTilesProtocol initialization."""
    protocol = PMTilesProtocol()
    assert "unpkg.com/pmtiles" in protocol.script_url

    custom_url = "https://custom.cdn/pmtiles.js"
    protocol_custom = PMTilesProtocol(script_url=custom_url)
    assert protocol_custom.script_url == custom_url

def test_pmtiles_protocol_register():
    """Test PMTilesProtocol registration on a Map instance."""
    protocol = PMTilesProtocol()
    m = Map(center=[0, 0], zoom=2)

    # Register protocol
    protocol.register(m)

    # Check if external script was added
    scripts_urls = [s.get("src") for s in m.external_scripts]
    assert protocol.script_url in scripts_urls

    # Check if JavaScript code was added to on_load_js
    js_code = "\n".join(m._on_load_callbacks)
    assert "if (typeof pmtiles === 'undefined')" in js_code
    assert "pmtiles.Protocol()" in js_code
    assert "maplibregl.addProtocol('pmtiles'" in js_code


def test_pmtiles_protocol_register_custom_url():
    """Test PMTilesProtocol registration with a custom URL on a Map instance."""
    custom_url = "https://example.com/pmtiles.js"
    protocol = PMTilesProtocol(script_url=custom_url)
    m = Map(center=[0, 0], zoom=2)

    protocol.register(m)

    scripts_urls = [s.get("src") for s in m.external_scripts]
    assert custom_url in scripts_urls
    assert "unpkg.com/pmtiles" not in scripts_urls


def test_pmtiles_protocol_register_multiple_times():
    """Test calling PMTilesProtocol registration multiple times on the same map."""
    protocol = PMTilesProtocol()
    m = Map(center=[0, 0], zoom=2)

    protocol.register(m)
    protocol.register(m)

    scripts_urls = [s.get("src") for s in m.external_scripts]
    # Should only be appended once to avoid duplicate injection
    assert scripts_urls.count(protocol.script_url) == 1

    js_code = "\n".join(m._on_load_callbacks)
    # The registration script should appear only once to prevent maplibregl exceptions
    assert js_code.count("maplibregl.addProtocol('pmtiles'") == 1


def test_pmtiles_protocol_playwright(page):
    """Integration test using Playwright to verify protocol registration logic."""
    import tempfile
    import os

    protocol = PMTilesProtocol()
    m = Map(center=[0, 0], zoom=2)
    protocol.register(m)

    html = m.render()

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
        f.write(html)
        temp_file = f.name

    try:
        # Load the HTML page into the browser
        page.goto(f"file://{os.path.abspath(temp_file)}")

        # Wait for the map to be fully loaded (maplibregl creates a canvas)
        page.wait_for_selector(".maplibregl-canvas")

        # Verify pmtiles is loaded and available
        is_pmtiles_defined = page.evaluate("typeof pmtiles !== 'undefined'")
        assert is_pmtiles_defined is True

        # Verify the map was initialized
        is_maplibregl_defined = page.evaluate("typeof maplibregl !== 'undefined'")
        assert is_maplibregl_defined is True

    finally:
        os.unlink(temp_file)
