# MapLibre Examples Testing Suite

This directory contains a comprehensive testing system to validate that `maplibreum` can reproduce all official MapLibre GL JS examples.

## Purpose

The goal is to systematically test `maplibreum`'s capability to reproduce MapLibre's official examples, providing:
- **Automated validation** of feature coverage
- **Regression testing** for new releases
- **Example conversion** from JavaScript to Python
- **Performance benchmarking** against reference implementations

## Quick Start

### 1. Install Dependencies
```bash
pip install requests beautifulsoup4
```

### 2. Fetch Latest Examples
```bash
cd /home/kaue/maplibreum_prototype
python misc/maplibre_examples/scrapping.py
```

### 3. Check Status
```bash
python -c "import json; data = json.load(open('misc/maplibre_examples/status.json')); print(f'Total examples: {len(data)}'); print(f'Downloaded: {sum(1 for v in data.values() if list(v.values())[0][\"source_status\"])}'); print(f'Implemented: {sum(1 for v in data.values() if list(v.values())[0][\"task_status\"])}')"
```

## Directory Structure

```
misc/maplibre_examples/
├── README.md           # This file - agent instructions
├── scrapping.py        # Fetches examples from maplibre.org
├── status.json         # Tracks progress per example
└── pages/             # Downloaded HTML examples
    ├── 3d-terrain.html
    ├── add-a-marker.html
    └── ... (100+ examples)
```

## Agent Workflow

### For Testing Coverage:
1. **Parse `status.json`** to identify untested examples (`task_status: false`)
2. **Analyze HTML files** in `pages/` to extract JavaScript code
3. **Create equivalent Python/maplibreum code** in `tests/test_examples/`
4. **Update `status.json`** when implementation is complete
5. **Run tests** with `pytest tests/test_examples/`

### For Adding New Examples:
1. **Re-run scrapping** to fetch latest examples
2. **Identify new entries** in `status.json`
3. **Follow conversion workflow** above

### For Regression Testing:
1. **Run all example tests**: `pytest tests/test_examples/ -v`
2. **Check failure patterns** in test output
3. **Update maplibreum core** if systematic failures found

## Status Tracking

The `status.json` file tracks each example with:
```json
{
  "example-name": {
    "example-name": {
      "url": "https://maplibre.org/...",
      "source_status": true,    // HTML downloaded
      "file_path": "misc/...",  // Local file path
      "task_status": false      // Python equivalent created
    }
  }
}
```

## Key Commands for Agents

```bash
# Refresh examples from maplibre.org
python misc/maplibre_examples/scrapping.py

# Count implementation progress
python -c "
import json
with open('misc/maplibre_examples/status.json') as f:
    data = json.load(f)
total = len(data)
implemented = sum(1 for v in data.values() if list(v.values())[0]['task_status'])
print(f'Progress: {implemented}/{total} ({implemented/total*100:.1f}%)')
"

# Find next example to implement
python -c "
import json
with open('misc/maplibre_examples/status.json') as f:
    data = json.load(f)
for name, info in data.items():
    if not list(info.values())[0]['task_status']:
        print(f'Next: {name}')
        print(f'URL: {list(info.values())[0][\"url\"]}')
        print(f'File: {list(info.values())[0][\"file_path\"]}')
        break
"

# Run specific example test
pytest tests/test_examples/test_<example_name>.py -v

# Run all example tests
pytest tests/test_examples/ -v
```

## Implementation Guidelines

When converting JavaScript examples to Python:
1. **Extract core MapLibre functionality** from HTML/JS
2. **Map JavaScript API calls** to maplibreum equivalents
3. **Preserve visual/functional behavior** 
4. **Create pytest test case** that validates output
5. **Update `task_status: true`** in status.json
6. **Document any limitations** or differences

## Notes for Agents

- **HTML files contain complete examples** with embedded JavaScript
- **Focus on MapLibre-specific code**, ignore generic HTML/CSS
- **Some examples may require new maplibreum features** - document these
- **Maintain test isolation** - each example should be self-contained
- **Use descriptive test names** matching original example names


## Roadmap

### MapLibre Examples Implementation Progress

This roadmap tracks the systematic implementation of all 123 official MapLibre GL JS examples to ensure comprehensive feature coverage and compatibility. This shall be updated every iteration.

**Current Coverage:** 28/123 examples completed (22.8%).

#### Phase 1: Core Functionality (13/123 completed - 10.6%)

**✅ Completed Examples:**
- `add-a-default-marker` - Basic marker placement
- `display-a-map` - Map initialization and basic configuration
- `display-a-popup` - Static popup functionality
- `display-a-popup-on-click` - Interactive popups with event handling
- `display-map-navigation-controls` - Built-in navigation controls
- `add-a-geojson-line` - GeoJSON LineString layers with styling
- `add-a-geojson-polygon` - GeoJSON polygon rendering and styling
- `add-an-icon-to-the-map` - Custom icon symbol layers
- `add-multiple-geometries-from-one-geojson-source` - Complex GeoJSON datasets
- `create-a-heatmap-layer` - Heatmap visualization for point data
- `create-and-style-clusters` - Marker clustering for performance
- `fit-a-map-to-a-bounding-box` - Viewport and bounds management
- `3d-terrain` - 3D terrain rendering

