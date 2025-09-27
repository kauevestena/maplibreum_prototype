"""Parity test for the slowly-fly-to-a-location MapLibre example."""

from maplibreum.core import Map


def test_slowly_fly_to_a_location():
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
