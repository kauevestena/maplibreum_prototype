"""Parity test for the fly-to-a-location MapLibre example."""

from maplibreum.core import Map


def test_fly_to_a_location():
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