**🎯 Next Priority Examples (Phase 1 continuation):**
- `display-a-popup-on-hover` - Hover-based popup interactivity
- `display-html-clusters-with-custom-properties` - Rich cluster labelling
- `display-a-non-interactive-map` - Static map rendering patterns
- `draw-a-circle` - Client-side drawing primitives
- `draw-geojson-points` - Styling raw GeoJSON points
- `display-a-remote-svg-symbol` - External asset symbol usage

#### Phase 2: Advanced Styling & Layers (15/123 completed - 12.2%)

**✅ Completed Examples (Milestone reached):**
- `add-a-pattern-to-a-polygon` – Pattern fills via `Map.add_image` and `FillLayer` helpers.
- `add-a-color-relief-layer` – Custom raster-dem color ramp rendered through `ColorReliefLayer`.
- `add-a-hillshade-layer` – Hillshade styling with layout/paint passthrough.
- `add-a-multidirectional-hillshade-layer` – Advanced hillshade paint options (illumination + highlight).
- `add-a-new-layer-below-labels` – Symbol overlays inserted with the `before` parameter.
- `create-a-gradient-line-using-an-expression` – Line metrics and gradient expressions.
- `style-lines-with-a-data-driven-property` – Feature-driven styling using `get` expressions.
- `change-building-color-based-on-zoom-level` – Zoom-interpolated extrusion coloring.
- `visualize-population-density` – Nested `let`/`var` expressions for thematic fills.
- `display-a-globe-with-a-fill-extrusion-layer` – Globe projection with extruded GeoJSON polygons.
- `add-a-vector-tile-source` – External vector source with styled waterways.
- `add-a-raster-tile-source` – Raster tile overlay registered through `RasterLayer`.
- `add-contour-lines` – Combined hillshade, contour, and label layers built through helper wrappers.
- `display-a-remote-svg-symbol` – Remote SVG sprites loaded via `Map.add_image` and symbol layouts.
- `filter-within-a-layer` – Circle-layer filters expressed with helper-managed expression arrays.

**🧭 Dependency Inventory & Priorities**

| Example | Category | Key Dependencies | Helper Alignment |
| --- | --- | --- | --- |
| `add-a-pattern-to-a-polygon` | Pattern fills | Requires runtime image registration | `Map.add_image` + `FillLayer` |
| `visualize-population-density` | Expressions | Nested `let`/`var` and `to-color` expressions | Raw expression lists with layer wrappers |
| `change-building-color-based-on-zoom-level` | Extrusions & expressions | Zoom-driven color/height interpolation | `FillExtrusionLayer` paint passthrough |
| `display-a-globe-with-a-fill-extrusion-layer` | Globe + extrusions | Projection option and extrusion paint | `map_options['projection']` + `FillExtrusionLayer` |
| `create-a-gradient-line-using-an-expression` | Line gradients | `lineMetrics` and `line-gradient` | `LineLayer` layout/paint passthrough |
| `style-lines-with-a-data-driven-property` | Data driven styling | Feature property accessors | `LineLayer` with expression paint |
| `add-a-color-relief-layer` | Raster styling | Color relief paint arrays | `ColorReliefLayer` helper |
| `add-a-hillshade-layer` | Raster hillshade | Shadow/exaggeration tuning | `HillshadeLayer` helper |
| `add-a-multidirectional-hillshade-layer` | Raster hillshade | Illumination direction and highlight colors | `HillshadeLayer` helper |
| `add-a-new-layer-below-labels` | Layer ordering | `before` placement and symbol layout | `SymbolLayer` + `Map.add_layer(before=...)` |
| `add-a-vector-tile-source` | Vector source | External tile registration and line styling | `Map.add_source` + `LineLayer` |
| `add-a-raster-tile-source` | Raster source | Remote raster tiles | `Map.add_source` + `RasterLayer` |
| `add-contour-lines` | Multi-layer styling | Hillshade tiles with contour vectors and label expressions | `HillshadeLayer` + `LineLayer` + `SymbolLayer` |
| `display-a-remote-svg-symbol` | Pattern icons | Remote sprite loading and icon layout overrides | `Map.add_image` + `SymbolLayer` |
| `filter-within-a-layer` | Expressions | Compound property filters on circle paints | `CircleLayer` filter serialization |

**📝 Pending Phase 2 Inventory (prioritized by helper readiness):**

