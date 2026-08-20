"""Reproduce OSWM's profile-aware hazard analysis map with Maplibreum."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from maplibreum import Map
from maplibreum.controls import PanelControl
from maplibreum.layers import LineLayer, RasterLayer
from maplibreum.sources import GeoJSONSource, ImageSource, VectorSource

from .common import (
    BASE_URL,
    add_pmtiles_v4,
    add_standard_controls,
    load_json,
    raster_style,
    save_map,
)


HAZARD_ROOT = f"{BASE_URL}data/hazard_analysis/"
PROFILES_URL = f"{HAZARD_ROOT}profiles.json"
TERRAIN_URL = f"{HAZARD_ROOT}terrain.json"
PMTILES_URL = f"{HAZARD_ROOT}hazard.pmtiles"
BOUNDARY_URL = f"{BASE_URL}data/boundaries/polygon.geojson"
GUIDE_URL = f"{BASE_URL}oswm_codebase/hazard_analysis/classification_guide.html"
DEFAULT_OUTPUT = Path(__file__).with_name("generated") / "hazard_analysis.html"

TRANSPARENT_PIXEL = "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="

HAZARD_CSS = """
:root { font-family: Inter, "Helvetica Neue", Arial, sans-serif; color: #1f2933; }
* { box-sizing: border-box; }
body { overflow: hidden; }
.oswm-hazard-logo { left: 7px !important; position: absolute; top: 7px !important; z-index: 6; }
.oswm-hazard-logo img { display: block; width: min(330px,44vw); }
#hazardPanel {
    background: rgba(255,255,255,.96); border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,.18);
    max-height: calc(100vh - 32px); overflow: auto; padding: 15px; position: absolute;
    right: 48px; top: 16px; width: min(330px,calc(100vw - 76px)); z-index: 5;
}
.hazard-panel-header { align-items: center; display: flex; justify-content: space-between; margin: 0 0 5px; }
.hazard-panel-header h1 { font-size: 20px; margin: 0; }
.hazard-guide-link { background: #e8f4f8; border: 1px solid #b8dae6; border-radius: 5px; color: #165a72; cursor: pointer; display: inline-block; font-size: 11px; font-weight: 700; padding: 4px 9px; text-decoration: none; white-space: nowrap; }
.hazard-guide-link:hover { background: #d0ecf4; }
.hazard-subtitle, .hazard-note { color: #59636e; font-size: 12px; line-height: 1.4; }
.hazard-control { margin-top: 12px; }
.hazard-control > label { display: block; font-size: 11px; font-weight: 750; letter-spacing: .045em; margin-bottom: 4px; text-transform: uppercase; }
.hazard-control select, .hazard-control input[type="range"] { width: 100%; }
.hazard-control select { background: #fff; border: 1px solid #aeb6bf; border-radius: 6px; padding: 7px; }
.hazard-inline { align-items: center; display: flex; gap: 9px; }
.hazard-inline input { margin: 0; }
.hazard-inline label { font-size: 13px; font-weight: 500; letter-spacing: 0; margin: 0; text-transform: none; }
#hazardLegend { border-top: 1px solid #d8dde2; margin-top: 13px; padding-top: 11px; }
.hazard-legend-row { align-items: center; display: flex; margin-bottom: 4px; }
.hazard-swatch { border: 1px solid #aeb6bf; border-radius: 50%; display: inline-block; height: 14px; margin-right: 6px; width: 14px; }
#hazardSource { color: #65717d; font-size: 10px; line-height: 1.35; margin-top: 10px; }
#hazardLoading { color: #8a4d00; display: none; font-size: 12px; font-weight: 700; margin-top: 9px; }
.hazard-welcome { background: rgba(14,22,31,.55); display: grid; inset: 0; padding: 20px; place-items: center; position: fixed; z-index: 20; }
.hazard-welcome[hidden] { display: none; }
.hazard-modal { background: white; border-radius: 14px; box-shadow: 0 10px 35px rgba(0,0,0,.3); max-width: 570px; padding: 24px; }
.hazard-modal h2 { margin-top: 0; }
.hazard-modal p, .hazard-modal li { font-size: 14px; line-height: 1.5; }
.hazard-modal button { background: #165a72; border: 0; border-radius: 7px; color: white; cursor: pointer; font-weight: 700; padding: 9px 15px; }
.maplibregl-popup-content { max-height: 65vh; max-width: 390px; overflow: auto; }
.hazard-popup-title { font-size: 15px; font-weight: 800; margin-bottom: 5px; }
.hazard-badge { border-radius: 999px; color: white; display: inline-block; font-size: 11px; margin: 2px 3px 2px 0; padding: 2px 7px; }
.hazard-evidence { font-size: 12px; margin: 7px 0 0; padding-left: 18px; }
.hazard-popup-links { border-top: 1px solid #d8dde2; display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; padding-top: 8px; }
.hazard-popup-links a { color: #3b82f6; font-size: .9em; text-decoration: none; }
@media (max-width: 650px) {
    .oswm-hazard-logo img { width: 190px; }
    #hazardPanel { bottom: 12px; max-height: 52vh; right: 12px; top: auto; width: calc(100vw - 24px); }
}
"""


def _panel_html() -> str:
    return f"""
<aside id="hazardPanel">
  <div class="hazard-panel-header">
    <h1>Hazard Analysis</h1>
    <a href="{GUIDE_URL}" target="_blank" rel="noopener" class="hazard-guide-link">📋 Guide</a>
  </div>
  <div class="hazard-subtitle">Evidence-based pedestrian difficulty and danger screening</div>
  <div class="hazard-control">
    <label for="hazardProfileSelect">User profile</label>
    <select id="hazardProfileSelect"></select>
    <div id="hazardProfileDescription" class="hazard-note"></div>
  </div>
  <div class="hazard-control">
    <label for="hazardCategorySelect">Hazard category</label>
    <select id="hazardCategorySelect"><option value="all">All categories</option></select>
  </div>
  <div class="hazard-control">
    <label for="hazardSeveritySelect">Minimum level</label>
    <select id="hazardSeveritySelect"></select>
  </div>
  <div class="hazard-control">
    <label for="hazardConfidenceRange">Minimum confidence: <span id="hazardConfidenceValue">0</span>%</label>
    <input id="hazardConfidenceRange" type="range" min="0" max="100" value="0" step="5">
  </div>
  <div class="hazard-control hazard-inline">
    <input id="hazardUnknownToggle" type="checkbox">
    <label for="hazardUnknownToggle">Show insufficient-data features</label>
  </div>
  <div class="hazard-control hazard-inline">
    <input id="hazardTerrainToggle" type="checkbox">
    <label for="hazardTerrainToggle">Terrain difficulty potential</label>
  </div>
  <div id="hazardLoading">Loading selected profile…</div>
  <div id="hazardLegend"></div>
  <div id="hazardSource"></div>
</aside>
"""


def _welcome_html() -> str:
    return f"""
<div class="hazard-welcome" id="hazardWelcome">
  <div class="hazard-modal">
    <h2>Read this map as a screening tool</h2>
    <p>Hazards are inferred from available OSM attributes and a global terrain model. A feature with no detected hazard is <strong>not certified safe</strong>.</p>
    <ul>
      <li>Missing tactile, surface or kerb data remains unknown; it is never treated as “no”.</li>
      <li>Longitudinal terrain slope is contextual and directional. Cross slope requires an explicit <code>incline:across=*</code> tag.</li>
      <li>Critical means an apparent barrier or an extreme contextual safety risk; the popup states which.</li>
    </ul>
    <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
      <button id="closeHazardWelcome">Explore the map</button>
      <a href="{GUIDE_URL}" target="_blank" rel="noopener" class="hazard-guide-link" style="padding:9px 15px;font-size:13px">📋 Classification Guide</a>
    </div>
  </div>
</div>
"""


def _hazard_layer_definitions(source_layer: str) -> list[LineLayer]:
    return [
        LineLayer(
            "unknown-lines",
            "hazards",
            source_layer=source_layer,
            filter=["==", ["get", "status"], "insufficient_data"],
            paint={
                "line-color": "#6b7280",
                "line-width": 2,
                "line-dasharray": [2, 2],
                "line-opacity": 0.55,
            },
        ),
        LineLayer(
            "hazard-lines",
            "hazards",
            source_layer=source_layer,
            paint={
                "line-color": [
                    "match",
                    ["get", "severity"],
                    1,
                    "#fee08b",
                    2,
                    "#fdae61",
                    3,
                    "#f46d43",
                    4,
                    "#a50026",
                    "#ffffff",
                ],
                "line-width": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    10,
                    ["case", ["boolean", ["feature-state", "hover"], False], 3, 1.5],
                    17,
                    ["case", ["boolean", ["feature-state", "hover"], False], 12, 6],
                ],
                "line-opacity": 0.9,
            },
        ),
        LineLayer(
            "hazard-hit",
            "hazards",
            source_layer=source_layer,
            paint={"line-color": "rgba(0,0,0,0)", "line-width": 14},
        ),
    ]


def _application_js(metadata: dict[str, Any], terrain: dict[str, Any]) -> str:
    metadata_json = json.dumps(metadata, separators=(",", ":"))
    terrain_json = json.dumps(terrain, separators=(",", ":"))
    return f"""
const hazardState = {{metadata: {metadata_json}, terrain: {terrain_json}, profile: null, fitted: false}};
const hazardElement = id => document.getElementById(id);
const escapeHazardHtml = value => String(value ?? '').replace(/[&<>"']/g, character =>
    ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[character]);
const objectValue = value => {{
    if (typeof value !== 'string') return value;
    try {{ return JSON.parse(value); }} catch (_error) {{ return value; }}
}};

function addHazardLayers(sourceLayer) {{
    map.addLayer({{id:'unknown-lines',type:'line',source:'hazards','source-layer':sourceLayer,
        filter:['==',['get','status'],'insufficient_data'],
        paint:{{'line-color':'#6b7280','line-width':2,'line-dasharray':[2,2],'line-opacity':.55}}}});
    map.addLayer({{id:'hazard-lines',type:'line',source:'hazards','source-layer':sourceLayer,
        paint:{{'line-color':['match',['get','severity'],1,'#fee08b',2,'#fdae61',3,'#f46d43',4,'#a50026','#fff'],
        'line-width':['interpolate',['linear'],['zoom'],10,['case',['boolean',['feature-state','hover'],false],3,1.5],17,['case',['boolean',['feature-state','hover'],false],12,6]],
        'line-opacity':.9}}}});
    map.addLayer({{id:'hazard-hit',type:'line',source:'hazards','source-layer':sourceLayer,
        paint:{{'line-color':'rgba(0,0,0,0)','line-width':14}}}});
}}

function applyHazardFilters() {{
    if (!map.getLayer('hazard-lines')) return;
    const minimum = Number(hazardElement('hazardSeveritySelect').value);
    const confidence = Number(hazardElement('hazardConfidenceRange').value);
    const category = hazardElement('hazardCategorySelect').value;
    hazardElement('hazardConfidenceValue').textContent = confidence;
    const severityField = category === 'all' ? 'severity' : `category_${{category}}`;
    const filter = ['all', ['!=',['get','status'],'insufficient_data'],
        ['>=',['coalesce',['get',severityField],0],minimum],
        ['>=',['coalesce',['get','confidence'],0],confidence]];
    map.setFilter('hazard-lines', filter);
    map.setFilter('hazard-hit', filter);
    map.setLayoutProperty('unknown-lines', 'visibility',
        hazardElement('hazardUnknownToggle').checked ? 'visible' : 'none');
}}

function updateHazardTerrain() {{
    const visible = hazardElement('hazardTerrainToggle').checked && hazardState.terrain?.available;
    map.setLayoutProperty('terrain-potential', 'visibility', visible ? 'visible' : 'none');
    if (!visible || !hazardState.profile) return;
    const profile = hazardState.terrain.profiles[hazardState.profile];
    map.getSource('terrain-source').updateImage({{
        url: new URL(profile.path, {json.dumps(BASE_URL)}).href,
        coordinates: hazardState.terrain.coordinates
    }});
}}

function fitHazardBounds() {{
    if (hazardState.fitted || !hazardState.terrain?.bounds) return;
    const [west,south,east,north] = hazardState.terrain.bounds;
    map.fitBounds([[west,south],[east,north]], {{padding:45,maxZoom:16}});
    hazardState.fitted = true;
}}

function switchHazardProfile() {{
    const profile = hazardElement('hazardProfileSelect').value;
    hazardState.profile = profile;
    hazardElement('hazardProfileDescription').textContent = hazardState.metadata.profiles[profile].description;
    for (const layerId of ['unknown-lines','hazard-lines','hazard-hit']) {{
        if (map.getLayer(layerId)) map.removeLayer(layerId);
    }}
    addHazardLayers(`hazard_${{profile}}`);
    applyHazardFilters();
    updateHazardTerrain();
    fitHazardBounds();
}}

function hazardPopupHtml(feature, lngLat) {{
    const properties = feature.properties;
    const element = feature.geometry.type === 'Point' ? 'node' : 'way';
    const severity = Number(properties.severity);
    const level = hazardState.metadata.severity_levels[String(severity)];
    const directionName = Number(properties.severity_fwd) >= Number(properties.severity_bwd) ? 'forward' : 'backward';
    const direction = objectValue(properties[directionName]) || {{}};
    const impact = objectValue(properties.impact) || [];
    const ruleIds = objectValue(direction.rule_ids) || [];
    const rulesById = Object.fromEntries(hazardState.metadata.rules.map(rule => [rule.id,rule]));
    const evidence = ruleIds.map(ruleId => rulesById[ruleId]).filter(Boolean);
    const criticalContext = severity === 4
        ? (properties.traversability === 'impassable' ? 'Apparent mobility barrier' : 'Extreme contextual safety risk') : '';
    return `<div class="hazard-popup-title">${{escapeHazardHtml(level?.label || 'Hazard')}}</div>
      ${{criticalContext ? `<div><strong>${{escapeHazardHtml(criticalContext)}}</strong></div>` : ''}}
      <div>Impact: ${{escapeHazardHtml(impact.join?.(', ') || impact || '—')}}</div>
      <div>Traversability: ${{escapeHazardHtml(properties.traversability)}}</div>
      <div>Forward / backward: ${{properties.severity_fwd}} / ${{properties.severity_bwd}}</div>
      <div>Confidence: ${{properties.confidence}}% · evidence coverage: ${{properties.coverage}}%</div>
      <div>Status: ${{escapeHazardHtml(properties.status)}} · slope: ${{escapeHazardHtml(properties.slope_source)}}</div>
      <div>Feature: ${{escapeHazardHtml(properties.edge_kind)}} · ${{escapeHazardHtml(properties.source_id)}}</div>
      <ul class="hazard-evidence">${{evidence.map(item => {{
          const effect = item.effects?.[hazardState.profile] || {{severity:0}};
          const category = hazardState.metadata.categories[item.category] || {{label:item.category}};
          const color = hazardState.metadata.severity_levels[String(effect.severity)]?.color || '#64748b';
          return `<li><span class="hazard-badge" style="background:${{color}}">${{escapeHazardHtml(category.label)}}</span> ${{escapeHazardHtml(item.description)}}</li>`;
      }}).join('') || '<li>No hazard rule matched the available evidence.</li>'}}</ul>
      <div class="hazard-popup-links">
        <a href="https://www.openstreetmap.org/${{element}}/${{encodeURIComponent(properties.source_id)}}" target="_blank" rel="noopener">OSM</a>
        <a href="https://www.mapillary.com/app/?lat=${{lngLat.lat}}&lng=${{lngLat.lng}}&z=19" target="_blank" rel="noopener">Mapillary</a>
        <a href="https://geohack.toolforge.org/geohack.php?params=${{lngLat.lat}}_N_${{lngLat.lng}}_E" target="_blank" rel="noopener">GeoHack</a>
      </div>`;
}}

for (const [id, profile] of Object.entries(hazardState.metadata.profiles)) {{
    hazardElement('hazardProfileSelect').add(new Option(profile.label,id));
}}
for (const [id, category] of Object.entries(hazardState.metadata.categories)) {{
    hazardElement('hazardCategorySelect').add(new Option(category.label,id));
}}
for (const [level, item] of Object.entries(hazardState.metadata.severity_levels)) {{
    hazardElement('hazardSeveritySelect').add(new Option(`${{level}} — ${{item.label}}`,level));
}}
hazardElement('hazardSeveritySelect').value = '1';
hazardElement('hazardLegend').innerHTML = Object.values(hazardState.metadata.severity_levels)
    .map(item => `<div class="hazard-legend-row"><span class="hazard-swatch" style="background:${{item.color}}"></span>${{escapeHazardHtml(item.label)}}</div>`)
    .join('') + '<div class="hazard-legend-row"><span class="hazard-swatch" style="background:#6b7280"></span>Insufficient data</div>';
hazardElement('hazardSource').textContent = hazardState.terrain.available
    ? `${{hazardState.terrain.description}} ${{hazardState.terrain.source_attribution}}`
    : 'Terrain overlay unavailable for this generation.';

hazardElement('hazardProfileSelect').addEventListener('input', switchHazardProfile);
for (const id of ['hazardCategorySelect','hazardSeveritySelect','hazardConfidenceRange','hazardUnknownToggle']) {{
    hazardElement(id).addEventListener('input', applyHazardFilters);
}}
hazardElement('hazardTerrainToggle').addEventListener('change', updateHazardTerrain);
hazardElement('closeHazardWelcome').addEventListener('click', () => {{
    hazardElement('hazardWelcome').hidden = true;
}});
map.on('click', 'hazard-hit', event => {{
    const feature = event.features?.[0];
    if (!feature) return;
    new maplibregl.Popup().setLngLat(event.lngLat)
        .setHTML(DOMPurify.sanitize(hazardPopupHtml(feature,event.lngLat))).addTo(map);
}});
switchHazardProfile();
"""


def build_map(
    *,
    profiles: Any = PROFILES_URL,
    terrain: Any = TERRAIN_URL,
) -> Map:
    metadata = load_json(profiles)
    terrain_payload = load_json(terrain)
    initial_profile = "wheelchair" if "wheelchair" in metadata["profiles"] else next(
        iter(metadata["profiles"])
    )
    source_layer = f"hazard_{initial_profile}"
    coordinates = terrain_payload.get("coordinates") or [[0, 0], [0, 0], [0, 0], [0, 0]]

    map_object = Map(
        title="OSWM Hazard Analysis (Maplibreum)",
        map_style=raster_style("light"),
        center=[-49.274, -25.465],
        zoom=12,
        width="100%",
        height="100vh",
        custom_css=HAZARD_CSS,
        container_id="oswm-hazard-map",
    )
    add_pmtiles_v4(map_object)
    add_standard_controls(map_object, geolocate=False)

    map_object.add_source("boundary", GeoJSONSource(BOUNDARY_URL))
    map_object.add_source(
        "terrain-source", ImageSource(url=TRANSPARENT_PIXEL, coordinates=coordinates)
    )
    map_object.add_source(
        "hazards",
        VectorSource(url=f"pmtiles://{PMTILES_URL}", promote_id="source_id"),
    )
    map_object.add_layer(
        LineLayer(
            "boundary-line",
            "boundary",
            paint={"line-color": "#9ca3af", "line-width": 2},
        )
    )
    map_object.add_layer(
        RasterLayer(
            "terrain-potential",
            "terrain-source",
            layout={"visibility": "none"},
            paint={"raster-opacity": 0.7},
        )
    )
    for layer in _hazard_layer_definitions(source_layer):
        map_object.add_layer(layer)

    map_object.add_feature_state_hover("hazard-hit", "hazards")
    map_object.add_control(
        PanelControl(
            html_content=(
                f'<a href="{BASE_URL}" title="Open the OSWM node">'
                f'<img src="{BASE_URL}oswm_codebase/assets/branding/logos/page_logo.png" '
                'alt="OpenSidewalkMap"></a>'
            ),
            css_class="oswm-hazard-logo",
        )
    )
    map_object.add_control(
        PanelControl(html_content=_panel_html(), css_class="oswm-hazard-panel-shell")
    )
    map_object.add_control(
        PanelControl(html_content=_welcome_html(), css_class="oswm-hazard-welcome-shell")
    )
    map_object.add_on_load_js(_application_js(metadata, terrain_payload))
    return map_object


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", default=PROFILES_URL, help="Profiles JSON path or URL")
    parser.add_argument("--terrain", default=TERRAIN_URL, help="Terrain JSON path or URL")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(save_map(build_map(profiles=args.profiles, terrain=args.terrain), args.output))


if __name__ == "__main__":
    main()
