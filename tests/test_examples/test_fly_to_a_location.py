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
    """Test fly-to-a-location using the new Python API approach (Phase 1 improvement)."""
    
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

    # Define the fly action using the existing camera API
    def create_fly_action():
        """Create JavaScript for random fly action."""
        return """
        map.flyTo({
            center: [
                -74.5 + (Math.random() - 0.5) * 10,
                40 + (Math.random() - 0.5) * 10
            ],
            essential: true
        });
        """
    
    # Create a button control with the fly action
    button = ButtonControl(
        label="Fly",
        onclick_js=create_fly_action()
    )
    
    # For now, we'll still need to inject the button creation
    # This is a transitional approach - Phase 1.5
    m.add_on_load_js(f"""
        const flyBtn = document.createElement('button');
        flyBtn.id = '{button.id}';
        flyBtn.className = '{button.css_class}';
        flyBtn.textContent = '{button.label}';
        document.body.appendChild(flyBtn);
        flyBtn.addEventListener('click', () => {{
            {button.onclick_js}
        }});
    """)

    html = m.render()

    # Verify the map configuration
    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-74.5, 40]' in html
    assert '"zoom": 9' in html
    
    # Verify the improved approach still works
    assert "map.flyTo({" in html
    assert "essential: true" in html
    
    # Verify button creation
    assert button.id in html
    assert button.label in html


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
