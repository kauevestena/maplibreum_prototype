
import pytest
from maplibreum.controls import GeocodingControl
from maplibreum.core import Map

def test_geocoding_control_init():
    """Test GeocodingControl initialization."""
    # Test default initialization
    ctrl = GeocodingControl()
    assert ctrl.api_url is None
    assert ctrl.position == "top-left"
    assert ctrl.placeholder == "Search"
    assert ctrl.marker is True
    assert ctrl.show_result_popup is True
    assert ctrl.kwargs == {}
    assert ctrl.id.startswith("geocoding_")

    # Test custom initialization
    ctrl_custom = GeocodingControl(
        api_url="https://api.example.com",
        position="bottom-right",
        placeholder="Find place",
        marker=False,
        show_result_popup=False,
        limit=5
    )
    assert ctrl_custom.api_url == "https://api.example.com"
    assert ctrl_custom.position == "bottom-right"
    assert ctrl_custom.placeholder == "Find place"
    assert ctrl_custom.marker is False
    assert ctrl_custom.show_result_popup is False
    assert ctrl_custom.kwargs == {"limit": 5}

def test_geocoding_control_to_dict():
    """Test serialization to dictionary."""
    ctrl = GeocodingControl(api_url="http://test.com", limit=10)
    data = ctrl.to_dict()

    assert data["id"] == ctrl.id
    assert data["api_url"] == "http://test.com"
    assert data["position"] == "top-left"
    assert data["limit"] == 10
    assert data["marker"] is True

def test_geocoding_control_to_js_custom_api():
    """Test JS generation with custom API URL."""
    api_url = "https://my.geocoder.com/search"
    ctrl = GeocodingControl(api_url=api_url)
    js = ctrl.to_js()

    assert "new MaplibreGeocoder" in js
    assert f"fetch(`{api_url}" in js
    assert "map.addControl(geocoder, 'top-left')" in js

def test_geocoding_control_to_js_mock_api():
    """Test JS generation with default mock API."""
    ctrl = GeocodingControl()
    js = ctrl.to_js()

    assert "new MaplibreGeocoder" in js
    assert "nominatimResponse" in js
    assert "Museum Campus" in js  # Part of the hardcoded mock response
    assert "map.addControl(geocoder, 'top-left')" in js

def test_map_add_geocoding_control():
    """Test adding GeocodingControl to a Map instance."""
    m = Map()
    ctrl = GeocodingControl(placeholder="Find location")
    m.add_control(ctrl)

    # Verify control added to map controls list
    assert len(m.controls) == 1
    assert m.controls[0]["type"] == "geocoding"
    assert m.controls[0]["options"]["placeholder"] == "Find location"

    # Verify HTML rendering
    html = m.render()

    # Check for library assets injection
    assert "maplibre-gl-geocoder.css" in html
    assert "maplibre-gl-geocoder.min.js" in html

    # Check for control initialization JS
    assert "new MaplibreGeocoder" in html
    assert "placeholder: 'Find location'" in html
