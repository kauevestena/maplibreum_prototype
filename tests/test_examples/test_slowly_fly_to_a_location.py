"""Parity test for the slowly-fly-to-a-location MapLibre example."""

from maplibreum.core import Map


def test_slowly_fly_to_a_location():
    """Test slowly-fly-to-a-location using original JavaScript injection approach."""
    button_css = """
    .maplibreum-slow-fly {
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
                "const start = [-74.5, 40];",
                "const end = [74.5, 40];",
                "let isAtStart = true;",
                "const slowFly = document.createElement('button');",
                "slowFly.id = 'fly';",
                "slowFly.className = 'maplibreum-slow-fly';",
                "slowFly.textContent = 'Fly';",
                "document.body.appendChild(slowFly);",
                "slowFly.addEventListener('click', () => {",
                "    const target = isAtStart ? end : start;",
                "    isAtStart = !isAtStart;",
                "    map.flyTo({",
                "        center: target,",
                "        zoom: 9,",
                "        bearing: 0,",
                "        speed: 0.2,",
                "        curve: 1,",
                "        easing(t) { return t; },",
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
    assert "speed: 0.2" in html
    assert "curve: 1" in html
    assert "easing(t) { return t; }" in html


def test_slowly_fly_to_a_location_with_python_api():
    """Test slowly-fly-to-a-location using the existing Python API (Phase 1 improvement)."""
    
    button_css = """
    .maplibreum-slow-fly-improved {
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

    # Use the existing fly_to API to demonstrate it already supports slow flying
    # This is a proof that the API already exists and works!
    m.fly_to(
        center=[74.5, 40],  # Fly to the opposite side of the world
        zoom=9,
        bearing=0,
        speed=0.2,  # Slow speed
        curve=1,
        essential=True
    )

    # Create a button for interactive usage (still needs some JS for interaction)
    m.add_on_load_js("""
        const slowFlyBtn = document.createElement('button');
        slowFlyBtn.id = 'slow-fly-improved';
        slowFlyBtn.className = 'maplibreum-slow-fly-improved';
        slowFlyBtn.textContent = 'Slow Fly (API)';
        document.body.appendChild(slowFlyBtn);
        
        const locations = [[-74.5, 40], [74.5, 40]];
        let currentIndex = 0;
        
        slowFlyBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % locations.length;
            const target = locations[currentIndex];
            
            // This demonstrates the same functionality as the API call above
            map.flyTo({
                center: target,
                zoom: 9,
                bearing: 0,
                speed: 0.2,
                curve: 1,
                easing: function(t) { return t; },
                essential: true
            });
        });
    """)

    html = m.render()

    # Verify that the existing API is being used
    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-74.5, 40]' in html
    assert '"zoom": 9' in html
    
    # Verify the API call generated the correct camera action
    assert 'map.flyTo({"center": [74.5, 40], "zoom": 9, "bearing": 0, "speed": 0.2, "curve": 1, "essential": true});' in html
    
    # Verify interactive button still works
    assert "speed: 0.2" in html
    assert "curve: 1" in html


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
