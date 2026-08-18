"""Parity test for the fly-to-a-location MapLibre example."""

from maplibreum.core import Map
from maplibreum.controls import ButtonControl


def test_fly_to_a_location():
    """Test fly-to-a-location using improved Python API approach (Phase 1 improvement)."""
    
    # Default button styles that match the original example
    button_css = """
    .maplibreum-button {
        display: block;
        position: absolute;
        top: 20px;
        left: 50%;
        transform: translate(-50%);
        width: 50%;
        height: 40px;
        padding: 10px;
        border: none;
        border-radius: 3px;
        font-size: 12px;
        text-align: center;
        color: #fff;
        background: #ee8a65;
        cursor: pointer;
    }
    """.strip()

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-74.5, 40],
        zoom=9,
        custom_css=button_css,
    )

    # Create a button control with the fly action using proper Python API
    button = ButtonControl(
        label="Fly",
        onclick_js="""
        map.flyTo({
            center: [
                -74.5 + (Math.random() - 0.5) * 10,
                40 + (Math.random() - 0.5) * 10
            ],
            essential: true
        });
        """
    )
    
    # Add the button control to the map using the control system
    # This demonstrates how to properly integrate ButtonControl
    m.add_control(button, position="top-right")

    html = m.render()

    # Verify the map configuration
    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-74.5, 40]' in html
    assert '"zoom": 9' in html
    
    # Verify the improved approach still works
    assert "map.flyTo({" in html
    assert "essential: true" in html
    
    # Verify button control is properly integrated
    assert button.id in html
    assert button.label in html
    assert "buttonControl" in html  # Button control JavaScript code
    assert "maplibregl-ctrl" in html  # MapLibre control styling


