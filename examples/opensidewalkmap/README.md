# OpenSidewalkMap field test

These five Python builders reproduce every distinct MapLibre map currently deployed from the `opensidewalkmap_beta` main node. They exercise Maplibreum against production PMTiles, large temporal GeoJSON, terrain, third-party ES modules, rich dashboard layouts, and application-specific interaction logic.

| Python builder | Reference deployment | Reproduced behavior |
|---|---|---|
| `main_webmap.py` | [`map.html`](https://kauevestena.github.io/opensidewalkmap_beta/map.html) | Ten complete map themes, PMTiles sources, native layer legend, viewport theme charts, snapshot export, hover state, property popups and external links |
| `routing.py` | [`routing_demo.html`](https://kauevestena.github.io/opensidewalkmap_beta/oswm_codebase/routing/routing_demo.html) | Accessible routing profiles, click-to-route snapping, directional weights, terrain/hillshade, markers, and distance-only comparison |
| `hazard_analysis.py` | [`hazard_analysis.html`](https://kauevestena.github.io/opensidewalkmap_beta/oswm_codebase/hazard_analysis/hazard_analysis.html) | Profile/category/severity/confidence filters, unknown-data and terrain overlays, feature-state hover, evidence popups, and screening guidance |
| `completeness.py` | [`completeness/index.html`](https://kauevestena.github.io/opensidewalkmap_beta/quality_check/completeness/) | Zoom-dependent tile grid, footway/sidewalk metric selection, history slider, tile trend popups, histogram, boxplot, and manual/automatic zoom selection |
| `acquisition.py` | [`acquisition/index.html`](https://kauevestena.github.io/opensidewalkmap_beta/hub/acquisition/) | Responsive discovery dashboard, service tabs, search, list/map switch, status cards, project footprints, branded markers, and project popups |

The builders use Maplibreum for map construction, styles, sources, layers, controls, terrain, PMTiles registration, page layout, module/style dependencies, popups, and event bindings. Raw JavaScript is confined to the domain algorithms and highly stateful application behavior that has no declarative MapLibre equivalent (routing, charts, dynamic filtering, and dashboard rendering).

## Generate all examples

From the Maplibreum repository:

```bash
python -m examples.opensidewalkmap.generate_all
```

To use JSON inputs from a fresh adjacent OpenSidewalkMap checkout while keeping that checkout read-only:

```bash
python -m examples.opensidewalkmap.generate_all \
  --source-root ../opensidewalkmap_beta \
  --output-dir /tmp/maplibreum-oswm-field-test
```

The routing graph remains a deployed URL because `data/routing/demo.geojson` is generated during OpenSidewalkMap deployment and is not tracked in the source checkout. Generated HTML is intentionally ignored by Git; each builder can also be imported and displayed in a notebook:

```python
from examples.opensidewalkmap.routing import build_map

build_map()
```

Each `build_map` function accepts injectable paths, URLs, or payloads for its non-map metadata, which keeps the examples deterministic and unit-testable.
