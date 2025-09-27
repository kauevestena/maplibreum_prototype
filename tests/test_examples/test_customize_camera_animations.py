"""Parity test for the customize-camera-animations MapLibre example."""

from maplibreum.core import Map
from maplibreum import layers


def test_customize_camera_animations():
    overlay_css = """
    .map-overlay {
        font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
        position: absolute;
        width: 200px;
        top: 0;
        left: 0;
        padding: 10px;
    }

    .map-overlay .map-overlay-inner {
        background-color: #fff;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        border-radius: 3px;
        padding: 10px;
        margin-bottom: 10px;
    }

    .map-overlay-inner fieldset {
        border: none;
        padding: 0;
        margin: 0 0 10px;
    }

    .map-overlay-inner fieldset:last-child {
        margin: 0;
    }

    .map-overlay-inner select {
        width: 100%;
    }

    .map-overlay-inner button {
        background-color: cornflowerblue;
        color: white;
        border-radius: 5px;
        display: inline-block;
        height: 20px;
        border: none;
        cursor: pointer;
    }

    .map-overlay-inner button:hover {
        background-color: blue;
        box-shadow: inset 0 0 0 3px rgba(0, 0, 0, 0.1);
        transition: background-color 500ms linear;
    }

    .offset > label,
    .offset > input {
        display: inline;
    }

    #animateLabel {
        display: inline-block;
        min-width: 20px;
    }
    """.strip()

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-95, 40],
        zoom=3,
        custom_css=overlay_css,
    )

    m.add_source(
        "center",
        {
            "type": "geojson",
            "data": {"type": "Point", "coordinates": [-94, 40]},
        },
    )

    m.add_layer(
        layers.SymbolLayer(
            id="center",
            source="center",
            layout={
                "text-field": "Center: [-94, 40]",
                "text-font": ["Noto Sans Regular"],
                "text-offset": [0, 0.6],
                "text-anchor": "top",
            },
        ).to_dict()
    )

    m.add_layer(
        layers.CircleLayer(
            id="center-circle",
            source="center",
            paint={"circle-radius": 6, "circle-color": "#007cbf"},
        ).to_dict()
    )

    overlay_js = "\n".join(
        [
            "const overlay = document.createElement('div');",
            "overlay.className = 'map-overlay top';",
            "overlay.innerHTML = `",
            "    <div class=\"map-overlay-inner\">",
            "        <fieldset>",
            "            <label for=\"easing\">Select easing function</label>",
            "            <select id=\"easing\" name=\"easing\">",
            "                <option value=\"easeInCubic\">Ease In Cubic</option>",
            "                <option value=\"easeOutQuint\">Ease Out Quint</option>",
            "                <option value=\"easeInOutCirc\">Ease In/Out Circ</option>",
            "                <option value=\"easeOutBounce\">Ease Out Bounce</option>",
            "            </select>",
            "        </fieldset>",
            "        <fieldset>",
            "            <label for=\"duration\">Set animation duration</label>",
            "            <p id=\"durationValue\"></p>",
            "            <input type=\"range\" id=\"duration\" name=\"duration\" min=\"0\" max=\"10000\" step=\"500\" value=\"1000\" />",
            "        </fieldset>",
            "        <fieldset>",
            "            <label>Animate camera motion</label>",
            "            <label for=\"animate\" id=\"animateLabel\">Yes</label>",
            "            <input type=\"checkbox\" id=\"animate\" name=\"animate\" checked />",
            "        </fieldset>",
            "        <fieldset class=\"offset\">",
            "            <label for=\"offset-x\">Offset-X</label>",
            "            <input type=\"number\" id=\"offset-x\" name=\"offset-x\" min=\"-200\" max=\"200\" step=\"50\" value=\"0\" />",
            "        </fieldset>",
            "        <fieldset class=\"offset\">",
            "            <label for=\"offset-y\">Offset-Y</label>",
            "            <input type=\"number\" id=\"offset-y\" name=\"offset-y\" min=\"-200\" max=\"200\" step=\"50\" value=\"0\" />",
            "            <p>Offsets can be negative</p>",
            "        </fieldset>",
            "        <button type=\"button\" id=\"animateButton\" name=\"test-animation\">Test Animation</button>",
            "    </div>",
            "`;",
            "document.body.appendChild(overlay);",
            "const easingFunctions = {",
            "    easeInCubic(t) {",
            "        return t * t * t;",
            "    },",
            "    easeOutQuint(t) {",
            "        return 1 - Math.pow(1 - t, 5);",
            "    },",
            "    easeInOutCirc(t) {",
            "        return t < 0.5 ?",
            "            (1 - Math.sqrt(1 - Math.pow(2 * t, 2))) / 2 :",
            "            (Math.sqrt(1 - Math.pow(-2 * t + 2, 2)) + 1) / 2;",
            "    },",
            "    easeOutBounce(t) {",
            "        const n1 = 7.5625;",
            "        const d1 = 2.75;",
            "        if (t < 1 / d1) {",
            "            return n1 * t * t;",
            "        } else if (t < 2 / d1) {",
            "            return n1 * (t -= 1.5 / d1) * t + 0.75;",
            "        } else if (t < 2.5 / d1) {",
            "            return n1 * (t -= 2.25 / d1) * t + 0.9375;",
            "        }",
            "        return n1 * (t -= 2.625 / d1) * t + 0.984375;",
            "    }",
            "};",
            "const durationValueSpan = document.getElementById('durationValue');",
            "const durationInput = document.getElementById('duration');",
            "durationValueSpan.innerHTML = `${durationInput.value / 1000} seconds`;",
            "durationInput.addEventListener('change', (e) => {",
            "    durationValueSpan.innerHTML = `${e.target.value / 1000} seconds`;",
            "});",
            "const animateLabel = document.getElementById('animateLabel');",
            "const animateValue = document.getElementById('animate');",
            "animateValue.addEventListener('change', (e) => {",
            "    animateLabel.innerHTML = e.target.checked ? 'Yes' : 'No';",
            "});",
            "const animateButton = document.getElementById('animateButton');",
            "animateButton.addEventListener('click', () => {",
            "    const easingInput = document.getElementById('easing');",
            "    const easingFn = easingFunctions[easingInput.options[easingInput.selectedIndex].value];",
            "    const duration = parseInt(durationInput.value, 10);",
            "    const animate = animateValue.checked;",
            "    const offsetX = parseInt(document.getElementById('offset-x').value, 10);",
            "    const offsetY = parseInt(document.getElementById('offset-y').value, 10);",
            "    const animationOptions = {",
            "        duration,",
            "        easing: easingFn,",
            "        offset: [offsetX, offsetY],",
            "        animate,",
            "        essential: true",
            "    };",
            "    const center = [",
            "        -95 + (Math.random() - 0.5) * 20,",
            "        40 + (Math.random() - 0.5) * 20",
            "    ];",
            "    animationOptions.center = center;",
            "    map.flyTo(animationOptions);",
            "    map.getSource('center').setData({",
            "        'type': 'Point',",
            "        'coordinates': center",
            "    });",
            "    map.setLayoutProperty(",
            "        'center',",
            "        'text-field',",
            "        `Center: [${center[0].toFixed(1)}, ${center[1].toFixed(1)}]`",
            "    );",
            "});",
        ]
    )

    m.add_on_load_js(overlay_js)

    html = m.render()

    assert '"style": "https://demotiles.maplibre.org/style.json"' in html
    assert '"center": [-95, 40]' in html
    assert '"zoom": 3' in html
    assert 'map.addSource("center"' in html
    assert "map.flyTo(animationOptions);" in html
    assert "animationOptions.center = center" in html
    assert "map.setLayoutProperty(\n        'center'" in html
