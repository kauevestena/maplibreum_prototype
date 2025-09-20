# MapLibreum

A Python library for creating interactive MapLibre maps, like Folium but for MapLibre.

## Installation

```bash
pip install maplibreum
```

## Development

```bash
pip install -e .
pytest
```

## Usage

```python
from maplibreum import Map

# Create a map centered at a specific location
m = Map(center=[-23.5505, -46.6333], zoom=10)

# Pin a specific MapLibre GL JS version (defaults to 3.4.0)
m_custom = Map(maplibre_version="2.4.0")

# Add a marker at the map center
m.add_marker(popup="Hello, MapLibre!")

# Or specify coordinates for the marker
m.add_marker(coordinates=[-23.55, -46.63], popup="Another marker")

# Add a heatmap layer from GeoJSON points
geojson = {"type": "FeatureCollection", "features": []}
source = {"type": "geojson", "data": geojson}
m.add_heatmap_layer("heat", source)

# Register event callbacks (Jupyter notebooks)
def handle_click(evt):
    print("Clicked at", evt["lngLat"])
m.on_click(handle_click)

# Enable built-in controls
m.add_control("geolocate", "top-right", options={"trackUserLocation": True})
m.add_control(
    "attribution", "bottom-right", options={"customAttribution": "My Data"}
)

# Enable terrain and atmospheric effects
m.add_dem_source("terrain", "https://example.com/dem.png")
m.set_terrain("terrain")
m.add_sky_layer()
m.set_fog()

# Save the map to an HTML file
m.save("my_map.html")
```

## Feature Demonstrations

```python
from maplibreum import (
    Map,
    Choropleth,
    Marker,
    MarkerCluster,
    LayerControl,
)

m = Map()

# Choropleth
Choropleth(geojson_data).add_to(m)

# Marker clusters
cluster = MarkerCluster().add_to(m)
Marker(coordinates=[0, 0]).add_to(cluster)

# Clustered GeoJSON
m.add_clustered_geojson(geojson_data)

# Layer controls
LayerControl().add_to(m)
```

## Expressions

MapLibre uses array-based expressions for data-driven styling. The
``maplibreum.expressions`` module provides helpers to construct and
validate these expressions:

```python
from maplibreum.expressions import get, interpolate, var

color = interpolate(
    "linear",
    var("heatmap-density"),
    [(0, "blue"), (1, "red")],
)
```

## Example Notebooks

```bash
jupyter notebook examples
```

### Live Examples Gallery

View interactive examples deployed to GitHub Pages: [MapLibreum Examples Gallery](https://kauevestena.github.io/maplibreum_prototype/)

The examples gallery is automatically generated from Jupyter notebooks in the `examples/` folder and showcases:
- Creative MapLibreum examples and tutorials
- Basic usage patterns
- New features demonstrations  
- Event handling and interactions

To deploy examples to GitHub Pages, see [GitHub Pages Documentation](docs/GITHUB_PAGES.md).

## Changelog

See the [CHANGELOG](CHANGELOG.md) for a detailed list of updates in each release.

## Testing MapLibreum Functionality

### Basic Testing

Run the core test suite to verify MapLibreum's basic functionality:

```bash
# Install development dependencies
pip install -e .
pip install pytest jupyter

# Run all basic tests
pytest tests/ -v
```

### Advanced Testing: MapLibre Examples Validation

To verify that MapLibreum is working properly and to check feature coverage against MapLibre GL JS, use the comprehensive testing suite in `misc/maplibre_examples/`:

#### MapLibre Examples Testing Suite

The `misc/maplibre_examples/` directory contains a systematic testing system that validates MapLibreum's capability to reproduce all official MapLibre GL JS examples. This provides:

- **Automated validation** of feature coverage  
- **Regression testing** for new releases
- **Example conversion** from JavaScript to Python
- **Performance benchmarking** against reference implementations

#### Current Status

**MapLibreum Feature Coverage: 6/123 (4.9%)**

The following MapLibre GL JS examples have been successfully implemented and tested:

- ✅ **add-a-default-marker** - Basic marker placement functionality
- ✅ **display-a-map** - Simple map initialization with custom styles
- ✅ **display-a-popup** - Static popup creation with custom HTML content
- ✅ **add-a-geojson-line** - GeoJSON LineString rendering with custom styling
- ✅ **add-an-icon-to-the-map** - Custom icon symbol layers with property expressions
- ✅ **display-a-popup-on-click** - Interactive popups with GeoJSON feature properties

#### Quick Status Check

```bash
# Install dependencies for the testing suite
pip install requests beautifulsoup4

# Check current implementation progress
python -c "
import json
with open('misc/maplibre_examples/status.json') as f:
    data = json.load(f)
total = len(data)
implemented = sum(1 for v in data.values() if list(v.values())[0]['task_status'])
print(f'MapLibreum Feature Coverage: {implemented}/{total} ({implemented/total*100:.1f}%)')
print(f'Total MapLibre examples available: {total}')
print(f'Examples successfully implemented: {implemented}')
"
```

#### Running Example Tests

```bash
# Run all implemented example tests (when available)
pytest tests/test_examples/ -v

# Refresh examples from MapLibre.org (optional)
python misc/maplibre_examples/scrapping.py

# Find next example to implement
python -c "
import json
with open('misc/maplibre_examples/status.json') as f:
    data = json.load(f)
for name, info in data.items():
    if not list(info.values())[0]['task_status']:
        print(f'Next unimplemented example: {name}')
        print(f'MapLibre URL: {list(info.values())[0][\"url\"]}')
        break
"
```

For detailed information about the testing suite, see [misc/maplibre_examples/README.md](misc/maplibre_examples/README.md).

## Roadmap

### MapLibre Examples Implementation Progress

This roadmap tracks the systematic implementation of all 123 official MapLibre GL JS examples to ensure comprehensive feature coverage and compatibility.

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

## Contributing

Contributions are welcome! Please see the [issues page](https://github.com/kauevestena/maplibreum_prototype/issues) to see what needs to be done.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
