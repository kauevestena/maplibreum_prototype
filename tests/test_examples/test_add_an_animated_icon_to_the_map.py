"""Test for add-an-animated-icon-to-the-map MapLibre example."""

import json

import pytest

from maplibreum import Map
from maplibreum.animation import AnimatedIcon


def test_add_an_animated_icon_to_the_map():
    """Test adding an animated icon with the new Python API."""
    m = Map(map_style="https://demotiles.maplibre.org/style.json")

    # Create and add the animated icon
    animated_icon = AnimatedIcon()
    icon_id = m.add_animated_icon(animated_icon)

    # Define the GeoJSON source
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
            }
        ],
    }
    m.add_source("animated-points", {"type": "geojson", "data": geojson_data})

    # Add the symbol layer using the animated icon
    m.add_layer(
        {
            "id": "animated-points-layer",
            "type": "symbol",
            "source": "animated-points",
            "layout": {"icon-image": icon_id},
        }
    )

    # Validate that the JavaScript for the icon is added
    assert any(icon_id in js for js in m._on_load_callbacks)

    # Render and validate HTML
    html = m.render()
    assert f"map.addImage('{icon_id}'" in html
    assert "animated-points-layer" in html
    assert "icon-image" in html


if __name__ == "__main__":
    pytest.main([__file__])
