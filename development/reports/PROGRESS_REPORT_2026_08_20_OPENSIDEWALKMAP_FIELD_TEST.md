# OpenSidewalkMap field test — 2026-08-20

## Scope and source revisions

The field test used fresh clones and made no tracked or untracked changes to the OpenSidewalkMap checkout.

| Repository | Role | Revision |
|---|---|---|
| `kauevestena/maplibreum_prototype` | Python library and implementation target | `4c60a411a6a19202c782a9c1dd50e0d3838760d4` (work performed on local branch `field-test/opensidewalkmap-examples`) |
| `kauevestena/opensidewalkmap_beta` | Main node and deployed-page reference | `2965337ebb7392c53e8dd10bc30de6dc93f3799f` |
| `kauevestena/oswm_codebase` | OpenSidewalkMap submodule | `42d1f4fe32942a27423bc028fef0341a2627139b` |

The inventory searched deployed and source HTML for real `new maplibregl.Map(...)` construction. It found five distinct applications:

1. the main node web map (`map.html`);
2. accessible routing (`oswm_codebase/routing/routing_demo.html`);
3. hazard analysis (`oswm_codebase/hazard_analysis/hazard_analysis.html`);
4. temporal completeness analysis (`quality_check/completeness/index.html`); and
5. acquisition discovery (`hub/acquisition/index.html`).

Documentation-only snippets in `hub/API/index.html`, Leaflet quality-control maps, deprecated/prototype pages, the main-map generator template, and the ten theme variants within the main map were excluded as redundant or non-MapLibre deployments.

## Reproductions

The implementations live in `examples/opensidewalkmap/` and can be generated together with:

```bash
python -m examples.opensidewalkmap.generate_all \
  --source-root ../opensidewalkmap_beta \
  --output-dir /tmp/maplibreum-oswm-field-test
```

| Builder | Functional coverage | Layout coverage |
|---|---|---|
| `main_webmap.py` | All ten styles; PMTiles; bounds/hash; navigation, fullscreen, scale and geolocation; feature hover; property/link popups; native layer legend; viewport theme charts; snapshot control | Linked OSWM logo, top-right style selector and native controls, detached symbology panel, responsive mobile adjustments |
| `routing.py` | Turf snapping and distance calculations; `geojson-path-finder`; directional profile weights; start/end/reset clicks; distance-only comparison; route/time/error output; DEM terrain and hillshade | Linked logo, collapsible route panel, profile selector and comparison state, start-up guidance modal, responsive bottom panel |
| `hazard_analysis.py` | PMTiles source layers per profile; category/severity/confidence filters; insufficient-data toggle; terrain image switching; feature-state hover; evidence-aware popup and external links | Linked logo, profile/filter/legend panel, screening modal, classification-guide actions, mobile panel positioning |
| `completeness.py` | Compact JSON-to-GeoJSON transformation; zoom 12–17 layers; metric and timestamp selection; auto/manual zoom; dynamic colors; tile history popup; histogram and boxplot | Dark glass top bar, right controls, left legend and chart button, statistics modal, responsive controls |
| `acquisition.py` | Statistics and service state; service tabs; search; list/map transition; filtered footprints and custom markers; safe project popups | Dashboard grid, gradient/glass cards, projects table, status panel, full map surface under the map-mode controls, responsive two-column statistics |

Application-specific JavaScript remains only where the behavior is inherently stateful or algorithmic: routing graph construction, Chart.js chart management, dynamic profile/source-layer replacement, and dashboard table/marker rendering. Map construction, dependency registration, styles, sources, layers, controls, terrain, structured popups, hover state, events, and page structure are driven through the Python API.

## Maplibreum gaps and defects fixed

| Finding | Resolution |
|---|---|
| No way to import ES modules with named/default exports before map initialization | Added `Map.add_external_module(...)` with validation and deterministic global exposure |
| No reusable complete-style selector | Added and exported `StyleSwitcherControl`; it dispatches a post-`style.load` `maplibreum-style-change` event |
| No external stylesheet API for third-party controls | Added `Map.add_external_stylesheet(...)` with URL de-duplication and optional attributes |
| Existing popup helper could not render several properties from vector-tile features | Added `Map.add_feature_popup(...)` with aliases, safe missing values, templated links, and DOMPurify sanitization |
| Repeated, error-prone vector feature hover code | Added `Map.add_feature_state_hover(...)`, including source-layer tracking and reliable previous-state cleanup |
| No page-level structure for dashboard applications | Added `Map.add_page_element(...)` for trusted HTML before or after the map container |
| Large mutable GeoJSON had to be embedded twice for client updates | Generated maps now retain the exact source definitions passed to MapLibre in `map.__maplibreumSourceDefinitions` |
| `PanelControl` embedded HTML inside a JavaScript template literal and inserted it on a timer | Replaced template-literal interpolation with JSON encoding and synchronous insertion after map creation |
| The package imports `requests` at runtime but did not declare it | Added `requests>=2.0` to project dependencies |

## Verification

### Automated tests

- New focused coverage: 20 tests across `tests/test_field_test_api.py` and `tests/test_opensidewalkmap_examples.py`.
- Complete non-browser suite: **316 passed, 1 skipped, 1 browser-marked test deselected** in 36.46 seconds.
- The only warning came from the temporary source-only dependency harness used in the restricted test environment, not from repository code.

### Production-sized generation

All five pages generated successfully against data in the fresh OpenSidewalkMap checkout:

| Output | Size |
|---|---:|
| `main_webmap.html` | 247 KiB |
| `routing.html` | 40 KiB |
| `hazard_analysis.html` | 56 KiB |
| `completeness.html` | 18 MiB |
| `acquisition.html` | 38 KiB |

The 18 MiB completeness output contains its full multi-zoom, 13-timestamp tile history once. Each production page's longest inline script passed `node --check`, and static document parsing found no duplicate IDs.

### Layout and browser constraints

The reference deployments were opened in a cloud browser and their desktop layouts were inspected directly. Routing, hazard, completeness, and acquisition panels matched the source CSS/DOM used by the Python reproductions; the acquisition reference returned all three project rows and the completeness reference exposed all 13 timestamp positions.

A final WebGL canvas comparison of the generated local HTML could not be performed in this environment:

- the local Playwright package had no browser binary, and downloading its matching Chromium build was blocked by the runtime network policy;
- the cloud browser cannot access local files; and
- the cloud browser reports that WebGL2 is unavailable, which also prevents the deployed MapLibre reference canvases from rendering there.

This limitation applies only to GPU/browser rendering validation. Python construction, full-data generation, JavaScript syntax, dependency wiring, DOM contracts, and interaction configuration were verified. A browser with WebGL2 should run the generated pages as the final manual smoke test.

## Residual risks and follow-up

- Routing loads the approximately 13.3 MiB deployed graph at runtime, matching the reference behavior; slow connections will delay profile interaction.
- The completeness page deliberately remains large because it is a standalone historical dataset. A future production optimization could publish the transformed tile history as a separate compressed GeoJSON or binary source.
- OSWM-specific chart and snapshot controls remain externally versioned with the node deployment. Their public module interfaces are loaded by URL so the reproduction stays aligned with the current node.
- No OpenSidewalkMap edit was made.
