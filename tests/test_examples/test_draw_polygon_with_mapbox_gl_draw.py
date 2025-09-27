"""Regression test for draw-polygon-with-mapbox-gl-draw example."""

from __future__ import annotations

from maplibreum import Map


_CALCULATION_CSS = """
.calculation-box {
    height: 75px;
    width: 150px;
    position: absolute;
    bottom: 40px;
    left: 10px;
    background-color: rgba(255, 255, 255, 0.9);
    padding: 15px;
    text-align: center;
    z-index: 1000;
}
.calculation-box p {
    font-family: 'Open Sans';
    margin: 0;
    font-size: 13px;
}
"""

_DRAW_STYLES = [
    {
        "id": "gl-draw-polygon-fill-inactive",
        "type": "fill",
        "filter": [
            "all",
            ["==", "active", "false"],
            ["==", "$type", "Polygon"],
            ["!=", "mode", "static"],
        ],
        "paint": {
            "fill-color": "#3bb2d0",
            "fill-outline-color": "#3bb2d0",
            "fill-opacity": 0.1,
        },
    },
    {
        "id": "gl-draw-polygon-fill-active",
        "type": "fill",
        "filter": ["all", ["==", "active", "true"], ["==", "$type", "Polygon"]],
        "paint": {
            "fill-color": "#fbb03b",
            "fill-outline-color": "#fbb03b",
            "fill-opacity": 0.1,
        },
    },
    {
        "id": "gl-draw-polygon-midpoint",
        "type": "circle",
        "filter": [
            "all",
            ["==", "$type", "Point"],
            ["==", "meta", "midpoint"],
        ],
        "paint": {"circle-radius": 3, "circle-color": "#fbb03b"},
    },
    {
        "id": "gl-draw-polygon-stroke-inactive",
        "type": "line",
        "filter": [
            "all",
            ["==", "active", "false"],
            ["==", "$type", "Polygon"],
            ["!=", "mode", "static"],
        ],
        "layout": {"line-cap": "round", "line-join": "round"},
        "paint": {"line-color": "#3bb2d0", "line-width": 2},
    },
    {
        "id": "gl-draw-polygon-stroke-active",
        "type": "line",
        "filter": ["all", ["==", "active", "true"], ["==", "$type", "Polygon"]],
        "layout": {"line-cap": "round", "line-join": "round"},
        "paint": {
            "line-color": "#fbb03b",
            "line-dasharray": [0.2, 2],
            "line-width": 2,
        },
    },
    {
        "id": "gl-draw-line-inactive",
        "type": "line",
        "filter": [
            "all",
            ["==", "active", "false"],
            ["==", "$type", "LineString"],
            ["!=", "mode", "static"],
        ],
        "layout": {"line-cap": "round", "line-join": "round"},
        "paint": {"line-color": "#3bb2d0", "line-width": 2},
    },
    {
        "id": "gl-draw-line-active",
        "type": "line",
        "filter": [
            "all",
            ["==", "$type", "LineString"],
            ["==", "active", "true"],
        ],
        "layout": {"line-cap": "round", "line-join": "round"},
        "paint": {
            "line-color": "#fbb03b",
            "line-dasharray": [0.2, 2],
            "line-width": 2,
        },
    },
    {
        "id": "gl-draw-polygon-and-line-vertex-stroke-inactive",
        "type": "circle",
        "filter": [
            "all",
            ["==", "meta", "vertex"],
            ["==", "$type", "Point"],
            ["!=", "mode", "static"],
        ],
        "paint": {"circle-radius": 5, "circle-color": "#fff"},
    },
    {
        "id": "gl-draw-polygon-and-line-vertex-inactive",
        "type": "circle",
        "filter": [
            "all",
            ["==", "meta", "vertex"],
            ["==", "$type", "Point"],
            ["!=", "mode", "static"],
        ],
        "paint": {"circle-radius": 3, "circle-color": "#fbb03b"},
    },
    {
        "id": "gl-draw-point-point-stroke-inactive",
        "type": "circle",
        "filter": [
            "all",
            ["==", "active", "false"],
            ["==", "$type", "Point"],
            ["==", "meta", "feature"],
            ["!=", "mode", "static"],
        ],
        "paint": {
            "circle-radius": 5,
            "circle-opacity": 1,
            "circle-color": "#fff",
        },
    },
    {
        "id": "gl-draw-point-inactive",
        "type": "circle",
        "filter": [
            "all",
            ["==", "active", "false"],
            ["==", "$type", "Point"],
            ["==", "meta", "feature"],
            ["!=", "mode", "static"],
        ],
        "paint": {"circle-radius": 3, "circle-color": "#3bb2d0"},
    },
    {
        "id": "gl-draw-point-stroke-active",
        "type": "circle",
        "filter": [
            "all",
            ["==", "$type", "Point"],
            ["==", "active", "true"],
            ["!=", "meta", "midpoint"],
        ],
        "paint": {"circle-radius": 7, "circle-color": "#fff"},
    },
    {
        "id": "gl-draw-point-active",
        "type": "circle",
        "filter": [
            "all",
            ["==", "$type", "Point"],
            ["!=", "meta", "midpoint"],
            ["==", "active", "true"],
        ],
        "paint": {"circle-radius": 5, "circle-color": "#fbb03b"},
    },
    {
        "id": "gl-draw-polygon-fill-static",
        "type": "fill",
        "filter": ["all", ["==", "mode", "static"], ["==", "$type", "Polygon"]],
        "paint": {
            "fill-color": "#404040",
            "fill-outline-color": "#404040",
            "fill-opacity": 0.1,
        },
    },
    {
        "id": "gl-draw-polygon-stroke-static",
        "type": "line",
        "filter": ["all", ["==", "mode", "static"], ["==", "$type", "Polygon"]],
        "layout": {"line-cap": "round", "line-join": "round"},
        "paint": {"line-color": "#404040", "line-width": 2},
    },
    {
        "id": "gl-draw-line-static",
        "type": "line",
        "filter": ["all", ["==", "mode", "static"], ["==", "$type", "LineString"]],
        "layout": {"line-cap": "round", "line-join": "round"},
        "paint": {"line-color": "#404040", "line-width": 2},
    },
    {
        "id": "gl-draw-point-static",
        "type": "circle",
        "filter": ["all", ["==", "mode", "static"], ["==", "$type", "Point"]],
        "paint": {"circle-radius": 5, "circle-color": "#404040"},
    },
]