| Example | Category | Key Dependencies | Helper Alignment | Priority |
| --- | --- | --- | --- | --- |
| `draw-a-circle` | Expressions & drawing | GeoJSON circle generation and circle layer styling | Supported via GeoJSON sources + `CircleLayer` | High |
| `fit-to-the-bounds-of-a-linestring` | Camera & multi-layer | Automatic extent fitting for line sources | `Map.fit_bounds` + line helpers | High |
| `display-line-that-crosses-180th-meridian` | Multi-layer styling | Wrapping-aware line rendering & map world copies | `LineLayer` + `map_options['renderWorldCopies']` | High |
| `create-a-heatmap-layer-on-a-globe-with-terrain-elevation` | Multi-layer & terrain | Heatmap paint plus globe projection & terrain exaggeration | `Map.add_heatmap_layer`, `set_terrain`, globe projection options | High |
| `change-a-layers-color-with-buttons` | Expressions & UI | DOM events updating paint properties | Filters/paints supported; needs UI wiring via `extra_js` | Medium |
| `filter-layer-symbols-using-global-state` | Expressions | Feature filters toggled from Python state | Filter serialization ready; requires shared state helpers | Medium |
| `filter-symbols-by-text-input` | Expressions & UI | Text input driving symbol layer filters | Filter helpers available; needs input binding | Medium |
| `center-the-map-on-a-clicked-symbol` | Interactivity | Symbol click events triggering camera transitions | Map event API exists; requires scripted callbacks | Medium |
| `animate-a-line` | Animation | Timed updates to line source data | Data updates possible via callbacks; needs animation loop glue | Medium |
| `animate-symbol-to-follow-the-mouse` | Animation & events | Pointer tracking and dynamic symbol placement | Event hooks exist; requires continuous update bridge | Medium |
| `add-a-custom-layer-with-tiles-to-a-globe` | Custom layers | WebGL custom layer registration on globe projection | Custom layer hooks missing | Low |
| `add-a-custom-style-layer` | Custom layers | Raw WebGL style layer integration | Custom layer hooks missing | Low |
| `add-a-simple-custom-layer-on-a-globe` | Custom layers | Custom render loop on globe context | Custom layer hooks missing | Low |
| `create-deckgl-layer-using-rest-api` | Custom layers | Deck.GL interop and REST-driven styling | Requires Deck.GL adapter | Low |
| `toggle-deckgl-layer` | Custom layers | Runtime Deck.GL layer management | Requires Deck.GL adapter | Low |

These additions push Phase 2 beyond the 20% coverage milestone, validating multi-layer contour styling, remote sprite usage, and compound filter expressions through automated pytest scenarios.

#### Phase 3: Interactivity & Events (Target: 35% coverage)

**Planned Examples:**
- Mouse events (hover, click, move)
- Feature selection and highlighting
- Custom popup templates
- Dynamic layer toggling
- User interaction controls

#### Phase 4: Advanced Features (Target: 50% coverage)

**Planned Examples:**
- 3D terrain and elevation
- Globe projection
- Animation and transitions
- Time-based data visualization
- Custom layer implementations

#### Phase 5: Specialized Features (Target: 70% coverage)

**Planned Examples:**
- Vector tile sources
- Raster layers and overlays
- External data integration
- Performance optimization techniques
- Accessibility features

#### Phase 6: Edge Cases & Completeness (Target: 100% coverage)

**Planned Examples:**
- Complex coordinate systems
- Right-to-left text support
- Mobile-specific optimizations
- Browser compatibility features
- Advanced customization options

### Implementation Guidelines

**Priority Criteria:**
1. **Foundation First**: Core mapping functionality (markers, popups, basic layers)
2. **User Impact**: Features most commonly used by developers
3. **API Coverage**: Ensuring all major MapLibreum APIs are validated
4. **Complexity Gradual**: Simple examples before complex integrations

**Development Process:**
1. Select example from next priority list
2. Analyze original MapLibre JavaScript implementation
3. Create equivalent maplibreum Python test
4. Identify any missing API features in maplibreum
5. Implement necessary API extensions (if needed)
6. Validate with comprehensive test coverage
7. Update status.json and documentation
8. Commit progress and move to next example

**Success Metrics:**
- ✅ All tests pass without modification to core maplibreum functionality
- ✅ Generated HTML closely matches MapLibre example behavior
- ✅ Test demonstrates practical usage patterns
- ✅ Documentation includes clear JavaScript-to-Python conversion notes

### Contributing to the Roadmap

Community contributions are welcome! To contribute:

1. Check the current status: `python -c "import json; ..."`
2. Pick an unimplemented example from the next priority list
3. Follow the implementation guidelines above
4. Submit a pull request with your implementation
5. Update this roadmap with progress

The systematic approach ensures that maplibreum achieves comprehensive compatibility with MapLibre GL JS while maintaining code quality and usability for Python developers.


#### Current Status

**MapLibreum Feature Coverage: 6/123 (4.9%)**

The following MapLibre GL JS examples have been successfully implemented and tested:

- ✅ **add-a-default-marker** - Basic marker placement functionality
- ✅ **display-a-map** - Simple map initialization with custom styles
- ✅ **display-a-popup** - Static popup creation with custom HTML content
- ✅ **add-a-geojson-line** - GeoJSON LineString rendering with custom styling
- ✅ **add-an-icon-to-the-map** - Custom icon symbol layers with property expressions
- ✅ **display-a-popup-on-click** - Interactive popups with GeoJSON feature properties