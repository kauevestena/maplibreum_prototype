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

## Contributing

Contributions are welcome! Please see the [issues page](https://github.com/kauevestena/maplibreum_prototype/issues) to see what needs to be done.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
