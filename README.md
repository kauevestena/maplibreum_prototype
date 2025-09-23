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

# Controls
from maplibreum.controls import MiniMapControl, MeasureControl, SearchControl

# Add a minimap
m.add_control(MiniMapControl())

# Add a measure control
m.add_measure_control()

# Add a search control
# You will need an API key from a geocoding provider like Maptiler.
# https://www.maptiler.com/cloud/keys/
m.add_search_control(SearchControl(provider="maptiler", api_key="YOUR_API_KEY"))

# Enable terrain and atmospheric effects
m.add_dem_source("terrain", "https://example.com/dem.png")
m.set_terrain("terrain")
m.add_sky_layer()
m.set_fog()

# Save the map to an HTML file
m.save("my_map.html")

# Switch to an Albers projection and enable RTL/mobile options
m.set_projection({"name": "albers", "parallels": [29.5, 45.5], "center": [-96, 37.8]})
m.enable_rtl_text_plugin()
m.set_mobile_behavior(cooperative_gestures=True, touch_zoom_rotate=False)
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

## Contributing

Contributions are welcome! Please see the [issues page](https://github.com/kauevestena/maplibreum_prototype/issues) to see what needs to be done.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
