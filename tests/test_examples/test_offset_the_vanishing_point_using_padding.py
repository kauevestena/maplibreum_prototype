"""Parity test for the offset-the-vanishing-point-using-padding example."""

from maplibreum.core import Map


def test_offset_the_vanishing_point_using_padding():
    sidebar_css = "\n".join(
        [
            ".rounded-rect { background: white; border-radius: 10px; box-shadow: 0 0 50px -25px black; }",
            ".flex-center { position: absolute; display: flex; justify-content: center; align-items: center; }",
            ".flex-center.left { left: 0; }",
            ".flex-center.right { right: 0; }",
            ".sidebar-content { position: absolute; width: 95%; height: 95%; font-family: Arial, Helvetica, sans-serif; font-size: 32px; color: gray; }",
            ".sidebar-toggle { position: absolute; width: 1.3em; height: 1.3em; display: flex; justify-content: center; align-items: center; cursor: pointer; }",
            ".sidebar-toggle.left { right: -1.5em; }",
            ".sidebar-toggle.right { left: -1.5em; }",
            ".sidebar { transition: transform 1s; z-index: 1; width: 300px; height: 100%; }",
            ".left.collapsed { transform: translateX(-295px); }",
            ".right.collapsed { transform: translateX(295px); }",
        ]
    )

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-77.01866, 38.888],
        zoom=4,
        pitch=60,
        custom_css=sidebar_css,
    )

    m.add_marker(coordinates=[-77.01866, 38.888])

    container_id = m.map_id

    sidebar_js = "\n".join(
        [
            f"const mapContainer = document.getElementById('{container_id}');",
            "const leftSidebar = document.createElement('div');",
            "leftSidebar.id = 'left';",
            "leftSidebar.className = 'sidebar flex-center left collapsed';",
            "leftSidebar.innerHTML = `",
            "    <div class=\"sidebar-content rounded-rect flex-center\">",
            "        Left Sidebar",
            "        <div class=\"sidebar-toggle rounded-rect left\">&rarr;</div>",
            "    </div>",
            "`;",
            "const rightSidebar = document.createElement('div');",
            "rightSidebar.id = 'right';",
            "rightSidebar.className = 'sidebar flex-center right collapsed';",
            "rightSidebar.innerHTML = `",
            "    <div class=\"sidebar-content rounded-rect flex-center\">",
            "        Right Sidebar",
            "        <div class=\"sidebar-toggle rounded-rect right\">&larr;</div>",
            "    </div>",
            "`;",
            "mapContainer.appendChild(leftSidebar);",
            "mapContainer.appendChild(rightSidebar);",
            "function toggleSidebar(id) {",
            "    const elem = document.getElementById(id);",
            "    const classes = elem.className.split(' ');",
            "    const collapsed = classes.indexOf('collapsed') !== -1;",
            "    const padding = {};",
            "    if (collapsed) {",
            "        classes.splice(classes.indexOf('collapsed'), 1);",
            "        padding[id] = 300;",
            "        map.easeTo({ padding, duration: 1000 });",
            "    } else {",
            "        padding[id] = 0;",
            "        classes.push('collapsed');",
            "        map.easeTo({ padding, duration: 1000 });",
            "    }",
            "    elem.className = classes.join(' ');",
            "}",
            "leftSidebar.querySelector('.sidebar-toggle').addEventListener('click', () => toggleSidebar('left'));",
            "rightSidebar.querySelector('.sidebar-toggle').addEventListener('click', () => toggleSidebar('right'));",
            "toggleSidebar('left');",
        ]
    )

    m.add_on_load_js(sidebar_js)

    html = m.render()

    assert '"style": "https://demotiles.maplibre.org/style.json"' in html
    assert '"center": [-77.01866, 38.888]' in html
    assert '"zoom": 4' in html
    assert '"pitch": 60' in html
    assert "map.easeTo({ padding, duration: 1000 });" in html
    assert "padding[id] = 300" in html