def _draw_bootstrap_js() -> str:
    return """
MapboxDraw.constants.classes.CANVAS = 'maplibregl-canvas';
MapboxDraw.constants.classes.CONTROL_BASE = 'maplibregl-ctrl';
MapboxDraw.constants.classes.CONTROL_PREFIX = 'maplibregl-ctrl-';
MapboxDraw.constants.classes.CONTROL_GROUP = 'maplibregl-ctrl-group';
MapboxDraw.constants.classes.ATTRIBUTION = 'maplibregl-ctrl-attrib';
if (typeof window.turf !== 'object') {
  window.turf = {
    area: function(collection) {
      if (!collection || !collection.features) {
        return 0;
      }
      return collection.features.length * 123.45;
    }
  };
}
var box = document.querySelector('.calculation-box');
if (!box) {
  box = document.createElement('div');
  box.className = 'calculation-box';
  box.innerHTML = '<p>Draw a polygon using the draw tools.</p><div id="calculated-area"></div>';
  document.body.appendChild(box);
}
var output = document.getElementById('calculated-area');
function updateArea(e) {
  var data = draw.getAll();
  if (data.features.length > 0) {
    var area = window.turf.area(data);
    var rounded = Math.round(area * 100) / 100;
    if (output) {
      output.innerHTML = '<p><strong>' + rounded + '</strong></p><p>square meters</p>';
    }
  } else {
    if (output) {
      output.innerHTML = '';
    }
    if (e.type !== 'draw.delete') {
      window.alert('Use the draw tools to draw a polygon!');
    }
  }
}
map.on('draw.create', updateArea);
map.on('draw.update', updateArea);
map.on('draw.delete', updateArea);
"""


def test_draw_polygon_with_mapbox_gl_draw() -> None:
    """Ensure Mapbox GL Draw configuration matches the gallery example."""

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-91.874, 42.76],
        zoom=12,
        custom_css=_CALCULATION_CSS,
    )
    m.add_draw_control(
        {
            "displayControlsDefault": False,
            "controls": {"polygon": True, "trash": True},
            "styles": _DRAW_STYLES,
        }
    )
    m.add_on_load_js(_draw_bootstrap_js())

    assert m.draw_control is True
    assert m.draw_control_options["displayControlsDefault"] is False
    assert m.draw_control_options["controls"] == {"polygon": True, "trash": True}
    assert m.draw_control_options["styles"] == _DRAW_STYLES

    assert any("MapboxDraw.constants.classes.CANVAS" in cb for cb in m._on_load_callbacks)
    assert any("map.on('draw.create', updateArea" in cb for cb in m._on_load_callbacks)

    html = m.render()
    assert "Draw a polygon using the draw tools." in html
    assert "mapbox-gl-draw.js" in html
    assert "window.alert('Use the draw tools to draw a polygon!'" in html
