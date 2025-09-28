#!/usr/bin/env python3
"""Test error handling improvements in maplibreum."""

import pytest
from maplibreum import Map
from maplibreum.core import validate_url


class TestErrorHandlingImprovements:
    """Test cases for error handling improvements."""

    def test_validate_url_function(self):
        """Test the URL validation function."""
        # Valid absolute URLs
        assert validate_url("https://example.com/script.js")
        assert validate_url("http://example.com/tiles/{z}/{x}/{y}.png")
        assert validate_url("https://api.example.com/v1/data")
        
        # Valid relative URLs
        assert validate_url("/path/to/script.js", allow_relative=True)
        assert validate_url("../scripts/lib.js", allow_relative=True)
        assert validate_url("script.js", allow_relative=True)
        
        # Invalid URLs
        assert not validate_url("")
        assert not validate_url("   ")
        assert not validate_url(None)
        assert not validate_url(123)
        assert not validate_url("ftp://invalid-scheme.com")  # ftp not typically allowed for scripts
        assert not validate_url("javascript:alert('xss')")
        assert not validate_url("data:text/javascript,alert('xss')")
        
        # Relative URLs when not allowed
        assert not validate_url("/path/to/script.js", allow_relative=False)
        assert not validate_url("script.js", allow_relative=False)

    def test_add_external_script_validation(self):
        """Test that add_external_script validates URLs properly."""
        m = Map()
        
        # Valid URLs should work
        m.add_external_script("https://example.com/script.js")
        m.add_external_script("/path/to/script.js")
        
        # Invalid URLs should raise ValueError
        with pytest.raises(ValueError, match="requires a script URL"):
            m.add_external_script("")
            
        with pytest.raises(ValueError, match="requires a script URL"):
            m.add_external_script("   ")
            
        with pytest.raises(ValueError, match="Invalid script URL format"):
            m.add_external_script("javascript:alert('xss')")
            
        with pytest.raises(ValueError, match="Invalid script URL format"):
            m.add_external_script("data:text/javascript,alert('xss')")

    def test_add_tile_layer_validation(self):
        """Test that add_tile_layer validates URLs and parameters properly."""
        m = Map()
        
        # Valid tile URL should work
        m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png")
        
        # Invalid URLs should raise ValueError
        with pytest.raises(ValueError, match="requires a valid tile URL"):
            m.add_tile_layer("")
            
        with pytest.raises(ValueError, match="requires a valid tile URL"):
            m.add_tile_layer("   ")
            
        with pytest.raises(ValueError, match="Invalid tile URL format"):
            m.add_tile_layer("/relative/path")  # Relative not allowed for tiles
            
        # Invalid parameters should raise ValueError
        with pytest.raises(ValueError, match="tile_size must be a positive integer"):
            m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png", tile_size=0)
            
        with pytest.raises(ValueError, match="tile_size must be a positive integer"):
            m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png", tile_size=-1)
            
        with pytest.raises(ValueError, match="min_zoom must be a non-negative integer"):
            m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png", min_zoom=-1)
            
        with pytest.raises(ValueError, match="max_zoom must be a non-negative integer"):
            m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png", max_zoom=-1)
            
        with pytest.raises(ValueError, match="min_zoom cannot be greater than max_zoom"):
            m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png", min_zoom=10, max_zoom=5)
            
        with pytest.raises(ValueError, match="subdomains must be a list of strings"):
            m.add_tile_layer("https://{s}.example.com/tiles/{z}/{x}/{y}.png", subdomains="abc")
            
        with pytest.raises(ValueError, match="subdomains must be a list of strings"):
            m.add_tile_layer("https://{s}.example.com/tiles/{z}/{x}/{y}.png", subdomains=[1, 2, 3])

    def test_add_tile_layer_with_subdomains(self):
        """Test add_tile_layer with valid subdomains."""
        m = Map()
        
        # Valid subdomains should work
        m.add_tile_layer(
            "https://{s}.example.com/tiles/{z}/{x}/{y}.png", 
            subdomains=["a", "b", "c"]
        )
        
        # Should work even without {s} placeholder
        m.add_tile_layer(
            "https://example.com/tiles/{z}/{x}/{y}.png", 
            subdomains=["a", "b", "c"]  # This should be ignored
        )

    def test_parameter_validation_edge_cases(self):
        """Test edge cases in parameter validation."""
        m = Map()
        
        # Valid edge cases
        m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png", min_zoom=0, max_zoom=0)
        m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png", tile_size=1)
        
        # String representations of numbers should fail
        with pytest.raises(ValueError):
            m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png", tile_size="256")
            
        with pytest.raises(ValueError):
            m.add_tile_layer("https://example.com/tiles/{z}/{x}/{y}.png", min_zoom="0")


if __name__ == '__main__':
    pytest.main([__file__])