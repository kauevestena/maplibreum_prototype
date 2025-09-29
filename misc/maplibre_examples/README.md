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
python -c "import json; data = json.load(open('misc/maplibre_examples/status.json')); print(f'Total examples: {len(data)}'); print(f'Downloaded: {sum(1 for v in data.values() if v[\"source_status\"])}'); print(f'Implemented: {sum(1 for v in data.values() if v[\"task_status\"])}')"
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

## Browser Verification (Manual)

The core pytest suite only validates the generated HTML configuration. When you
need to confirm that MapLibre GL initialises correctly in a real browser:

1. **Install the optional tooling** (within your virtual environment):
   ```bash
   pip install pytest-playwright playwright
   playwright install chromium
   ```
2. **Regenerate the HTML artefacts** by running the automated examples suite:
   ```bash
   pytest tests/test_examples -q
   ```
   This recreates the files in `misc/maplibre_examples/reproduced_pages/`.
3. **Launch the browser checks** whenever you want an end-to-end sanity test:
   ```bash
   pytest playwright_tests --browser chromium -m browser
   ```

These Playwright-powered tests live outside the default `pytest` discovery
path, so CI remains lightweight while you can still perform manual parity
checks on demand.

## Status Tracking

The `status.json` file tracks each example with:
```json
{
  "example-name": {
    "url": "https://maplibre.org/...",
    "source_status": true,    // HTML downloaded
    "file_path": "misc/...",  // Local file path
    "task_status": false,     // Python equivalent created
    "script": "tests/..."     // Path to test file (null if not implemented)
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
implemented = sum(1 for v in data.values() if v['task_status'])
print(f'Progress: {implemented}/{total} ({implemented/total*100:.1f}%)')
"

# Find next example to implement
python -c "
import json
with open('misc/maplibre_examples/status.json') as f:
    data = json.load(f)
for name, info in data.items():
    if not info['task_status']:
        print(f'Next: {name}')
        print(f'URL: {info[\"url\"]}')
        print(f'File: {info[\"file_path\"]}')
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

### Coverage Summary

**Current Coverage:** 123/123 examples completed

- ✅ Ported `add-a-3d-model-to-globe-using-threejs` leveraging the new
  `Map.add_external_script` helper to load three.js dependencies and attach a
  custom layer via `add_on_load_js`.
- ✅ Implemented `display-buildings-in-3d` by dynamically inserting a `fill-extrusion` layer before the first symbol layer, ensuring labels render correctly on top of 3D buildings.
- ✅ Added `extrude-polygons-for-3d-indoor-mapping` to showcase 3D indoor mapping using the `fill-extrusion-height` paint property.
- ✅ Implemented `set-center-point-above-ground` by adding `elevation` and `centerClampedToGround` properties to the `Map` constructor, allowing for camera positioning relative to the terrain.
- ✅ Added `variable-label-placement` to demonstrate dynamic label repositioning using the `text-variable-anchor` and `text-radial-offset` layout properties, preventing label overlap during map interactions.
- ✅ Implemented `zoom-and-planet-size-relation-on-globe` to show how to compensate for the globe's enlargement near the poles when animating camera movements.

### Edge-case Validation

- ✅ **Right-to-left script support** – Exercised via `Map.enable_rtl_text_plugin`, matching the `add-support-for-right-to-left-scripts` gallery example with automated pytest coverage.
- ✅ **Mobile gesture flags** – `Map.set_mobile_behavior` mirrors the `cooperative-gestures` example, keeping `cooperativeGestures`, `touchZoomRotate`, and related constructor flags serialised into the output HTML.
- ✅ **Projection specialisation** – Custom projections such as Albers and globe views are serialised through `Map.set_projection` / `map_options`, with regression tests guarding the emitted configuration.

### Outstanding Engine Follow-ups

While the gallery coverage is exhaustive, a few MapLibre capabilities still require deeper engine work:

- **Custom WebGL style layers** – Proposed follow-up issue: "Expose custom WebGL layer hooks" to surface the `CustomLayerInterface` inside MapLibreum.
- **Deck.GL interoperability** – Proposed follow-up issue: "Provide a Deck.GL adapter" enabling deck layers to register through the Python API.
- **pmtiles:// protocol shimming** – Proposed follow-up issue: "Implement PMTiles protocol bridge" adding the front-end fetch interceptor required by MapLibre's pmtiles example.

### Maintenance Workflow

1. Re-run `python misc/maplibre_examples/scrapping.py` whenever the upstream gallery changes.
2. Re-generate progress stats with the helper snippets in this directory to confirm the 123/123 milestone.
3. Add pytest regressions for any new behaviours (e.g. gesture flags, plugin injection, projection tweaks) before flipping `task_status` to `true`.
4. Update this roadmap with milestone notes and keep the celebration banner alive for future iterations.

### Celebrating the Milestone

We're tracking towards the **123/123 coverage** milestone—complete feature
parity with the official MapLibre GL JS gallery while preserving a templated,
reproducible HTML/JS pipeline. Current parity stands at **123/123** with the
three.js globe example now automated.
