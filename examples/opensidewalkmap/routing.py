"""Reproduce OSWM's accessible routing demonstrator with Maplibreum."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from maplibreum import Map
from maplibreum.controls import PanelControl
from maplibreum.layers import HillshadeLayer, LineLayer
from maplibreum.sources import GeoJSONSource, RasterDemSource

from .common import BASE_URL, add_standard_controls, raster_style, save_map


ROUTING_DATA_URL = f"{BASE_URL}data/routing/demo.geojson"
PROFILES_URL = f"{BASE_URL}data/routing/profiles.json"
BOUNDARY_URL = f"{BASE_URL}data/boundaries/polygon.geojson"
DEFAULT_OUTPUT = Path(__file__).with_name("generated") / "routing.html"

ROUTING_CSS = """
:root { font-family: "Helvetica Neue", Arial, sans-serif; color: #202124; }
body { overflow: hidden; }
.oswm-routing-logo { left: 4px !important; position: absolute; top: 4px !important; z-index: 6; }
.oswm-routing-logo img { display: block; height: auto; max-width: min(40vw, 330px); }
#routingPanel {
    background: rgba(255,255,255,.95); border-radius: 10px; box-shadow: 0 4px 14px rgba(0,0,0,.16);
    box-sizing: border-box; padding: 14px 16px; position: absolute; right: 50px; top: 18px;
    width: min(300px, calc(100vw - 90px)); z-index: 5;
}
#routingPanel h2 { align-items: center; cursor: pointer; display: flex; font-size: 17px; justify-content: space-between; margin: 0; user-select: none; }
#routingPanel:not(.collapsed) h2 { margin-bottom: 10px; }
#panelToggleBtn { background: none; border: 0; color: #565c62; cursor: pointer; font-size: 12px; padding: 2px 4px; transition: transform .2s ease; }
#routingPanel.collapsed #panelToggleBtn { transform: rotate(-90deg); }
#routingPanel.collapsed #routingPanelContent { display: none; }
#routingPanel label { display: block; font-size: 12px; font-weight: 700; letter-spacing: .04em; margin-bottom: 5px; text-transform: uppercase; }
#profileSelect { background: white; border: 1px solid #aeb4ba; border-radius: 6px; font-size: 14px; padding: 8px; width: 100%; }
#profileDescription { color: #565c62; font-size: 12px; line-height: 1.35; margin: 8px 0 0; }
#compareOption { margin-top: 10px; }
#compareOption[hidden], #comparisonInfo[hidden] { display: none; }
#routingPanel .compare-label { align-items: center; cursor: pointer; display: flex; font-size: 13px; font-weight: 600; gap: 7px; letter-spacing: 0; margin: 0; text-transform: none; }
.compare-label input { margin: 0; }
#routeInfo { border-top: 1px solid #d7dadd; font-size: 14px; line-height: 1.55; margin-top: 12px; padding-top: 10px; }
#routeInfo.hidden { display: none; }
#routeInfo .no-route { color: #9d1d20; font-weight: 700; }
#routeInfo .experimental { color: #745100; font-size: 11px; margin-top: 7px; }
#comparisonInfo { background: #fff4eb; border-left: 4px solid #d55e00; font-size: 12px; margin-top: 9px; padding: 7px 9px; }
#comparisonInfo .comparison-title { font-weight: 700; }
.route-swatch { display: inline-block; margin-right: 5px; vertical-align: middle; width: 20px; }
.route-swatch.selected { border-top: 4px solid #123bd1; }
.route-swatch.distance { border-top: 3px dashed #d55e00; }
.route-marker { border: 2px solid white; border-radius: 50%; box-shadow: 0 1px 4px rgba(0,0,0,.55); height: 13px; width: 13px; }
.routing-modal-overlay { align-items: center; background: rgba(0,0,0,.5); box-sizing: border-box; display: flex; inset: 0; justify-content: center; padding: 20px; position: fixed; z-index: 10; }
.routing-modal-overlay[hidden] { display: none; }
.routing-modal { background: white; border-radius: 10px; box-sizing: border-box; padding: 22px; width: min(390px,100%); }
.routing-modal h2 { margin-top: 0; }
.routing-modal li { margin-bottom: 7px; }
.routing-modal button { background: steelblue; border: 0; border-radius: 5px; color: white; cursor: pointer; float: right; padding: 8px 18px; }
@media (max-width: 600px) {
    #routingPanel { bottom: 28px; right: 10px; top: auto; width: calc(100vw - 20px); }
    .oswm-routing-logo img { max-width: 55vw; }
}
"""

ROUTING_PANEL_HTML = """
<section id="routingPanel" aria-label="Routing options">
  <h2 id="routingPanelHeader" title="Click to collapse or expand">
    <span>Route profile</span>
    <button id="panelToggleBtn" aria-label="Toggle panel" aria-expanded="true">▼</button>
  </h2>
  <div id="routingPanelContent">
    <label for="profileSelect">Optimization</label>
    <select id="profileSelect"></select>
    <p id="profileDescription">Loading routing profiles…</p>
    <div id="compareOption" hidden>
      <label class="compare-label" for="compareDistance">
        <input type="checkbox" id="compareDistance"> Compare with distance-only
      </label>
    </div>
    <div id="routeInfo" class="hidden" aria-live="polite">
      <div class="route-result">
        <div>Distance: <strong><span id="distanceVal">-</span> km</strong></div>
        <div>Estimated time: <strong><span id="timeVal">-</span> min</strong></div>
        <div><span class="route-swatch selected"></span>Profile: <strong><span id="profileVal">-</span></strong></div>
        <div class="experimental" id="experimentalNote"></div>
      </div>
      <div class="no-route" hidden>No route was found for this profile.</div>
      <div id="comparisonInfo" hidden>
        <div class="comparison-title"><span class="route-swatch distance"></span>Distance-only comparison</div>
        <div>Shortest route: <strong><span id="comparisonDistanceVal">-</span> km</strong>, <span id="comparisonTimeVal">-</span> min</div>
        <div id="comparisonDelta"></div>
      </div>
    </div>
  </div>
</section>
"""

WELCOME_HTML = """
<div class="routing-modal-overlay" id="welcomeModalOverlay">
  <div class="routing-modal">
    <h2>OSWM accessible routing</h2>
    <p>This experimental router uses mapped OpenStreetMap accessibility information and estimated terrain slope.</p>
    <ol>
      <li>Select a routing profile.</li>
      <li>Optionally compare it with the distance-only route.</li>
      <li>Click a route origin, then a destination.</li>
      <li>A third click starts a new route.</li>
    </ol>
    <p>Missing data can affect the result. Profile grades are provisional and are not an accessibility guarantee.</p>
    <button id="modalOkBtn">Continue</button>
  </div>
</div>
"""


def _routing_js(data_url: str, profiles_url: str) -> str:
    return f"""
const turf = window.OSWMTurf;
const PathFinder = window.OSWMPathFinder;
const profileSelect = document.getElementById('profileSelect');
const profileDescription = document.getElementById('profileDescription');
const compareOption = document.getElementById('compareOption');
const compareDistance = document.getElementById('compareDistance');
const comparisonInfo = document.getElementById('comparisonInfo');
const routeInfo = document.getElementById('routeInfo');
const routingPanel = document.getElementById('routingPanel');
const routingPanelHeader = document.getElementById('routingPanelHeader');
const panelToggleBtn = document.getElementById('panelToggleBtn');
let originalData = null;
let profilePayload = null;
let distanceProfileId = null;
let start = null;
let end = null;
let bestPath = null;
let comparisonPath = null;
let markers = [];

routingPanelHeader.addEventListener('click', () => {{
    const collapsed = routingPanel.classList.toggle('collapsed');
    panelToggleBtn.setAttribute('aria-expanded', String(!collapsed));
}});
document.getElementById('modalOkBtn').addEventListener('click', () => {{
    document.getElementById('welcomeModalOverlay').hidden = true;
}});

function requireOk(response) {{
    if (!response.ok) throw new Error(`${{response.status}} ${{response.statusText}}`);
    return response;
}}

function selectedProfile() {{ return profilePayload.profiles[profileSelect.value]; }}
function selectedProfileLabel() {{ return selectedProfile().label; }}

function populateProfiles() {{
    profileSelect.replaceChildren();
    const profiles = Object.entries(profilePayload.profiles).sort(([leftId, left], [rightId, right]) => {{
        if (leftId === rightId) return 0;
        if (leftId === 'wheelchair') return -1;
        if (rightId === 'wheelchair') return 1;
        if (leftId === distanceProfileId) return 1;
        if (rightId === distanceProfileId) return -1;
        return left.label.localeCompare(right.label);
    }});
    for (const [profileId, profile] of profiles) {{
        const option = document.createElement('option');
        option.value = profileId;
        option.textContent = profile.label;
        profileSelect.appendChild(option);
    }}
    profileSelect.value = profilePayload.profiles.wheelchair ? 'wheelchair' : profiles[0][0];
}}

function updateProfileControls() {{
    const profile = selectedProfile();
    const distanceOnly = profile.routing_mode === 'distance';
    profileDescription.textContent = profile.description;
    compareOption.hidden = distanceOnly;
    compareDistance.disabled = distanceOnly;
    if (distanceOnly) {{
        compareDistance.checked = false;
        removeComparisonPath();
        comparisonInfo.hidden = true;
    }}
}}

profileSelect.addEventListener('change', () => {{
    updateProfileControls();
    if (start && end) calculateRoute();
}});
compareDistance.addEventListener('change', () => {{
    if (start && end) calculateRoute();
    else if (!compareDistance.checked) {{ removeComparisonPath(); comparisonInfo.hidden = true; }}
}});

function nearestNetworkPoint(coordinates) {{
    const target = turf.point(coordinates);
    let best = null;
    let bestDistance = Infinity;
    for (const feature of originalData.features) {{
        if (feature.geometry.type !== 'LineString') continue;
        const candidate = turf.nearestPointOnLine(feature, target, {{units: 'meters'}});
        const distance = turf.distance(target, candidate, {{units: 'meters'}});
        if (distance < bestDistance) {{
            bestDistance = distance;
            best = {{coordinates: candidate.geometry.coordinates, routingId: feature.properties.routing_id}};
        }}
    }}
    return best;
}}

function addMarker(coordinates, color) {{
    const element = document.createElement('div');
    element.className = 'route-marker';
    element.style.backgroundColor = color;
    markers.push(new maplibregl.Marker({{element}}).setLngLat(coordinates).addTo(map));
}}

function splitFeatureAtSnaps(feature, snaps) {{
    let parts = [feature];
    for (const snap of snaps) {{
        parts = parts.flatMap(part => {{
            const split = turf.lineSplit(part, turf.point(snap.coordinates));
            if (split.features.length <= 1) return [part];
            return split.features.map(piece => ({{...piece, properties: {{...feature.properties}}}}));
        }});
    }}
    return parts;
}}

function queryNetwork() {{
    const snapsByFeature = new Map();
    for (const snap of [start, end]) {{
        const list = snapsByFeature.get(snap.routingId) || [];
        list.push(snap);
        snapsByFeature.set(snap.routingId, list);
    }}
    return {{
        type: 'FeatureCollection',
        features: originalData.features.flatMap(feature => {{
            const snaps = snapsByFeature.get(feature.properties.routing_id);
            return snaps ? splitFeatureAtSnaps(feature, snaps) : [feature];
        }})
    }};
}}

function gradeMultiplier(profile, grade) {{
    for (const band of profile.cost.grade_multipliers) {{
        if (grade >= band.min_grade) return band.multiplier;
    }}
    return null;
}}

function profileWeight(profileId) {{
    const profile = profilePayload.profiles[profileId];
    return (a, b, properties) => {{
        const segmentM = turf.distance(turf.point(a), turf.point(b), {{units: 'meters'}});
        if (profile.routing_mode === 'distance') return segmentM;
        const edgeKind = properties.edge_kind || 'footway';
        const eventPenalty = profile.cost.event_penalties_m[edgeKind];
        if (eventPenalty === null || eventPenalty === undefined) return 0;
        const featureLength = Math.max(Number(properties.length_m) || segmentM, segmentM);
        const proportionalPenalty = eventPenalty * segmentM / featureLength;
        const directionalCost = direction => {{
            const suffix = direction === 'forward' ? 'fwd' : 'bwd';
            if (properties[`${{profileId}}_allow_${{suffix}}`] === false) return 0;
            const grade = Number(properties[`${{profileId}}_grade_${{suffix}}`]);
            const multiplier = gradeMultiplier(profile, grade);
            if (!Number.isFinite(grade) || grade <= 0 || multiplier === null) return 0;
            return segmentM * multiplier + proportionalPenalty;
        }};
        return {{forward: directionalCost('forward'), backward: directionalCost('backward')}};
    }};
}}

function findPath(network, profileId) {{
    const pathFinder = new PathFinder(network, {{tolerance: 1e-5, weight: profileWeight(profileId)}});
    return pathFinder.findPath(turf.point(start.coordinates), turf.point(end.coordinates));
}}
function hasUsablePath(path) {{ return Boolean(path?.path && path.path.length >= 2); }}

function setRouteLayer(path, sourceId, layerId, paint) {{
    const data = turf.featureCollection([turf.lineString(path.path)]);
    if (map.getSource(sourceId)) {{ map.getSource(sourceId).setData(data); return; }}
    map.addSource(sourceId, {{type: 'geojson', data}});
    map.addLayer({{id: layerId, type: 'line', source: sourceId,
        layout: {{'line-join': 'round', 'line-cap': 'round'}}, paint}});
}}

function calculateRoute() {{
    const network = queryNetwork();
    const profileId = profileSelect.value;
    const profile = selectedProfile();
    const shouldCompare = compareDistance.checked && profile.routing_mode !== 'distance';
    bestPath = findPath(network, profileId);
    const distancePath = profile.routing_mode === 'distance' ? bestPath : findPath(network, distanceProfileId);
    comparisonPath = shouldCompare ? distancePath : null;

    if (hasUsablePath(comparisonPath)) {{
        setRouteLayer(comparisonPath, 'distance-comparison-path', 'distance-comparison-path-layer',
            {{'line-color': '#d55e00', 'line-width': 5, 'line-dasharray': [2,1.5], 'line-offset': 5}});
    }} else removeComparisonPath();

    if (!hasUsablePath(bestPath)) {{
        showNoRoute(hasUsablePath(distancePath)
            ? `No route found for ${{profile.label}}: the path is blocked by barriers or steep inclines.`
            : 'No route found: the endpoints belong to disconnected sidewalk networks.');
        removePrimaryPath();
        updateComparisonInfo(null, comparisonPath);
        return;
    }}

    const pathLine = turf.lineString(bestPath.path);
    setRouteLayer(bestPath, 'best-path', 'best-path-layer', {{'line-color': '#123bd1', 'line-width': 8}});
    if (map.getLayer('distance-comparison-path-layer')) map.moveLayer('best-path-layer');
    const distanceKm = turf.length(pathLine, {{units: 'kilometers'}});
    const timeMinutes = Math.max(1, Math.round(distanceKm / profile.speed_kmh * 60));
    document.getElementById('distanceVal').textContent = distanceKm.toFixed(2);
    document.getElementById('timeVal').textContent = timeMinutes;
    document.getElementById('profileVal').textContent = selectedProfileLabel();
    document.getElementById('experimentalNote').textContent = profile.provisional
        ? 'This accessibility profile is provisional and requires calibration.' : '';
    routeInfo.querySelector('.route-result').hidden = false;
    routeInfo.querySelector('.no-route').hidden = true;
    routeInfo.classList.remove('hidden');
    updateComparisonInfo(bestPath, comparisonPath);
}}

function updateComparisonInfo(selectedPath, distancePath) {{
    if (!compareDistance.checked || !hasUsablePath(distancePath)) {{ comparisonInfo.hidden = true; return; }}
    const distanceKm = turf.length(turf.lineString(distancePath.path), {{units: 'kilometers'}});
    const distanceProfile = profilePayload.profiles[distanceProfileId];
    document.getElementById('comparisonDistanceVal').textContent = distanceKm.toFixed(2);
    document.getElementById('comparisonTimeVal').textContent = Math.max(1, Math.round(distanceKm / distanceProfile.speed_kmh * 60));
    const deltaElement = document.getElementById('comparisonDelta');
    if (!hasUsablePath(selectedPath)) {{
        deltaElement.textContent = 'A shortest-distance route exists, but the selected profile found no usable route.';
    }} else {{
        const selectedKm = turf.length(turf.lineString(selectedPath.path), {{units: 'kilometers'}});
        const deltaKm = selectedKm - distanceKm;
        if (Math.abs(deltaKm) < .005) deltaElement.textContent = 'The selected and distance-only routes have the same length.';
        else {{
            const percentage = distanceKm > 0 ? Math.abs(deltaKm) / distanceKm * 100 : 0;
            deltaElement.textContent = `Selected route: ${{Math.abs(deltaKm).toFixed(2)}} km ${{deltaKm > 0 ? 'longer' : 'shorter'}} (${{percentage.toFixed(1)}}%).`;
        }}
    }}
    comparisonInfo.hidden = false;
}}

function showNoRoute(message) {{
    const noRoute = routeInfo.querySelector('.no-route');
    noRoute.textContent = message || 'No route was found for this profile.';
    routeInfo.querySelector('.route-result').hidden = true;
    noRoute.hidden = false;
    routeInfo.classList.remove('hidden');
}}
function hideRouteInfo() {{ routeInfo.classList.add('hidden'); }}
function removePath(sourceId, layerId) {{
    if (map.getLayer(layerId)) map.removeLayer(layerId);
    if (map.getSource(sourceId)) map.removeSource(sourceId);
}}
function removePrimaryPath() {{ removePath('best-path', 'best-path-layer'); }}
function removeComparisonPath() {{
    removePath('distance-comparison-path', 'distance-comparison-path-layer');
    comparisonPath = null;
}}
function resetPath() {{
    start = null; end = null; bestPath = null; comparisonPath = null;
    markers.forEach(marker => marker.remove()); markers = [];
    removePrimaryPath(); removeComparisonPath(); comparisonInfo.hidden = true; hideRouteInfo();
}}

map.on('click', event => {{
    if (!originalData) return;
    const snapped = nearestNetworkPoint([event.lngLat.lng, event.lngLat.lat]);
    if (!snapped) return;
    if (!start) {{ start = snapped; addMarker(snapped.coordinates, '#0f5128'); hideRouteInfo(); }}
    else if (!end) {{ end = snapped; addMarker(snapped.coordinates, '#8b0000'); calculateRoute(); }}
    else {{ resetPath(); start = snapped; addMarker(snapped.coordinates, '#0f5128'); }}
}});

Promise.all([
    fetch({json.dumps(data_url)}).then(requireOk).then(response => response.json()),
    fetch({json.dumps(profiles_url)}).then(requireOk).then(response => response.json())
]).then(([data, profiles]) => {{
    originalData = data;
    profilePayload = profiles;
    distanceProfileId = profiles.distance_profile_id;
    if (!distanceProfileId || profiles.profiles[distanceProfileId]?.routing_mode !== 'distance') {{
        throw new Error('No distance-only routing profile was provided.');
    }}
    populateProfiles();
    updateProfileControls();
    map.fitBounds(turf.bbox(data), {{padding: 35}});
}}).catch(error => {{
    console.error(error);
    showNoRoute(`Routing data could not be loaded: ${{error.message}}`);
}});
"""


def build_map(
    *,
    data_url: str = ROUTING_DATA_URL,
    profiles_url: str = PROFILES_URL,
) -> Map:
    map_object = Map(
        title="OSWM Accessible Routing (Maplibreum)",
        map_style=raster_style("light"),
        center=[-49.274, -25.465],
        zoom=14,
        pitch=48,
        width="100%",
        height="100vh",
        custom_css=ROUTING_CSS,
        container_id="oswm-routing-map",
    )
    map_object.add_external_module(
        "https://esm.sh/@turf/turf@7.3.5", "OSWMTurf"
    )
    map_object.add_external_module(
        "https://esm.sh/geojson-path-finder@2.1.0",
        "OSWMPathFinder",
        export_name="default",
    )

    map_object.add_source(
        "aws-terrain",
        RasterDemSource(
            tiles="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
            encoding="terrarium",
            tile_size=256,
            max_zoom=15,
        ),
    )
    map_object.add_source("line", GeoJSONSource(data_url))
    map_object.add_source("boundaries", GeoJSONSource(BOUNDARY_URL))
    map_object.add_layer(
        HillshadeLayer(
            "hills",
            "aws-terrain",
            paint={"hillshade-exaggeration": 0.45, "hillshade-shadow-color": "#473b30"},
        )
    )
    map_object.add_layer(
        LineLayer(
            "line-layer",
            "line",
            layout={"line-join": "round", "line-cap": "round"},
            paint={
                "line-color": [
                    "match",
                    ["get", "edge_kind"],
                    "crossing",
                    "#704ba0",
                    "stairs",
                    "#bd5b00",
                    "#4682b4",
                ],
                "line-width": 4,
                "line-opacity": 0.82,
            },
        )
    )
    map_object.add_layer(
        LineLayer(
            "boundary-layer",
            "boundaries",
            paint={"line-color": "#000", "line-width": 0.3},
        )
    )
    map_object.set_terrain("aws-terrain", exaggeration=1.2)
    add_standard_controls(map_object)
    map_object.add_control(
        "terrain", "top-right", {"source": "aws-terrain", "exaggeration": 1.2}
    )

    map_object.add_control(
        PanelControl(
            html_content=(
                f'<a href="{BASE_URL}" title="Open the OSWM node">'
                f'<img src="{BASE_URL}oswm_codebase/assets/branding/logos/page_logo.png" '
                'alt="OpenSidewalkMap"></a>'
            ),
            css_class="oswm-routing-logo",
        )
    )
    map_object.add_control(
        PanelControl(html_content=ROUTING_PANEL_HTML, css_class="oswm-routing-ui")
    )
    map_object.add_control(
        PanelControl(html_content=WELCOME_HTML, css_class="oswm-routing-welcome")
    )
    map_object.add_on_load_js(_routing_js(data_url, profiles_url))
    return map_object


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-url", default=ROUTING_DATA_URL)
    parser.add_argument("--profiles-url", default=PROFILES_URL)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(save_map(build_map(data_url=args.data_url, profiles_url=args.profiles_url), args.output))


if __name__ == "__main__":
    main()
