"""Reproduce OSWM's pedestrian-data acquisition dashboard with Maplibreum."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from maplibreum import Map
from maplibreum.layers import FillLayer, LineLayer
from maplibreum.sources import GeoJSONSource

from .common import BASE_URL, empty_feature_collection, load_json, raster_style, save_map


RESULTS_URL = f"{BASE_URL}hub/acquisition/results.json"
BOUNDARY_URL = f"{BASE_URL}data/boundaries/polygon.geojson"
DEFAULT_OUTPUT = Path(__file__).with_name("generated") / "acquisition.html"

ACQUISITION_CSS = """
:root {
    --acq-bg: #0f172a; --acq-card: rgba(30,41,59,.92); --acq-border: rgba(255,255,255,.08);
    --acq-primary: #00f2fe; --acq-secondary: #4facfe; --acq-text: #f8fafc; --acq-muted: #94a3b8;
    --acq-success: #10b981; --acq-warning: #f59e0b; --acq-error: #ef4444; --acq-purple: #8b5cf6;
}
* { box-sizing:border-box; }
body {
    background: linear-gradient(135deg,#0f172a 0%,#1e1b4b 100%); color:var(--acq-text);
    display:grid; font-family:'Outfit',sans-serif; gap:1.25rem;
    grid-template-columns:1fr; grid-template-rows:auto auto minmax(500px,1fr) auto;
    min-height:100vh; padding-bottom:2rem;
}
#oswm-acquisition-map { border:1px solid var(--acq-border); border-radius:16px; grid-column:1; grid-row:3; height:100% !important; margin:0 2rem; min-height:500px; overflow:hidden; width:calc(100% - 4rem) !important; }
.acquisition-header { backdrop-filter:blur(12px); background:rgba(15,23,42,.65); border-bottom:1px solid var(--acq-border); grid-row:1; padding:1.25rem 2rem; }
.acquisition-header-inner { align-items:center; display:flex; justify-content:space-between; margin:0 auto; max-width:1400px; }
.acquisition-header h1 { background:linear-gradient(to right,var(--acq-primary),var(--acq-secondary)); background-clip:text; font-size:1.4rem; font-weight:600; margin:0; -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.acquisition-timestamp { color:var(--acq-muted); font-family:'Fira Code',monospace; font-size:.85rem; }
.acquisition-stats { display:grid; gap:1.25rem; grid-row:2; grid-template-columns:repeat(4,minmax(150px,1fr)); margin:0 2rem; }
.acquisition-stat, .acquisition-project-panel, .acquisition-status { backdrop-filter:blur(16px); background:var(--acq-card); border:1px solid var(--acq-border); border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,.2); }
.acquisition-stat { padding:1.2rem 1.5rem; }
.acquisition-stat .label { color:var(--acq-muted); font-size:.78rem; letter-spacing:1px; text-transform:uppercase; }
.acquisition-stat .value { color:var(--acq-primary); font-size:1.8rem; font-weight:700; }
.acquisition-project-panel { grid-column:1; grid-row:3; margin:0 2rem; overflow:auto; padding:1.5rem; position:relative; transition:background .2s; z-index:4; }
.acquisition-project-panel.map-mode { background:transparent; border-color:transparent; box-shadow:none; overflow:visible; pointer-events:none; }
.acquisition-project-panel.map-mode .acquisition-panel-bar { backdrop-filter:blur(16px); background:rgba(15,23,42,.9); border:1px solid var(--acq-border); border-radius:12px; padding:12px; pointer-events:auto; }
.acquisition-panel-heading { align-items:center; display:flex; flex-wrap:wrap; gap:.75rem; justify-content:space-between; margin-bottom:1.25rem; }
.acquisition-panel-heading h2 { font-size:1.15rem; margin:0; }
.acquisition-view-toggle { background:rgba(15,23,42,.4); border:1px solid var(--acq-border); border-radius:8px; display:flex; padding:2px; }
.acquisition-view-btn { background:none; border:0; border-radius:6px; color:var(--acq-muted); cursor:pointer; font-family:inherit; font-size:.85rem; font-weight:500; padding:.4rem 1rem; }
.acquisition-view-btn.active { background:var(--acq-primary); color:#0f172a; }
.acquisition-tabs { border-bottom:2px solid var(--acq-border); display:flex; overflow-x:auto; }
.acquisition-tab { background:none; border:0; border-bottom:2px solid transparent; color:var(--acq-muted); cursor:pointer; font-family:inherit; margin-bottom:-2px; padding:.7rem 1.2rem; white-space:nowrap; }
.acquisition-tab.active { border-bottom-color:var(--acq-primary); color:var(--acq-primary); }
.acquisition-tab-count { background:rgba(0,242,254,.12); border-radius:10px; color:var(--acq-primary); font-size:.72rem; font-weight:600; margin-left:.35rem; padding:.05rem .4rem; }
.acquisition-controls { display:flex; margin:1rem 0; }
.acquisition-search { background:rgba(15,23,42,.72); border:1px solid var(--acq-border); border-radius:8px; color:var(--acq-text); flex:1; font:inherit; min-width:200px; outline:none; padding:.6rem 1rem; }
.acquisition-search:focus { border-color:rgba(0,242,254,.5); }
.acquisition-table-area { overflow:auto; }
.acquisition-project-panel.map-mode .acquisition-table-area { display:none; }
.acquisition-projects-table { border-collapse:collapse; width:100%; }
.acquisition-projects-table th { border-bottom:1px solid var(--acq-border); color:var(--acq-muted); font-size:.75rem; letter-spacing:.8px; padding:.75rem 1rem; text-align:left; text-transform:uppercase; }
.acquisition-projects-table td { border-bottom:1px solid rgba(255,255,255,.03); font-size:.88rem; padding:.75rem 1rem; vertical-align:top; }
.acquisition-project-title { color:var(--acq-primary); font-weight:500; text-decoration:none; }
.acquisition-project-description { color:var(--acq-muted); max-width:360px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.acquisition-keyword { background:rgba(0,242,254,.1); border-radius:4px; color:var(--acq-primary); display:inline-block; font-size:.72rem; font-weight:600; margin:.1rem; padding:.1rem .45rem; }
.acquisition-status-tag { background:rgba(255,255,255,.08); border-radius:4px; color:var(--acq-muted); font-size:.75rem; font-weight:600; padding:.15rem .5rem; }
.acquisition-status-tag.active { background:rgba(16,185,129,.15); color:var(--acq-success); }
.acquisition-status { grid-row:4; margin:0 2rem; padding:1.25rem 1.5rem; }
.acquisition-status h2 { font-size:1.1rem; margin:0 0 1rem; }
.acquisition-service-badges { display:flex; flex-wrap:wrap; gap:.75rem; }
.acquisition-service-badge { align-items:center; background:rgba(255,255,255,.03); border:1px solid var(--acq-border); border-radius:8px; display:inline-flex; font-size:.85rem; gap:.4rem; padding:.4rem .9rem; }
.acquisition-service-dot { border-radius:50%; height:8px; width:8px; }
.acquisition-service-dot.ok { background:var(--acq-success); box-shadow:0 0 6px var(--acq-success); }
.acquisition-service-dot.offline { background:var(--acq-error); }
.acquisition-service-dot.error { background:var(--acq-warning); }
.acquisition-empty { color:var(--acq-muted); padding:3rem 1rem; text-align:center; }
.acquisition-marker { align-items:center; border:2px solid #fff; border-radius:50% 50% 50% 0; box-shadow:0 4px 10px rgba(0,0,0,.3); cursor:pointer; display:flex; height:32px; justify-content:center; transform:rotate(-45deg); width:32px; }
.acquisition-marker span { font-size:16px; transform:rotate(45deg); }
.acquisition-marker.tasking { background:#e04c3f; } .acquisition-marker.roulette { background:#10b981; } .acquisition-marker.pic { background:#8b5cf6; }
.maplibregl-popup-content { background:#fff !important; border-radius:12px !important; color:#0f172a !important; padding:12px 16px !important; }
@media (max-width: 800px) {
    body { grid-template-rows:auto auto minmax(520px,1fr) auto; }
    .acquisition-stats { grid-template-columns:repeat(2,1fr); margin:0 1rem; }
    #oswm-acquisition-map, .acquisition-project-panel, .acquisition-status { margin-left:1rem; margin-right:1rem; width:calc(100% - 2rem) !important; }
    .acquisition-timestamp { display:none; }
}
"""


def projects_geojson(projects: list[dict[str, Any]]) -> dict[str, Any]:
    features = []
    for project in projects:
        geometry = project.get("geometry")
        if geometry is None and project.get("bbox"):
            west, south, east, north = project["bbox"]
            geometry = {
                "type": "Polygon",
                "coordinates": [
                    [[west, south], [west, north], [east, north], [east, south], [west, south]]
                ],
            }
        if geometry:
            features.append(
                {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "service": project.get("service", "Unknown"),
                        "id": str(project.get("id", "")),
                        "title": project.get("title", "Untitled"),
                    },
                }
            )
    return {"type": "FeatureCollection", "features": features}


def _header_html(node_name: str, generated_at: str) -> str:
    try:
        timestamp = datetime.fromisoformat(generated_at.replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    except ValueError:
        timestamp = generated_at
    return f"""
<header class="acquisition-header">
  <div class="acquisition-header-inner">
    <h1>🚶 OSWM Data Acquisition — {node_name}</h1>
    <span class="acquisition-timestamp">{timestamp}</span>
  </div>
</header>
"""


def _dashboard_html() -> str:
    return """
<section class="acquisition-stats" id="acquisitionStats"></section>
<section class="acquisition-project-panel" id="acquisitionProjectPanel">
  <div class="acquisition-panel-bar">
    <div class="acquisition-panel-heading">
      <h2>📋 Discovered Projects</h2>
      <div class="acquisition-view-toggle">
        <button class="acquisition-view-btn active" id="acquisitionListView">📋 List View</button>
        <button class="acquisition-view-btn" id="acquisitionMapView">🗺️ Map View</button>
      </div>
    </div>
    <div class="acquisition-tabs" id="acquisitionTabs"></div>
    <div class="acquisition-controls"><input class="acquisition-search" id="acquisitionSearch" type="search" placeholder="Filter projects by title or keyword…"></div>
  </div>
  <div class="acquisition-table-area" id="acquisitionTable"></div>
</section>
<section class="acquisition-status">
  <h2>📡 Service Status</h2>
  <div class="acquisition-service-badges" id="acquisitionServiceBadges"></div>
</section>
"""


def _application_js(projects: list[dict[str, Any]], service_status: dict[str, Any]) -> str:
    projects_json = json.dumps(projects, separators=(",", ":"))
    status_json = json.dumps(service_status, separators=(",", ":"))
    return f"""
const acquisitionProjects = {projects_json};
const acquisitionServiceStatus = {status_json};
let acquisitionTab = 'all';
let acquisitionMarkers = [];
const acquisitionEscape = value => String(value ?? '').replace(/[&<>"']/g, character =>
    ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[character]);
const acquisitionSafeUrl = value => {{
    try {{ const url = new URL(value); return ['http:','https:'].includes(url.protocol) ? url.href : '#'; }}
    catch (_error) {{ return '#'; }}
}};

function acquisitionFilteredProjects() {{
    const query = document.getElementById('acquisitionSearch').value.toLowerCase();
    return acquisitionProjects.filter(project => {{
        if (acquisitionTab !== 'all' && project.service !== acquisitionTab) return false;
        return !query || (project.title || '').toLowerCase().includes(query)
            || (project.description || '').toLowerCase().includes(query)
            || (project.matched_keywords || []).some(keyword => keyword.toLowerCase().includes(query));
    }});
}}

function renderAcquisitionStats() {{
    const services = new Set(acquisitionProjects.map(project => project.service));
    const keywords = new Set(acquisitionProjects.flatMap(project => project.matched_keywords || []));
    const cards = [['Total Projects',acquisitionProjects.length],['Services Queried',Object.keys(acquisitionServiceStatus).length],['Unique Keywords',keywords.size],['Active Services',services.size]];
    document.getElementById('acquisitionStats').innerHTML = cards.map(card => `<div class="acquisition-stat"><div class="label">${{card[0]}}</div><div class="value">${{card[1]}}</div></div>`).join('');
}}
function renderAcquisitionServices() {{
    document.getElementById('acquisitionServiceBadges').innerHTML = Object.entries(acquisitionServiceStatus).map(([name,info]) => {{
        const status = info.status || 'error';
        const statusClass = status === 'ok' || status.includes('online') ? 'ok' : status === 'offline' ? 'offline' : 'error';
        return `<div class="acquisition-service-badge"><span class="acquisition-service-dot ${{statusClass}}"></span>${{acquisitionEscape(name)}}</div>`;
    }}).join('');
}}
function renderAcquisitionTabs() {{
    const counts = {{}};
    acquisitionProjects.forEach(project => counts[project.service || 'Unknown'] = (counts[project.service || 'Unknown'] || 0) + 1);
    const entries = [['all','All',acquisitionProjects.length],...Object.entries(counts).map(([service,count]) => [service,service,count])];
    const container = document.getElementById('acquisitionTabs');
    container.innerHTML = entries.map(([value,label,count]) => `<button class="acquisition-tab ${{value === acquisitionTab ? 'active' : ''}}" data-service="${{acquisitionEscape(value)}}">${{acquisitionEscape(label)}}<span class="acquisition-tab-count">${{count}}</span></button>`).join('');
    container.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {{ acquisitionTab=button.dataset.service; renderAcquisitionTabs(); applyAcquisitionFilters(); }}));
}}
function renderAcquisitionTable(projects) {{
    const container = document.getElementById('acquisitionTable');
    if (!projects.length) {{ container.innerHTML='<div class="acquisition-empty">🔎<p>No projects found matching your criteria.</p></div>'; return; }}
    const active = new Set(['ready','published','active','building','partially loaded']);
    const rows = projects.map(project => {{
        const keywords = (project.matched_keywords || []).map(keyword => `<span class="acquisition-keyword">${{acquisitionEscape(keyword)}}</span>`).join('');
        const host = String(project.instance || '').replace(/^https?:\\/\\//,'').replace(/\\/$/,'');
        return `<tr><td><a class="acquisition-project-title" href="${{acquisitionSafeUrl(project.url)}}" target="_blank" rel="noopener">${{acquisitionEscape(project.title || 'Untitled')}}</a></td><td>${{acquisitionEscape(host)}}</td><td><span class="acquisition-status-tag ${{active.has(String(project.status || '').toLowerCase()) ? 'active' : ''}}">${{acquisitionEscape(project.status || 'N/A')}}</span></td><td>${{keywords}}</td><td class="acquisition-project-description" title="${{acquisitionEscape(project.description || '')}}">${{acquisitionEscape(project.description || '')}}</td></tr>`;
    }}).join('');
    container.innerHTML = `<table class="acquisition-projects-table"><thead><tr><th>Title</th><th>Instance</th><th>Status</th><th>Keywords</th><th>Description</th></tr></thead><tbody>${{rows}}</tbody></table>`;
}}
function acquisitionGeometry(project) {{
    if (project.geometry) return project.geometry;
    if (!project.bbox) return null;
    const [west,south,east,north] = project.bbox;
    return {{type:'Polygon',coordinates:[[[west,south],[west,north],[east,north],[east,south],[west,south]]]}};
}}
function acquisitionCentroid(project) {{
    const geometry = acquisitionGeometry(project);
    if (!geometry) return null;
    if (geometry.type === 'Point') return geometry.coordinates;
    const coordinates = geometry.coordinates?.[0];
    if (!coordinates?.length) return null;
    const total = coordinates.reduce((sum,point) => [sum[0]+point[0],sum[1]+point[1]],[0,0]);
    return [total[0]/coordinates.length,total[1]/coordinates.length];
}}
function updateAcquisitionMap(projects) {{
    acquisitionMarkers.forEach(marker => marker.remove()); acquisitionMarkers=[];
    const features=[];
    projects.forEach(project => {{
        const geometry=acquisitionGeometry(project);
        if (geometry) features.push({{type:'Feature',geometry,properties:{{service:project.service,id:String(project.id),title:project.title}}}});
        const centroid=acquisitionCentroid(project);
        if (!centroid) return;
        const markerElement=document.createElement('div');
        const markerClass=project.service === 'MapRoulette' ? 'roulette' : project.service === 'Pic4Review' ? 'pic' : 'tasking';
        const icon=project.service === 'MapRoulette' ? '🧩' : project.service === 'Pic4Review' ? '📷' : '🗺️';
        markerElement.className=`acquisition-marker ${{markerClass}}`; markerElement.innerHTML=`<span>${{icon}}</span>`;
        const popupHtml=`<div style="font-family:Outfit,sans-serif;min-width:200px"><h3 style="font-size:.95rem;margin:0 0 .25rem">${{acquisitionEscape(project.title || 'Untitled')}}</h3><div style="color:#64748b;font-size:.72rem;font-weight:700;text-transform:uppercase">${{acquisitionEscape(project.service)}} · ${{acquisitionEscape(project.status || 'N/A')}}</div><p style="color:#475569;font-size:.8rem">${{acquisitionEscape(project.description || 'No description available.')}}</p><a href="${{acquisitionSafeUrl(project.url)}}" target="_blank" rel="noopener">Open Project</a></div>`;
        const popup=new maplibregl.Popup({{offset:15}}).setHTML(DOMPurify.sanitize(popupHtml));
        acquisitionMarkers.push(new maplibregl.Marker({{element:markerElement,anchor:'bottom'}}).setLngLat(centroid).setPopup(popup).addTo(map));
    }});
    map.getSource('project-geometries').setData({{type:'FeatureCollection',features}});
}}
function applyAcquisitionFilters() {{
    const projects=acquisitionFilteredProjects();
    renderAcquisitionTable(projects); updateAcquisitionMap(projects);
}}
function setAcquisitionView(mapMode) {{
    document.getElementById('acquisitionProjectPanel').classList.toggle('map-mode',mapMode);
    document.getElementById('acquisitionListView').classList.toggle('active',!mapMode);
    document.getElementById('acquisitionMapView').classList.toggle('active',mapMode);
    if (mapMode) requestAnimationFrame(() => map.resize());
}}
document.getElementById('acquisitionSearch').addEventListener('input',applyAcquisitionFilters);
document.getElementById('acquisitionListView').addEventListener('click',() => setAcquisitionView(false));
document.getElementById('acquisitionMapView').addEventListener('click',() => setAcquisitionView(true));
renderAcquisitionStats(); renderAcquisitionServices(); renderAcquisitionTabs(); applyAcquisitionFilters();
"""


def build_map(results: Any = RESULTS_URL) -> Map:
    payload = load_json(results)
    projects = list(payload.get("projects", []))
    service_status = dict(payload.get("service_status", {}))
    bbox = payload.get("bbox", [-25.6435043, -49.38914, -25.3449505, -49.1843182])
    south, west, north, east = bbox

    map_object = Map(
        title=f"OSWM Data Acquisition — {payload.get('node_name', 'Node')}",
        map_style=raster_style("light"),
        center=[(west + east) / 2, (south + north) / 2],
        zoom=11,
        width="100%",
        height="100%",
        custom_css=ACQUISITION_CSS,
        container_id="oswm-acquisition-map",
    )
    map_object.fit_bounds([west, south, east, north], padding=40)
    map_object.add_external_stylesheet(
        "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap"
    )
    map_object.add_control("navigation", "top-right")
    map_object.add_control("scale", "bottom-right", {"unit": "metric"})
    map_object.add_source("boundaries", GeoJSONSource(BOUNDARY_URL))
    map_object.add_source(
        "project-geometries",
        GeoJSONSource(projects_geojson(projects) if projects else empty_feature_collection()),
    )
    map_object.add_layer(
        LineLayer(
            "boundary-layer",
            "boundaries",
            paint={
                "line-color": "#00f2fe",
                "line-width": 1.5,
                "line-opacity": 0.6,
                "line-dasharray": [4, 4],
            },
        )
    )
    service_color = [
        "match",
        ["get", "service"],
        "Tasking Manager",
        "#e04c3f",
        "MapRoulette",
        "#10b981",
        "Pic4Review",
        "#8b5cf6",
        "#4682b4",
    ]
    map_object.add_layer(
        FillLayer(
            "project-fills",
            "project-geometries",
            paint={"fill-color": service_color, "fill-opacity": 0.15},
        )
    )
    map_object.add_layer(
        LineLayer(
            "project-borders",
            "project-geometries",
            paint={
                "line-color": service_color,
                "line-width": 2,
                "line-dasharray": [2, 2],
            },
        )
    )
    map_object.add_page_element(
        _header_html(payload.get("node_name", "Node"), payload.get("generated_at", "")),
        before_map=True,
    )
    map_object.add_page_element(_dashboard_html())
    map_object.add_on_load_js(_application_js(projects, service_status))
    return map_object


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default=RESULTS_URL, help="Acquisition results JSON path or URL")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(save_map(build_map(args.results), args.output))


if __name__ == "__main__":
    main()
