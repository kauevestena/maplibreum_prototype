"""Parity test for the fly-to-a-location MapLibre example."""

from maplibreum.core import Map
from maplibreum.controls import ButtonControl


def test_fly_to_a_location():
    """Test fly-to-a-location using the original JavaScript injection approach."""
    button_css = """
    .maplibreum-fly-button {
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

    m.add_on_load_js(
        "\n".join(
            [
                "const flyButton = document.createElement('button');",
                "flyButton.id = 'fly';",
                "flyButton.className = 'maplibreum-fly-button';",
                "flyButton.textContent = 'Fly';",
                "document.body.appendChild(flyButton);",
                "flyButton.addEventListener('click', () => {",
                "    map.flyTo({",
                "        center: [",
                "            -74.5 + (Math.random() - 0.5) * 10,",
                "            40 + (Math.random() - 0.5) * 10",
                "        ],",
                "        essential: true",
                "    });",
                "});",
            ]
        )
    )

    html = m.render()

    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-74.5, 40]' in html
    assert '"zoom": 9' in html
    assert "map.flyTo({" in html
    assert "essential: true" in html


def test_fly_to_a_location_with_python_api():
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
    m.add_control(button, position="top-center")

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


def test_fly_to_a_location_with_existing_api():
    """Test fly-to-a-location using the existing camera action API (best current approach)."""
    
    button_css = """
    .maplibreum-fly-button {
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

    # Use the existing fly_to API method
    # This demonstrates that the functionality already exists!
    m.fly_to(center=[-74.5 + 2, 40 + 2], zoom=12, essential=True)

    # Still need a button for interaction, but this shows the API works
    m.add_on_load_js("""
        const flyButton = document.createElement('button');
        flyButton.id = 'fly-existing';
        flyButton.className = 'maplibreum-fly-button';
        flyButton.textContent = 'Fly (Existing API)';
        document.body.appendChild(flyButton);
        flyButton.addEventListener('click', () => {
            // This demonstrates we could trigger more camera actions from buttons
            map.flyTo({
                center: [
                    -74.5 + (Math.random() - 0.5) * 10,
                    40 + (Math.random() - 0.5) * 10
                ],
                essential: true
            });
        });
    """)

    html = m.render()

    # Verify the map configuration
    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-74.5, 40]' in html
    assert '"zoom": 9' in html
    
    # Verify that the existing camera action API is used
    assert 'map.flyTo({"center": [-72.5, 42], "zoom": 12, "essential": true});' in html
    
    # Verify button still works for interaction
    assert "map.flyTo({" in html
    assert "essential: true" in html
