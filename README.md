# MapLibreum

A Python library for creating interactive MapLibre maps, like Folium but for MapLibre.

## Installation

```bash
pip install maplibreum
```

## Usage

```python
from maplibreum import Map

# Create a map centered at a specific location
m = Map(center=[-23.5505, -46.6333], zoom=10)

# Add a marker at the map center
m.add_marker(popup="Hello, MapLibre!")

# Or specify coordinates for the marker
m.add_marker(coordinates=[-23.55, -46.63], popup="Another marker")

# Add a heatmap layer from GeoJSON points
geojson = {"type": "FeatureCollection", "features": []}
source = {"type": "geojson", "data": geojson}
m.add_heatmap_layer("heat", source)

# Add a 3D fill-extrusion layer
buildings = {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}}
m.add_fill_extrusion_layer("buildings", buildings)

# Save the map to an HTML file
m.save("my_map.html")
```

## Contributing

Contributions are welcome! Please see the [issues page](https://github.com/kauevestena/maplibreum_prototype/issues) to see what needs to be done.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.