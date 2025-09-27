"""Test suite for the create-a-time-slider example."""

from __future__ import annotations

from maplibreum import Map


# Sample of the earthquake dataset with month property applied in the
# original gallery example. The features below keep the structure but
# drastically reduce the payload so the regression test remains light.
_EARTHQUAKE_DATA = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [142.369, 38.322]},
            "properties": {"mag": 7.0, "time": 1425640986000, "month": 2},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [94.195, 26.692]},
            "properties": {"mag": 6.5, "time": 1429712490000, "month": 3},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-71.674, -31.573]},
            "properties": {"mag": 6.9, "time": 1438211046000, "month": 6},
        },
    ],
}


_CIRCLE_LAYER = {
    "id": "earthquake-circles",
    "type": "circle",
    "source": "earthquakes",
    "paint": {
        "circle-color": [
            "interpolate",
            ["linear"],
            ["get", "mag"],
            6,
            "#FCA107",
            8,
            "#7F3121",
        ],
        "circle-opacity": 0.75,
        "circle-radius": [
            "interpolate",
            ["linear"],
            ["get", "mag"],
            6,
            20,
            8,
            40,
        ],
    },
}


_LABEL_LAYER = {
    "id": "earthquake-labels",
    "type": "symbol",
    "source": "earthquakes",
    "layout": {
        "text-field": ["concat", ["to-string", ["get", "mag"]], "m"],
        "text-font": ["Noto Sans Regular"],
        "text-size": 12,
    },
    "paint": {"text-color": "rgba(0,0,0,0.5)"},
}


_SLIDER_CSS = """
.time-slider-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 25%;
    padding: 10px;
    font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
    z-index: 1000;
}
.time-slider-overlay .panel {
    background: #fff;
    border-radius: 3px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    margin-bottom: 10px;
    padding: 10px;
}
.time-slider-overlay .legend-bar {
    height: 10px;
    width: 100%;
    background: linear-gradient(to right, #fca107, #7f3121);
}
.time-slider-overlay input[type="range"] {
    width: 100%;
    cursor: ew-resize;
}
"""


def _slider_bootstrap_js() -> str:
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    month_list = ", ".join(f"'{month}'" for month in months)

    return f"""
const container = document.querySelector('.time-slider-overlay');
if (!container) {{
  const overlay = document.createElement('div');
  overlay.className = 'time-slider-overlay';
  overlay.innerHTML = `
    <div class="panel">
      <h2>Significant earthquakes in 2015</h2>
      <label id="time-slider-month" for="time-slider">January</label>
      <input id="time-slider" type="range" min="0" max="11" step="1" value="0" />
    </div>
    <div class="panel">
      <div class="legend">
        <div class="legend-bar"></div>
        <div>Magnitude (m)</div>
      </div>
    </div>`;
  document.body.appendChild(overlay);
}}
const slider = document.getElementById('time-slider');
const label = document.getElementById('time-slider-month');
const months = [{month_list}];
function applyMonth(month) {{
  var filter = ['==', ['get', 'month'], month];
  map.setFilter('earthquake-circles', filter);
  map.setFilter('earthquake-labels', filter);
  if (label) {{
    label.textContent = months[month];
  }}
}}
if (slider) {{
  slider.addEventListener('input', function(evt) {{
    applyMonth(parseInt(evt.target.value, 10));
  }});
  applyMonth(parseInt(slider.value || '0', 10));
}}
"""


def test_create_a_time_slider() -> None:
    """Reproduce the create-a-time-slider gallery example."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[31.4606, 20.7927],
        zoom=0.5,
        custom_css=_SLIDER_CSS,
    )

    m.add_source("earthquakes", _EARTHQUAKE_DATA)
    m.add_layer(_CIRCLE_LAYER)
    m.add_layer(_LABEL_LAYER)
    m.add_on_load_js(_slider_bootstrap_js())

    # Validate the stored configuration prior to rendering.
    source_names = [entry["name"] for entry in m.sources]
    assert "earthquakes" in source_names

    source_def = next(entry for entry in m.sources if entry["name"] == "earthquakes")
    assert source_def["definition"]["type"] == "FeatureCollection"
    assert len(source_def["definition"]["features"]) == 3
    assert source_def["definition"]["features"][0]["properties"]["month"] == 2

    layer_ids = [layer["id"] for layer in m.layers]
    assert layer_ids == ["earthquake-circles", "earthquake-labels"]

    circle_def = m.layers[0]["definition"]
    assert circle_def["paint"]["circle-opacity"] == 0.75
    assert circle_def["paint"]["circle-radius"][0] == "interpolate"

    label_def = m.layers[1]["definition"]
    assert label_def["layout"]["text-font"] == ["Noto Sans Regular"]
    assert label_def["paint"]["text-color"] == "rgba(0,0,0,0.5)"

    assert any("map.setFilter('earthquake-circles'" in cb for cb in m._on_load_callbacks)

    html = m.render()

    assert "time-slider-overlay" in html
    assert "Significant earthquakes in 2015" in html
    assert "Magnitude (m)" in html
    assert "applyMonth" in html
    assert "slider.addEventListener('input'" in html
