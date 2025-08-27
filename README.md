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

# Layer controls
LayerControl().add_to(m)
```

## Example Notebooks

```bash
jupyter notebook examples
```

## Contributing

Contributions are welcome! Please see the [issues page](https://github.com/kauevestena/maplibreum_prototype/issues) to see what needs to be done.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
