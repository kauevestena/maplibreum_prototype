"""Test for add-an-animated-icon-to-the-map MapLibre example."""

import json

import pytest

from maplibreum import Map


def test_add_an_animated_icon_to_the_map():
    """Replicate the animated pulsing dot icon example using maplibreum."""

    # Create the map using the same base style as the original example
    m = Map(map_style="https://demotiles.maplibre.org/style.json")

    # GeoJSON payload for the single point used by the example
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {},
            }
        ],
    }

    geojson_js = json.dumps(geojson_data)

    # JavaScript snippet mirroring the StyleImageInterface pulsing dot
    animation_lines = [
        "const size = 200;",
        "const pulsingDot = {",
        "    width: size,",
        "    height: size,",
        "    data: new Uint8Array(size * size * 4),",
        "    onAdd() {",
        "        const canvas = document.createElement('canvas');",
        "        canvas.width = this.width;",
        "        canvas.height = this.height;",
        "        this.context = canvas.getContext('2d');",
        "    },",
        "    render() {",
        "        const duration = 1000;",
        "        const t = (performance.now() % duration) / duration;",
        "        const radius = (size / 2) * 0.3;",
        "        const outerRadius = (size / 2) * 0.7 * t + radius;",
        "        const context = this.context;",
        "        context.clearRect(0, 0, this.width, this.height);",
        "        context.beginPath();",
        "        context.arc(this.width / 2, this.height / 2, outerRadius, 0, Math.PI * 2);",
        "        context.fillStyle = `rgba(255, 200, 200,${1 - t})`;",
        "        context.fill();",
        "        context.beginPath();",
        "        context.arc(this.width / 2, this.height / 2, radius, 0, Math.PI * 2);",
        "        context.fillStyle = 'rgba(255, 100, 100, 1)';",
        "        context.strokeStyle = 'white';",
        "        context.lineWidth = 2 + 4 * (1 - t);",
        "        context.fill();",
        "        context.stroke();",
        "        this.data = context.getImageData(0, 0, this.width, this.height).data;",
        "        map.triggerRepaint();",
        "        return true;",
        "    }",
        "};",
        "map.addImage('pulsing-dot', pulsingDot, { pixelRatio: 2 });",
        f"map.addSource('animated-points', {geojson_js});",
        "map.addLayer({",
        "    id: 'animated-points',",
        "    type: 'symbol',",
        "    source: 'animated-points',",
        "    layout: {",
        "        'icon-image': 'pulsing-dot'",
        "    }",
        "});",
    ]

    m.add_on_load_js("\n".join(animation_lines))

    # Ensure the custom animation script is recorded
    assert m._on_load_callbacks
    assert any("pulsing-dot" in snippet for snippet in m._on_load_callbacks)
    assert any("triggerRepaint" in snippet for snippet in m._on_load_callbacks)

    # Render HTML and validate critical pieces of the example are present
    html = m._repr_html_()
    assert "demotiles.maplibre.org/style.json" in html
    assert "pulsing-dot" in html
    assert "animated-points" in html
    assert "triggerRepaint" in html
    assert "Uint8Array" in html


if __name__ == "__main__":
    pytest.main([__file__])
