import pytest
from maplibreum.core import Map
from maplibreum.layers import SymbolLayer
from maplibreum.sources import GeoJSONSource


def test_add_live_realtime_data():
    """Test live data fetching using improved Python API (Phase 2 improvement).
    
    This version eliminates JavaScript injection by:
    1. Using RandomCoordinateFetcher class for specialized random.org API
    2. Using LiveDataFetcher for generic data fetching scenarios
    3. Providing configurable transform functions and fly-to behavior
    4. Clean Python API for real-time data configuration
    """
    from maplibreum.realtime import RandomCoordinateFetcher
    from maplibreum.layers import SymbolLayer
    
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        zoom=2,
    )
    
    # Create fetcher with Python API
    drone_fetcher = RandomCoordinateFetcher(
        source_id="drone",
        interval=2000,
        fly_to=True,
        fly_speed=0.5
    )
    
    # Add source with initial data
    m.add_source("drone", {"type": "geojson", "data": drone_fetcher.get_initial_data()})
    
    # Add layer
    drone_layer = SymbolLayer(
        id="drone",
        source="drone",
        layout={"icon-image": "airport"},
    )
    m.add_layer(drone_layer)
    
    # Add fetcher JavaScript
    m.add_on_load_js(drone_fetcher.to_js())
    
    html = m.render()
    
    # Verify Python API usage
    assert '"zoom": 2' in html
    assert 'map.addSource("drone"' in html
    assert '"icon-image": "airport"' in html
    
    # Verify LiveDataFetcher is present
    assert "window.setInterval" in html
    assert "fetch('https://www.random.org" in html
    assert "decimal-fractions" in html
    
    # Verify transform function
    assert "transformData" in html or "rawText.split" in html
    assert "(Number(l) * 180) - 90" in html
    
    # Verify source update logic
    assert "map.getSource('drone')" in html
    assert ".setData(" in html
    
    # Verify fly-to logic
    assert "map.flyTo" in html
    assert "speed: 0.5" in html
    
    # Verify error handling
    assert "catch" in html
    assert "console.error" in html or "Error fetching" in html
