"""Reproduce the primary ``opensidewalkmap_beta`` web map with Maplibreum."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from maplibreum import Map, StyleSwitcherControl
from maplibreum.controls import PanelControl

from .common import BASE_URL, add_pmtiles_v4, add_standard_controls, load_json, save_map


PARAMS_URL = f"{BASE_URL}webmap_params.json"
DEFAULT_OUTPUT = Path(__file__).with_name("generated") / "main_webmap.html"
DATA_LAYERS = (
    "sidewalks",
    "crossings",
    "kerbs",
    "stairways",
    "main_footways",
    "potential_footways",
    "informal_footways",
    "pedestrian_areas",
)

MAIN_CSS = """
body { background: #000; overflow: hidden; }
.oswm-logo-panel { left: 2px !important; pointer-events: auto; position: absolute; top: 2px !important; z-index: 20; }
.oswm-logo-panel img { display: block; height: auto; max-width: min(40vw, 330px); }
.oswm-symbology-panel {
    background: rgba(255, 255, 255, .96); border-radius: 5px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, .3); display: none;
    left: 1% !important; max-height: 70vh; max-width: 360px; overflow-y: auto;
    padding: 10px 14px; position: absolute; top: 50% !important;
    transform: translateY(-50%); z-index: 8;
}
.maplibreum-style-switcher { margin-right: 42px; }
.maplibreum-style-switcher select { font-size: 14px; min-width: 210px; }
.maplibreum-feature-popup-title { text-align: center; }
.maplibreum-feature-popup-links { justify-content: center; }
.maplibreum-feature-popup-links a { color: #087fbd; text-decoration: none; }
@media (max-width: 640px) {
    .oswm-logo-panel img { max-width: 52vw; }
    .maplibreum-style-switcher { margin-right: 0; margin-top: 110px; }
    .maplibreum-style-switcher select { min-width: 150px; width: 170px; }
    .oswm-symbology-panel { left: 8px !important; max-width: calc(100vw - 44px); }
}
"""


def _control_installation_js(params: dict[str, Any]) -> str:
    params_json = json.dumps(params, separators=(",", ":"))
    return f"""
const oswmParams = {params_json};
const styleSelector = document.getElementById('oswm-style-selector');
const symbologyPanel = map.getContainer().querySelector('.oswm-symbology-panel');
let legendControl = null;
let themeChartControl = null;

if (window.OswmLegendControl) {{
    legendControl = new window.OswmLegendControl(oswmParams, {{
        initialStyle: 'footway_categories',
        onToggle: (expanded) => {{
            if (symbologyPanel) symbologyPanel.style.display = expanded ? 'block' : 'none';
        }}
    }});
    map.addControl(legendControl, 'top-right');
}}

if (window.installThemeChartControl) {{
    themeChartControl = window.installThemeChartControl(map, oswmParams, {{
        position: 'bottom-left',
        loadECharts: () => import('https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.esm.mjs'),
        getActiveStyleKey: () => styleSelector?.value || 'footway_categories'
    }});
}}

if (window.installSnapshotControl) {{
    window.installSnapshotControl(map, oswmParams, {{
        position: 'top-right',
        getActiveStyleKey: () => styleSelector?.value || 'footway_categories'
    }});
}}

map.on('oswm-theme-chart-opened', () => legendControl?.close?.());
map.on('oswm-legend-opened', () => themeChartControl?.close?.());

map.getContainer().addEventListener('maplibreum-style-change', (event) => {{
    const styleKey = event.detail.styleKey;
    legendControl?.setActiveStyle?.(styleKey);
    themeChartControl?.setActiveStyle?.(styleKey);
    if (symbologyPanel && oswmParams.legend_fragments?.[styleKey]) {{
        symbologyPanel.innerHTML = oswmParams.legend_fragments[styleKey];
    }}
}});
"""


def build_map(params: Any = PARAMS_URL) -> Map:
    """Build the primary OSWM map from ``webmap_params.json``."""

    payload = load_json(params)
    styles = payload["styles"]
    initial_style = "footway_categories"
    labels = {
        key: f"Style: {style.get('name', key.replace('_', ' ').title())}"
        for key, style in styles.items()
    }

    map_object = Map(
        title="OpenSidewalkMap — Node Webmap (Maplibreum)",
        map_style=styles[initial_style],
        center=payload.get("center", [-49.274, -25.465]),
        zoom=payload.get("zoom", 15),
        width="100%",
        height="100vh",
        custom_css=MAIN_CSS,
        map_options={"hash": True},
        container_id="oswm-main-map",
    )
    map_object.fit_bounds(payload["bounds"])
    add_pmtiles_v4(map_object)
    add_standard_controls(map_object)

    map_object.add_control(
        StyleSwitcherControl(
            styles,
            labels=labels,
            initial_style=initial_style,
            title="OpenSidewalkMap theme",
            control_id="oswm-style-selector",
        ),
        "top-right",
    )

    map_object.add_external_stylesheet(
        f"{BASE_URL}oswm_codebase/assets/styles/oswm_legend_control.css"
    )
    map_object.add_external_stylesheet(
        f"{BASE_URL}oswm_codebase/assets/styles/webmap_theme_charts.css"
    )
    map_object.add_external_stylesheet(
        f"{BASE_URL}oswm_codebase/assets/styles/webmap_snapshot.css"
    )
    map_object.add_external_module(
        f"{BASE_URL}oswm_codebase/webmap/oswm_legend_control.js",
        "OswmLegendControl",
        export_name="OswmLegendControl",
    )
    map_object.add_external_module(
        f"{BASE_URL}oswm_codebase/webmap/theme_charts/theme_chart_control.js",
        "installThemeChartControl",
        export_name="installThemeChartControl",
    )
    map_object.add_external_module(
        f"{BASE_URL}oswm_codebase/webmap/snapshot/snapshot_control.js",
        "installSnapshotControl",
        export_name="installSnapshotControl",
    )

    map_object.add_control(
        PanelControl(
            html_content=(
                f'<a href="{payload.get("node_url", BASE_URL)}" title="Open the OSWM node">'
                f'<img src="{BASE_URL}oswm_codebase/assets/branding/logos/page_logo_dark_clean.png" '
                'alt="OpenSidewalkMap"></a>'
            ),
            css_class="oswm-logo-panel",
        )
    )
    map_object.add_control(
        PanelControl(
            html_content=payload.get("legend_fragments", {}).get(initial_style, ""),
            css_class="oswm-symbology-panel oswm-legend-symbology",
        )
    )

    popup_fields = [
        "surface",
        "smoothness",
        "width",
        "incline",
        "incline:across",
        "tactile_paving",
        "wheelchair",
        "lit",
        "last_update",
    ]
    popup_aliases = [
        "Surface",
        "Smoothness",
        "Width",
        "Incline",
        "Incline (across)",
        "Tactile paving",
        "Wheelchair",
        "Lit",
        "Last updated",
    ]
    links = [
        {
            "label": "See on OpenStreetMap",
            "url": "https://www.openstreetmap.org/{element}/{id}",
        },
        {
            "label": "Surroundings on Mapillary",
            "url": "https://www.mapillary.com/app/?lat={lat}&lng={lng}&z=19",
        },
        {
            "label": "Location on GeoHack",
            "url": "https://geohack.toolforge.org/geohack.php?params={lat}_N_{lng}_E",
        },
    ]
    for layer_id in payload.get("data_layers", DATA_LAYERS):
        source_id = f"oswm_pmtiles_{layer_id}"
        map_object.add_feature_state_hover(
            layer_id,
            source_id,
            source_layer=layer_id,
        )
        map_object.add_feature_popup(
            layer_id,
            popup_fields,
            aliases=popup_aliases,
            title=f"Feat. {{id}}: {layer_id.replace('_', ' ')}",
            links=links,
        )

    map_object.add_on_load_js(_control_installation_js(payload))
    return map_object


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--params", default=PARAMS_URL, help="webmap_params JSON path or URL")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Generated HTML path")
    args = parser.parse_args()
    print(save_map(build_map(args.params), args.output))


if __name__ == "__main__":
    main()
