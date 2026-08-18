"""Parity test for the slowly-fly-to-a-location MapLibre example."""

from maplibreum.core import Map
from maplibreum.controls import ButtonControl


def test_slowly_fly_with_duration_api():
    """Test using duration instead of speed for slow flying (alternative approach)."""
    
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-74.5, 40],
        zoom=9,
    )

    # Use duration parameter (more intuitive for Python users)
    m.fly_to(
        center=[74.5, 40],
        zoom=9,
        duration=5000,  # 5 seconds - much easier to understand than speed: 0.2
        essential=True
    )

    html = m.render()
    
    # Verify the duration-based approach works
    assert 'map.flyTo({"center": [74.5, 40], "zoom": 9, "duration": 5000, "essential": true});' in html


def test_slowly_fly_with_button_control():
    """Test slowly-fly-to-a-location using ButtonControl (Phase 1 improvement)."""
    
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
        background: #65a3be;
        cursor: pointer;
    }
    """.strip()

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-74.5, 40],
        zoom=9,
        custom_css=button_css,
    )

    # Create a button control that toggles between two locations with slow flying
    button = ButtonControl(
        label="Slow Fly",
        onclick_js="""
        const locations = [[-74.5, 40], [74.5, 40]];
        const currentCenter = map.getCenter();
        const isNearStart = Math.abs(currentCenter.lng + 74.5) < 10;
        const target = isNearStart ? locations[1] : locations[0];
        
        map.flyTo({
            center: target,
            zoom: 9,
            bearing: 0,
            speed: 0.2,
            curve: 1,
            easing: function(t) { return t; },
            essential: true
        });
        """
    )
    
    # Add the button control to the map
    m.add_control(button, position="top-right")

    html = m.render()

    # Verify the map configuration
    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-74.5, 40]' in html
    assert '"zoom": 9' in html
    
    # Verify button control functionality
    assert button.id in html
    assert button.label in html
    assert "buttonControl" in html
    
    # Verify slow fly parameters
    assert "speed: 0.2" in html
    assert "curve: 1" in html
    assert "easing: function(t) { return t; }" in html
