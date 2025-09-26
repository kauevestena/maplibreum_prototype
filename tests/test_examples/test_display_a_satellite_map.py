"""Test for display-a-satellite-map example."""

import pytest
from maplibreum import Map


def test_display_a_satellite_map():
    """Test displaying a satellite map with raster tiles."""
    
    # Create the satellite style as defined in the original example
    satellite_style = {
        "version": 8,
        "sources": {
            "satellite": {
                "type": "raster",
                "tiles": [
                    "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg"
                ],
                "tileSize": 256
            }
        },
        "layers": [{
            "id": "satellite",
            "type": "raster",
            "source": "satellite"
        }]
    }
    
    # Create map with same parameters as original
    m = Map(
        map_style=satellite_style,
        center=[137.9150899566626, 36.25956997955441],
        zoom=9
    )
    
    # Verify map configuration
    assert m.center == [137.9150899566626, 36.25956997955441]
    assert m.zoom == 9
    assert isinstance(m.map_style, dict)
    assert m.map_style["version"] == 8
    
    # Verify the satellite source
    assert "satellite" in m.map_style["sources"]
    satellite_source = m.map_style["sources"]["satellite"]
    assert satellite_source["type"] == "raster"
    assert len(satellite_source["tiles"]) == 1
    assert "tiles.maps.eox.at" in satellite_source["tiles"][0]
    assert satellite_source["tileSize"] == 256
    
    # Verify the satellite layer
    assert len(m.map_style["layers"]) == 1
    satellite_layer = m.map_style["layers"][0]
    assert satellite_layer["id"] == "satellite"
    assert satellite_layer["type"] == "raster"
    assert satellite_layer["source"] == "satellite"
    
    # Generate HTML and verify content
    html = m._repr_html_()
    
    # Should contain the map center and zoom
    assert '137.9150899566626' in html
    assert '36.25956997955441' in html
    
    # Should contain satellite imagery URL
    assert 'tiles.maps.eox.at' in html
    assert 's2cloudless-2020_3857' in html


if __name__ == "__main__":
    test_display_a_satellite_map()
    print("✓ display-a-satellite-map test passed")