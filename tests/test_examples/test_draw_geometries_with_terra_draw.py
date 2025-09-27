"""Regression test for draw-geometries-with-terra-draw example."""

from __future__ import annotations

from maplibreum import Map


_TERRA_DRAW_SCRIPT = (
    "https://cdn.jsdelivr.net/npm/@watergis/maplibre-gl-terradraw@1.0.1/dist/"
    "maplibre-gl-terradraw.umd.js"
)
_TERRA_DRAW_CSS = (
    "@import url('https://cdn.jsdelivr.net/npm/@watergis/maplibre-gl-terradraw@1.0.1/dist/"
    "maplibre-gl-terradraw.css');"
)
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


def _terra_bootstrap_js() -> str:
    modes_js = ", ".join(f"'{mode}'" for mode in _TERRA_MODES)
    return f"""
var terraNamespace = window.MaplibreTerradrawControl || (window.MaplibreTerradrawControl = {{}});
if (typeof terraNamespace.MaplibreTerradrawControl !== 'function') {{
  terraNamespace.MaplibreTerradrawControl = function(options) {{
    this.options = options || {{}};
    this.name = 'mock-terradraw-control';
    this.position = null;
  }};
  terraNamespace.MaplibreTerradrawControl.prototype.onAdd = function(mapInstance) {{
    this._map = mapInstance;
    var container = document.createElement('div');
    container.className = 'mock-terradraw-control';
    container.textContent = 'TerraDraw';
    return container;
  }};
  terraNamespace.MaplibreTerradrawControl.prototype.onRemove = function() {{
    this._map = null;
  }};
}}
var terraControl = new terraNamespace.MaplibreTerradrawControl({{
  modes: [{modes_js}],
  open: true
}});
if (typeof map.addControl === 'function') {{
  map.addControl(terraControl, 'top-left');
}}
"""


def test_draw_geometries_with_terra_draw() -> None:
    """Ensure Terra Draw integration mirrors the gallery example."""

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-91.874, 42.76],
        zoom=12,
        custom_css=_TERRA_DRAW_CSS,
    )
    m.add_external_script(_TERRA_DRAW_SCRIPT)
    m.add_on_load_js(_terra_bootstrap_js())

    assert m.external_scripts[0]["src"] == _TERRA_DRAW_SCRIPT
    assert _TERRA_DRAW_CSS in m.custom_css
    assert len(m._on_load_callbacks) == 1
    assert "MaplibreTerradrawControl" in m._on_load_callbacks[0]
    assert "modes: ['point', 'linestring'" in m._on_load_callbacks[0]

    html = m.render()
    assert _TERRA_DRAW_SCRIPT in html
    assert "mock-terradraw-control" in html
    assert "modes: ['point', 'linestring', 'polygon'" in html
