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

#### Phase 1: Core Functionality (6/123 completed - 4.9%)

**✅ Completed Examples:**
- `add-a-default-marker` - Basic marker placement
- `display-a-map` - Map initialization and basic configuration
- `display-a-popup` - Static popup functionality
- `add-a-geojson-line` - GeoJSON LineString layers with styling
- `add-an-icon-to-the-map` - Custom icon symbol layers
- `display-a-popup-on-click` - Interactive popups with event handling

**🎯 Next Priority Examples (Phase 1 continuation):**
- `add-a-geojson-polygon` - GeoJSON polygon rendering and styling
- `display-map-navigation-controls` - Built-in navigation controls
- `create-a-heatmap-layer` - Heatmap visualization for point data
- `create-and-style-clusters` - Marker clustering for performance
- `fit-a-map-to-a-bounding-box` - Viewport and bounds management
- `add-multiple-geometries-from-one-geojson-source` - Complex GeoJSON datasets

#### Phase 2: Advanced Styling & Layers (Target: 20% coverage)

**Planned Examples:**
- Polygon styling and patterns
- Multiple layer types (fill, line, circle, heatmap)
- Data-driven styling expressions
- Layer filtering and querying
- Custom style specifications

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