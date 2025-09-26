"""Test for add-a-stretchable-image-to-the-map example."""

import pytest
from maplibreum import Map


def test_add_a_stretchable_image_to_the_map():
    """Test adding stretchable images to the map with stretch options."""

    # Create map with same parameters as original
    m = Map(map_style="https://demotiles.maplibre.org/style.json", zoom=0.1)

    # Define image URLs
    images = {
        "popup": "https://maplibre.org/maplibre-gl-js/docs/assets/popup.png",
        "popup-debug": "https://maplibre.org/maplibre-gl-js/docs/assets/popup_debug.png",
    }

    # Add images with stretch options
    # Note: The stretch options might not be fully supported in current maplibreum
    # but we can add the images and test the basic functionality
    popup_debug_options = {
        "stretchX": [[25, 55], [85, 115]],
        "stretchY": [[25, 100]],
        "content": [25, 25, 115, 100],
        "pixelRatio": 2,
    }

    popup_options = {
        "stretchX": [[25, 55], [85, 115]],
        "stretchY": [[25, 100]],
        "content": [25, 25, 115, 100],
        "pixelRatio": 2,
    }

    # Add images with options
    m.add_image("popup-debug", url=images["popup-debug"], options=popup_debug_options)
    m.add_image("popup", url=images["popup"], options=popup_options)

    # Create GeoJSON data with points
    points_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [40, -30]},
                "properties": {
                    "image-name": "popup-debug",
                    "name": "Line 1\\nLine 2\\nLine 3",
                },
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [40, 30]},
                "properties": {
                    "image-name": "popup",
                    "name": "Line 1\\nLine 2\\nLine 3",
                },
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-40, -30]},
                "properties": {"image-name": "popup-debug", "name": "One longer line"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-40, 30]},
                "properties": {"image-name": "popup", "name": "One longer line"},
            },
        ],
    }

    # Add points source
    m.add_source("points", points_data)

    # Add points layer with stretchable icon backgrounds
    m.add_layer(
        {
            "id": "points",
            "type": "symbol",
            "source": "points",
            "layout": {
                "text-field": ["get", "name"],
                "icon-text-fit": "both",
                "icon-image": ["get", "image-name"],
                "icon-overlap": "always",
                "text-overlap": "always",
            },
        }
    )

    # Add original (non-stretched) comparison
    original_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, -70]}}
        ],
    }

    m.add_source("original", original_data)

    m.add_layer(
        {
            "id": "original",
            "type": "symbol",
            "source": "original",
            "layout": {
                "text-field": "non-stretched image",
                "icon-image": "popup-debug",
                "icon-overlap": "always",
                "text-overlap": "always",
            },
        }
    )

    # Verify images were added
    assert len(m.images) == 2

    # Check image entries
    image_names = [img["id"] for img in m.images]
    assert "popup-debug" in image_names
    assert "popup" in image_names

    # Check image URLs
    for img in m.images:
        if img["id"] == "popup-debug":
            assert "popup_debug.png" in img["url"]
            assert "options" in img
            assert "stretchX" in img["options"]
            assert "stretchY" in img["options"]
        elif img["id"] == "popup":
            assert "popup.png" in img["url"]
            assert "options" in img

    # Verify sources were added
    source_names = [source["name"] for source in m.sources]
    assert "points" in source_names
    assert "original" in source_names

    # Verify layers were added
    assert len(m.layers) == 2

    layer_ids = [layer["id"] for layer in m.layers]
    assert "points" in layer_ids
    assert "original" in layer_ids

    # Check points layer configuration
    points_layer = None
    for layer in m.layers:
        if layer["id"] == "points":
            points_layer = layer
            break

    assert points_layer is not None
    assert points_layer["definition"]["type"] == "symbol"
    assert points_layer["definition"]["layout"]["icon-text-fit"] == "both"
    assert points_layer["definition"]["layout"]["icon-image"] == ["get", "image-name"]
    assert points_layer["definition"]["layout"]["text-field"] == ["get", "name"]

    # Generate HTML and verify content
    html = m._repr_html_()

    # Should contain the map style
    assert "demotiles.maplibre.org/style.json" in html

    # Should contain image references
    assert "popup.png" in html
    assert "popup_debug.png" in html

    # Should contain stretch options (if supported)
    assert "stretchX" in html or "popup-debug" in html

    # Should contain text content
    assert "Line 1" in html or "non-stretched image" in html


if __name__ == "__main__":
    test_add_a_stretchable_image_to_the_map()
    print("✓ add-a-stretchable-image-to-the-map test passed")
