"""Reproduce OSWM's temporal completeness tile map with Maplibreum."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from maplibreum import Map
from maplibreum.controls import PanelControl
from maplibreum.layers import FillLayer, LineLayer
from maplibreum.sources import GeoJSONSource

from .common import BASE_URL, load_json, raster_style, save_map


DATA_URL = f"{BASE_URL}quality_check/completeness/data.json"
BOUNDARY_URL = f"{BASE_URL}data/boundaries/polygon.geojson"
DEFAULT_OUTPUT = Path(__file__).with_name("generated") / "completeness.html"
ZOOM_LEVELS = tuple(range(12, 18))

COMPLETENESS_CSS = """
* { box-sizing: border-box; }
body { background: #0f172a; color: #f8fafc; font-family: 'Outfit', sans-serif; overflow: hidden; }
.completeness-top-bar {
    align-items: center; backdrop-filter: blur(12px); background: rgba(15,23,42,.88);
    border-bottom: 1px solid rgba(255,255,255,.1); box-shadow: 0 4px 15px rgba(0,0,0,.2);
    display: flex; justify-content: space-between; left: 0; padding: 10px 20px; position: absolute;
    top: 0; width: 100%; z-index: 10;
}
.completeness-top-bar .back-btn { background: rgba(255,255,255,.05); border: 1px solid rgba(0,242,254,.3); border-radius: 6px; color: #00f2fe; font-size: .9rem; font-weight: 500; padding: 6px 12px; text-decoration: none; }
.completeness-top-bar h3 { color: #f8fafc; font-size: 1.15rem; font-weight: 600; letter-spacing: .5px; margin: 0; }
.completeness-top-bar img { height: 1.5em; margin-right: 10px; vertical-align: middle; }
.completeness-controls {
    backdrop-filter: blur(14px); background: rgba(15,23,42,.92); border: 1px solid rgba(255,255,255,.1);
    border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,.25); min-width: 220px; padding: 14px 16px;
    position: absolute; right: 12px; top: 62px; z-index: 10;
}
.completeness-controls h4, .completeness-legend h4 { color: #00f2fe; font-size: .85rem; font-weight: 600; margin: 0 0 10px; }
.completeness-controls label { align-items: center; color: #cbd5e1; cursor: pointer; display: flex; font-size: .85rem; gap: 8px; padding: 4px 0; }
.completeness-controls input[type="radio"] { accent-color: #00f2fe; }
.completeness-divider { border-top: 1px solid rgba(255,255,255,.08); margin: 10px 0; }
.completeness-label-row { align-items: center; color: #94a3b8; display: flex; font-size: .8rem; justify-content: space-between; margin-bottom: 4px; }
.completeness-controls input[type="range"], .completeness-legend input[type="range"] { accent-color: #00f2fe; cursor: pointer; width: 100%; }
.completeness-legend {
    backdrop-filter: blur(14px); background: rgba(15,23,42,.92); border: 1px solid rgba(255,255,255,.1);
    border-radius: 10px; bottom: 30px; box-shadow: 0 8px 24px rgba(0,0,0,.25); left: 12px;
    padding: 12px 16px; position: absolute; z-index: 10;
}
.completeness-legend .ratio-bar { background: linear-gradient(to right,#d73027,#fc8d59,#fee08b,#d9ef8b,#66bd63,#1a9850); border-radius: 4px; height: 14px; width: 180px; }
.completeness-legend .labels { color: #94a3b8; display: flex; font-size: .7rem; justify-content: space-between; margin-top: 3px; }
.completeness-no-data { align-items: center; color: #94a3b8; display: flex; font-size: .7rem; gap: 6px; margin-top: 6px; }
.completeness-no-data .swatch { background: #475569; border-radius: 3px; height: 14px; width: 14px; }
.completeness-auto-label { align-items: center; color: #cbd5e1; cursor: pointer; display: flex; font-size: .8rem; gap: 8px; }
#completenessStatsButton { align-items:center; backdrop-filter:blur(14px); background:rgba(15,23,42,.92); border:1px solid rgba(255,255,255,.1); border-radius:50%; bottom:240px; box-shadow:0 4px 12px rgba(0,0,0,.3); color:#00f2fe; cursor:pointer; display:flex; height:44px; justify-content:center; left:12px; position:absolute; width:44px; z-index:10; }
.completeness-modal { align-items:center; backdrop-filter:blur(4px); background:rgba(0,0,0,.6); display:flex; height:100%; justify-content:center; left:0; position:fixed; top:0; width:100%; z-index:9999; }
.completeness-modal[hidden] { display:none; }
.completeness-modal-card { background:rgba(15,23,42,.97); border:1px solid rgba(0,242,254,.3); border-radius:12px; box-shadow:0 12px 32px rgba(0,0,0,.5); max-width:95vw; padding:20px; width:800px; }
.completeness-modal-header { align-items:center; border-bottom:1px solid rgba(255,255,255,.1); display:flex; justify-content:space-between; margin-bottom:16px; padding-bottom:12px; }
.completeness-modal-header h3 { color:#00f2fe; font-size:1.2rem; margin:0; }
#closeCompletenessStats { background:none; border:0; color:#94a3b8; cursor:pointer; font-size:24px; }
.completeness-charts { display:flex; flex-wrap:wrap; gap:20px; }
.completeness-chart { flex:1; height:300px; min-width:300px; position:relative; }
.maplibregl-popup-content { background:rgba(15,23,42,.97) !important; border:1px solid rgba(0,242,254,.3) !important; border-radius:8px !important; box-shadow:0 8px 24px rgba(0,0,0,.3) !important; color:#cbd5e1; max-width:none !important; padding:12px !important; width:270px !important; }
.maplibregl-popup-tip { border-top-color:rgba(15,23,42,.97) !important; }
.maplibregl-popup-close-button { color:#94a3b8 !important; font-size:18px !important; }
@media (max-width: 650px) {
    .completeness-top-bar { gap:8px; padding:8px; }
    .completeness-top-bar h3 { font-size:.85rem; }
    .completeness-top-bar .spacer { display:none; }
    .completeness-controls { right:8px; top:58px; }
}
"""


def ratio_to_color(ratio: Any) -> str:
    if ratio is None:
        return "rgba(71, 85, 105, 0.5)"
    value = min(float(ratio), 1.0)
    stops = [
        (0.0, (215, 48, 39)),
        (0.15, (252, 141, 89)),
        (0.3, (254, 224, 139)),
        (0.5, (217, 239, 139)),
        (0.75, (102, 189, 99)),
        (1.0, (26, 152, 80)),
    ]
    lower, upper = stops[0], stops[-1]
    for candidate, following in zip(stops, stops[1:]):
        if candidate[0] <= value <= following[0]:
            lower, upper = candidate, following
            break
    fraction = 1 if upper[0] == lower[0] else (value - lower[0]) / (upper[0] - lower[0])
    color = tuple(round(left + fraction * (right - left)) for left, right in zip(lower[1], upper[1]))
    return f"rgba({color[0]}, {color[1]}, {color[2]}, 0.55)"


def completeness_to_geojson(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert OSWM's compact zoom/tile history JSON into map-ready polygons."""

    timestamps = payload.get("timestamps", [])
    latest_index = max(0, len(timestamps) - 1)
    features: list[dict[str, Any]] = []
    for zoom_text, zoom_payload in payload.get("zoom_levels", {}).items():
        zoom = int(zoom_text)
        for tile_id, tile in zoom_payload.get("tiles", {}).items():
            west, south, east, north = tile["bbox"]
            properties: dict[str, Any] = {
                "tile_id": tile_id,
                "zoom": zoom,
                "bbox": [west, south, east, north],
            }
            for index, record in enumerate(tile.get("data", [])):
                for key in (
                    "road_length",
                    "footway_length",
                    "sidewalk_length",
                    "footway_ratio",
                    "sidewalk_ratio",
                ):
                    properties[f"{key}_t{index}"] = record.get(key)
            properties["_color"] = ratio_to_color(
                properties.get(f"footway_ratio_t{latest_index}")
            )
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [west, south],
                                [east, south],
                                [east, north],
                                [west, north],
                                [west, south],
                            ]
                        ],
                    },
                    "properties": properties,
                }
            )
    return {"type": "FeatureCollection", "features": features}


def _top_bar_html(city: str) -> str:
    return f"""
<header class="completeness-top-bar">
  <a class="back-btn" href="{BASE_URL}quality_check/oswm_qc_main.html">← Back to QC Main</a>
  <h3><img src="{BASE_URL}oswm_codebase/assets/branding/logos/project_logo.png" alt="OSWM">Pedestrian Network Completeness — {city}</h3>
  <div class="spacer" style="width:120px"></div>
</header>
"""


def _controls_html(timestamp_count: int) -> str:
    last_index = max(0, timestamp_count - 1)
    display = "block" if timestamp_count > 1 else "none"
    return f"""
<section class="completeness-controls">
  <h4>Ratio Layer</h4>
  <label><input type="radio" name="completenessMetric" value="footway" checked> Footway / Road</label>
  <label><input type="radio" name="completenessMetric" value="sidewalk"> Sidewalk / Road</label>
  <div class="completeness-divider"></div>
  <div style="display:{display}">
    <div class="completeness-label-row"><span>Timestamp</span><span id="completenessTimestampLabel"></span></div>
    <input type="range" id="completenessTimestampSlider" min="0" max="{last_index}" value="{last_index}" step="1">
  </div>
</section>
"""


def _legend_html() -> str:
    return """
<section class="completeness-legend">
  <h4 id="completenessLegendTitle">Footway / Road Ratio</h4>
  <div class="ratio-bar"></div>
  <div class="labels"><span>0</span><span>0.25</span><span>0.5</span><span>0.75</span><span>1.0+</span></div>
  <div class="completeness-no-data"><span class="swatch"></span><span>No road data</span></div>
  <div class="completeness-divider"></div>
  <label class="completeness-auto-label"><input type="checkbox" id="completenessAutoScale" checked> Auto-scale zoom</label>
  <div id="completenessManualZoomGroup" style="display:none;margin-top:8px">
    <div class="completeness-label-row"><span>Manual Zoom</span><span id="completenessManualZoomLabel">Z12</span></div>
    <input type="range" id="completenessManualZoom" min="12" max="17" value="12" step="1">
  </div>
</section>
"""


def _statistics_html() -> str:
    return """
<button id="completenessStatsButton" title="Tile statistics" aria-label="Tile statistics">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
</button>
<div id="completenessStatsModal" class="completeness-modal" hidden>
  <div class="completeness-modal-card">
    <div class="completeness-modal-header"><h3>Tile Statistics</h3><button id="closeCompletenessStats">&times;</button></div>
    <div class="completeness-charts">
      <div class="completeness-chart"><canvas id="completenessHistogram"></canvas></div>
      <div class="completeness-chart"><canvas id="completenessBoxplot"></canvas></div>
    </div>
  </div>
</div>
"""


def _application_js(timestamps: list[str]) -> str:
    return f"""
const completenessTimestamps = {json.dumps(timestamps)};
const completenessGeoJSON = map.__maplibreumSourceDefinitions.tiles.data;
let completenessMetric = 'footway';
let completenessTimestamp = Math.max(0, completenessTimestamps.length - 1);
let completenessAutoScale = true;
let completenessManualZoom = 12;
let completenessHistogramChart = null;
let completenessBoxChart = null;

function completenessRatioColor(ratio) {{
    if (ratio === null || ratio === undefined) return 'rgba(71, 85, 105, 0.5)';
    const value = Math.min(ratio, 1);
    const stops = [[0,[215,48,39]],[.15,[252,141,89]],[.3,[254,224,139]],[.5,[217,239,139]],[.75,[102,189,99]],[1,[26,152,80]]];
    let lower = stops[0], upper = stops.at(-1);
    for (let index=0; index<stops.length-1; index++) {{
        if (value >= stops[index][0] && value <= stops[index+1][0]) {{ lower=stops[index]; upper=stops[index+1]; break; }}
    }}
    const fraction = upper[0] === lower[0] ? 1 : (value-lower[0])/(upper[0]-lower[0]);
    const color = lower[1].map((channel,index) => Math.round(channel + fraction*(upper[1][index]-channel)));
    return `rgba(${{color[0]}}, ${{color[1]}}, ${{color[2]}}, 0.55)`;
}}

function updateCompletenessColors() {{
    const key = `${{completenessMetric}}_ratio_t${{completenessTimestamp}}`;
    completenessGeoJSON.features.forEach(feature => {{ feature.properties._color = completenessRatioColor(feature.properties[key]); }});
    map.getSource('tiles').setData(completenessGeoJSON);
    document.getElementById('completenessLegendTitle').textContent = completenessMetric === 'footway'
        ? 'Footway / Road Ratio' : 'Sidewalk / Road Ratio';
}}
function activeCompletenessZoom() {{
    if (!completenessAutoScale) return completenessManualZoom;
    return Math.max(12, Math.min(17, Math.round(map.getZoom())));
}}
function updateCompletenessLayers() {{
    const active = activeCompletenessZoom();
    for (let zoom=12; zoom<=17; zoom++) map.setLayoutProperty(`tiles-z${{zoom}}`, 'visibility', zoom === active ? 'visible' : 'none');
}}
function updateCompletenessTimestampLabel() {{
    document.getElementById('completenessTimestampLabel').textContent = completenessTimestamps[completenessTimestamp] || '';
}}

function renderCompletenessStats() {{
    if (document.getElementById('completenessStatsModal').hidden) return;
    const activeZoom = activeCompletenessZoom();
    const key = `${{completenessMetric}}_ratio_t${{completenessTimestamp}}`;
    const ratios = completenessGeoJSON.features
        .filter(feature => feature.properties.zoom === activeZoom)
        .map(feature => feature.properties[key])
        .filter(value => value !== null && value !== undefined);
    const bins = Array(10).fill(0);
    ratios.forEach(ratio => {{ bins[Math.min(9,Math.floor(ratio*10))]++; }});
    completenessHistogramChart?.destroy();
    completenessHistogramChart = new Chart(document.getElementById('completenessHistogram'), {{
        type:'bar', data:{{labels:['0-.1','.1-.2','.2-.3','.3-.4','.4-.5','.5-.6','.6-.7','.7-.8','.8-.9','.9-1+'],datasets:[{{data:bins,backgroundColor:'rgba(0,242,254,.4)',borderColor:'#00f2fe',borderWidth:1}}]}},
        options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},title:{{display:true,text:`Ratio Histogram (Z${{activeZoom}})`,color:'#f8fafc'}}}},scales:{{y:{{ticks:{{color:'#94a3b8'}},grid:{{color:'rgba(255,255,255,.05)'}}}},x:{{ticks:{{color:'#94a3b8',font:{{size:10}}}},grid:{{display:false}}}}}}}}
    }});
    completenessBoxChart?.destroy();
    completenessBoxChart = new Chart(document.getElementById('completenessBoxplot'), {{
        type:'boxplot', data:{{labels:['Ratio Distribution'],datasets:[{{data:[ratios],backgroundColor:'rgba(0,242,254,.4)',borderColor:'#00f2fe',borderWidth:1,outlierBackgroundColor:'rgba(215,48,39,.8)'}}]}},
        options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},title:{{display:true,text:`Ratio Boxplot (Z${{activeZoom}})`,color:'#f8fafc'}}}},scales:{{y:{{min:0,max:1.05,ticks:{{color:'#94a3b8'}},grid:{{color:'rgba(255,255,255,.05)'}}}},x:{{ticks:{{color:'#94a3b8'}},grid:{{display:false}}}}}}}}
    }});
}}

function normaliseBBox(value) {{
    if (Array.isArray(value)) return value;
    try {{ return JSON.parse(value); }} catch (_error) {{ return [0,0,0,0]; }}
}}
function showCompletenessPopup(event, zoom) {{
    const properties = event.features[0].properties;
    const suffix = `_t${{completenessTimestamp}}`;
    const bbox = normaliseBBox(properties.bbox);
    const centerLat = (Number(bbox[1])+Number(bbox[3]))/2;
    const centerLon = (Number(bbox[0])+Number(bbox[2]))/2;
    const metricHistory = completenessTimestamps.map((_timestamp,index) => {{
        const value = properties[`${{completenessMetric}}_ratio_t${{index}}`];
        return value === null || value === undefined ? null : Number(value)*100;
    }});
    const formatLength = key => Number(properties[key] || 0).toLocaleString(undefined,{{maximumFractionDigits:0}});
    const formatRatio = key => properties[key] == null ? 'N/A' : `${{(Number(properties[key])*100).toFixed(1)}}%`;
    const osmEdit = zoom >= 16 ? `<a href="https://www.openstreetmap.org/edit#map=17/${{centerLat}}/${{centerLon}}" target="_blank" rel="noopener">Edit on OSM</a>` : '';
    const popupHtml = `<div class="completeness-popup">
      <h4 style="color:#00f2fe;margin:0 0 6px">Tile ${{properties.tile_id}}</h4>
      <div style="font-size:12px;line-height:1.6"><b>Roads:</b> ${{formatLength('road_length'+suffix)}} m<br><b>Footways:</b> ${{formatLength('footway_length'+suffix)}} m<br><b>Sidewalks:</b> ${{formatLength('sidewalk_length'+suffix)}} m<br><b>Footway ratio:</b> ${{formatRatio('footway_ratio'+suffix)}}<br><b>Sidewalk ratio:</b> ${{formatRatio('sidewalk_ratio'+suffix)}}</div>
      <div style="display:flex;gap:8px;margin-top:8px"><a href="https://www.openstreetmap.org/#map=${{zoom}}/${{centerLat}}/${{centerLon}}" target="_blank" rel="noopener">View on OSM</a>${{osmEdit}}<button class="copy-bbox" data-bbox="${{bbox.join(',')}}">Copy BBox</button></div>
      <div style="height:120px;margin-top:12px;position:relative"><canvas></canvas></div></div>`;
    const popup = new maplibregl.Popup({{className:'dark-popup'}}).setLngLat(event.lngLat)
        .setHTML(DOMPurify.sanitize(popupHtml)).addTo(map);
    popup.getElement().querySelector('.copy-bbox')?.addEventListener('click', button => navigator.clipboard.writeText(button.currentTarget.dataset.bbox));
    const canvas = popup.getElement().querySelector('canvas');
    if (canvas) new Chart(canvas, {{type:'line',data:{{labels:completenessTimestamps,datasets:[{{data:metricHistory,borderColor:'#00f2fe',backgroundColor:'rgba(0,242,254,.1)',fill:true,tension:.2,pointRadius:3}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{x:{{ticks:{{color:'#94a3b8',font:{{size:9}},maxRotation:45,minRotation:45}},grid:{{color:'rgba(255,255,255,.05)'}}}},y:{{beginAtZero:true,ticks:{{color:'#94a3b8',font:{{size:9}}}},grid:{{color:'rgba(255,255,255,.05)'}}}}}}}}}});
}}

for (let zoom=12; zoom<=17; zoom++) map.on('click', `tiles-z${{zoom}}`, event => showCompletenessPopup(event,zoom));
map.on('zoom', () => {{ if (completenessAutoScale) {{ updateCompletenessLayers(); renderCompletenessStats(); }} }});
document.getElementById('completenessAutoScale').addEventListener('change', event => {{
    completenessAutoScale = event.target.checked;
    document.getElementById('completenessManualZoomGroup').style.display = completenessAutoScale ? 'none' : 'block';
    updateCompletenessLayers(); renderCompletenessStats();
}});
document.getElementById('completenessManualZoom').addEventListener('input', event => {{
    completenessManualZoom = Number(event.target.value);
    document.getElementById('completenessManualZoomLabel').textContent = `Z${{completenessManualZoom}}`;
    updateCompletenessLayers(); renderCompletenessStats();
}});
document.querySelectorAll('input[name="completenessMetric"]').forEach(radio => radio.addEventListener('change', event => {{ completenessMetric=event.target.value; updateCompletenessColors(); renderCompletenessStats(); }}));
document.getElementById('completenessTimestampSlider').addEventListener('input', event => {{ completenessTimestamp=Number(event.target.value); updateCompletenessTimestampLabel(); updateCompletenessColors(); renderCompletenessStats(); }});
document.getElementById('completenessStatsButton').addEventListener('click', () => {{ document.getElementById('completenessStatsModal').hidden=false; renderCompletenessStats(); }});
document.getElementById('closeCompletenessStats').addEventListener('click', () => {{ document.getElementById('completenessStatsModal').hidden=true; }});
updateCompletenessTimestampLabel();
updateCompletenessColors();
updateCompletenessLayers();
"""


def build_map(data: Any = DATA_URL) -> Map:
    payload = load_json(data)
    metadata = payload.get("metadata", {})
    timestamps = list(payload.get("timestamps", []))
    geojson = completeness_to_geojson(payload)
    bounds = metadata.get("bounds", [-49.38914, -25.6435043, -49.1843182, -25.3449505])
    center = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2]

    map_object = Map(
        title=f"OSWM Completeness Analysis — {metadata.get('city', 'Node')}",
        map_style=raster_style("dark"),
        center=center,
        zoom=12,
        width="100%",
        height="100vh",
        custom_css=COMPLETENESS_CSS,
        map_options={"minZoom": 10, "maxZoom": 18},
        container_id="oswm-completeness-map",
    )
    map_object.add_external_stylesheet(
        "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap"
    )
    map_object.add_external_script(
        "https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"
    )
    map_object.add_external_script(
        "https://unpkg.com/@sgratzl/chartjs-chart-boxplot@4.3.1/build/index.umd.min.js"
    )
    map_object.add_control(
        "navigation", "bottom-right", {"showZoom": True, "showCompass": True}
    )
    map_object.add_control("scale", "bottom-right", {"unit": "metric"})
    map_object.add_source("tiles", GeoJSONSource(geojson))
    map_object.add_source("boundary", GeoJSONSource(BOUNDARY_URL))
    map_object.add_layer(
        LineLayer(
            "city-boundary-line",
            "boundary",
            paint={
                "line-color": "#00f2fe",
                "line-width": 2.5,
                "line-dasharray": [2, 2],
                "line-opacity": 0.8,
            },
        )
    )
    for zoom in ZOOM_LEVELS:
        map_object.add_layer(
            FillLayer(
                f"tiles-z{zoom}",
                "tiles",
                filter=["==", ["get", "zoom"], zoom],
                layout={"visibility": "visible" if zoom == 12 else "none"},
                paint={
                    "fill-color": ["get", "_color"],
                    "fill-opacity": 0.7,
                    "fill-outline-color": "rgba(255,255,255,0.25)",
                },
            )
        )
        map_object.add_event_listener(
            "mouseenter",
            layer_id=f"tiles-z{zoom}",
            js="map.getCanvas().style.cursor = 'pointer';",
        )
        map_object.add_event_listener(
            "mouseleave",
            layer_id=f"tiles-z{zoom}",
            js="map.getCanvas().style.cursor = '';",
        )

    map_object.add_control(
        PanelControl(
            html_content=_top_bar_html(metadata.get("city", "Node")),
            css_class="completeness-top-shell",
        )
    )
    map_object.add_control(
        PanelControl(
            html_content=_controls_html(len(timestamps)),
            css_class="completeness-controls-shell",
        )
    )
    map_object.add_control(
        PanelControl(html_content=_legend_html(), css_class="completeness-legend-shell")
    )
    map_object.add_control(
        PanelControl(html_content=_statistics_html(), css_class="completeness-stats-shell")
    )
    map_object.add_on_load_js(_application_js(timestamps))
    return map_object


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=DATA_URL, help="Completeness JSON path or URL")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(save_map(build_map(args.data), args.output))


if __name__ == "__main__":
    main()
