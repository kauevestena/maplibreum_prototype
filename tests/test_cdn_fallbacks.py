"""Test CDN fallback functionality in map rendering."""

import pytest
from maplibreum import Map


class TestCDNFallbacks:
    """Test that maps include CDN fallbacks and error handling."""

    def test_map_includes_cdn_fallbacks(self):
        """Test that generated HTML includes CDN fallback mechanisms."""
        m = Map(center=[0, 0], zoom=2)
        html = m.render()

        # Check for fallback loading function
        assert "loadMapLibreGL" in html
        assert "function loadMapLibreGL()" in html

        # Check for multiple CDN URLs
        assert "unpkg.com" in html
        assert "cdn.jsdelivr.net" in html
        assert "cdnjs.cloudflare.com" in html

    def test_map_includes_error_handling(self):
        """Test that generated HTML includes error handling."""
        m = Map(center=[0, 0], zoom=2)
        html = m.render()

        # Check for error handling functions
        assert "showMapError" in html
        assert "function showMapError" in html

        # Check for error messages
        assert "Map Loading Error" in html
        assert "Failed to load MapLibre GL JavaScript library" in html
        assert "network restrictions or CDN availability" in html

    def test_map_includes_css_fallbacks(self):
        """Test that CSS includes fallback mechanisms."""
        m = Map(center=[0, 0], zoom=2)
        html = m.render()

        # Check for CSS error handling
        assert "onerror=" in html
        # Should have fallback from unpkg to jsdelivr
        assert "this.href='https://cdn.jsdelivr.net/npm/maplibre-gl@" in html

    def test_map_initializes_with_try_catch(self):
        """Test that map initialization is wrapped in try-catch."""
        m = Map(center=[0, 0], zoom=2)
        html = m.render()

        # Check for try-catch around initialization
        assert "try {" in html
        assert "} catch (error)" in html
        assert "Error initializing the map" in html

    def test_additional_libraries_have_error_handling(self):
        """Test that additional libraries include error handling."""
        m = Map(center=[0, 0], zoom=2)
        
        # Add controls that require additional libraries
        m.add_control("minimap")
        
        html = m.render()

        # Check that additional scripts have error handlers
        assert "onerror=" in html
        assert "console.warn" in html

    def test_fallback_preserves_map_functionality(self):
        """Test that fallback mechanism doesn't break normal map functionality."""
        m = Map(center=[-74.5, 40], zoom=9, title="Test Map")
        m.add_control("navigation", "top-left")
        
        # Add a layer
        geojson_source = {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {"description": "Test point"},
                    "geometry": {"type": "Point", "coordinates": [-74.5, 40]}
                }]
            }
        }
        
        layer_definition = {
            "id": "test-points",
            "type": "circle",
            "paint": {"circle-radius": 6, "circle-color": "#007cbf"}
        }
        
        m.add_layer(layer_definition, source=geojson_source)
        
        html = m.render()
        
        # Verify normal map elements are still present
        assert "maplibregl.Map" in html
        assert "addControl" in html
        assert "addSource" in html
        assert "addLayer" in html
        assert "test-points" in html

    def test_error_message_styling(self):
        """Test that error message has proper styling."""
        m = Map(center=[0, 0], zoom=2)
        html = m.render()
        
        # Check for styled error display
        assert "🗺️" in html  # Map emoji
        assert "display: flex" in html
        assert "align-items: center" in html
        assert "justify-content: center" in html
        assert "background-color: #f8f9fa" in html
        assert "border: 2px dashed" in html