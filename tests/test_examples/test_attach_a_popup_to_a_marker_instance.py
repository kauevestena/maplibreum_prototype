"""Test for attach-a-popup-to-a-marker-instance example."""

import pytest
from maplibreum import Map
from maplibreum.markers import DivIcon


def test_attach_a_popup_to_a_marker_instance():
    """Test attaching a popup to a marker instance."""

    # Monument coordinates from the original example
    monument = [-77.0353, 38.8895]

    # Create map with same parameters as original
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json", center=monument, zoom=5
    )

    # Create a custom DivIcon that mimics the original CSS styling
    custom_icon = DivIcon(
        html="<div></div>",  # Need some HTML content for the template to work
        class_name="marker",
    )

    # Add CSS styling that matches the original
    custom_icon.css = """
    #marker {
        background-image: url('https://maplibre.org/maplibre-gl-js/docs/assets/washington-monument.jpg');
        background-size: cover;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        cursor: pointer;
    }
    
    .maplibregl-popup {
        max-width: 200px;
    }
    """

    # Create popup text from the original example
    popup_text = "Construction on the Washington Monument began in 1848."

    # Add marker with popup
    m.add_marker(coordinates=monument, icon=custom_icon, popup=popup_text)

    # Verify marker was added correctly
    assert len(m.markers) == 1

    # Verify marker properties
    marker = m.markers[0]
    assert marker["coordinates"] == monument
    assert marker["popup"] == popup_text
    assert marker["class_name"] == "marker"
    assert "html" in marker

    # Generate HTML and verify content
    html = m._repr_html_()

    # Should contain the map style and coordinates
    assert "demotiles.maplibre.org/style.json" in html
    assert "-77.0353" in html
    assert "38.8895" in html

    # Should contain popup text
    assert "Construction on the Washington Monument began in 1848" in html

    # Should contain monument image reference
    assert "washington-monument.jpg" in html


if __name__ == "__main__":
    test_attach_a_popup_to_a_marker_instance()
    print("✓ attach-a-popup-to-a-marker-instance test passed")
