"""Regression test for draw-geometries-with-terra-draw example."""

from __future__ import annotations

from maplibreum import Map
from maplibreum.controls import TerraDrawControl


_TERRA_MODES = [
    "point",
    "linestring",
    "polygon",
    "rectangle",
    "circle",
    "freehand",
    "angled-rectangle",
    "sensor",
    "sector",
    "select",
    "delete-selection",
    "delete",
    "download",
]


def test_draw_geometries_with_terra_draw() -> None:
    """Ensure Terra Draw integration works using the Python API."""

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-91.874, 42.76],
        zoom=12,
    )

    control = TerraDrawControl(
        modes=_TERRA_MODES,
        open=True,
    )
    m.add_control(control)

    # Verify script and CSS are added via the control
    assert any(
        "maplibre-gl-terradraw.umd.js" in script["src"] for script in m.external_scripts
    ), "Terra Draw script not found in external scripts"
    assert "maplibre-gl-terradraw.css" in m.custom_css, "Terra Draw CSS not found in custom CSS"

    # Verify control JS generation
    control_js = control.to_js()
    assert "MaplibreTerradrawControl" in control_js
    assert "modes: ['point', 'linestring', 'polygon'" in control_js
    assert "open: true" in control_js
    assert "map.addControl(terraControl, 'top-left')" in control_js

    # Verify JS injection into map
    assert any(
        "MaplibreTerradrawControl" in js for js in m._extra_js_snippets
    ), "Terra Draw JS snippet not found in extra JS snippets"

    html = m.render()
    assert "maplibre-gl-terradraw.umd.js" in html
    assert "maplibre-gl-terradraw.css" in html
    assert "MaplibreTerradrawControl" in html
