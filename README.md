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

## Quick Start

```python
from maplibreum import Map

# Create a basic map
m = Map(center=[-74.0, 40.7], zoom=12)
m.add_marker(popup="Hello, New York!")
m.save("my_map.html")
```

## Usage Examples

### Basic Maps and Markers

```python
from maplibreum import Map, Marker

# Create a map with custom style and settings
m = Map(
    center=[-23.5505, -46.6333], 
    zoom=10,
    map_style="https://demotiles.maplibre.org/style.json",
    title="São Paulo Map"
)

# Add markers with popups
m.add_marker(popup="São Paulo City Center")
m.add_marker(
    coordinates=[-23.55, -46.63], 
    popup="<h3>Custom Location</h3><p>With HTML content</p>",
    color="red"
)

# Pin a specific MapLibre GL JS version for consistency
m_versioned = Map(maplibre_version="3.6.2")
```

### Data Visualization

```python
# Heatmap from earthquake data
earthquake_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"magnitude": 2.5},
            "geometry": {"type": "Point", "coordinates": [-118.2, 34.0]}
        },
        {
            "type": "Feature", 
            "properties": {"magnitude": 4.1},
            "geometry": {"type": "Point", "coordinates": [-122.4, 37.8]}
        }
    ]
}

m = Map(center=[-120, 36], zoom=6)
m.add_source("earthquakes", {"type": "geojson", "data": earthquake_data})

# Add heatmap with custom styling
m.add_heatmap_layer(
    "earthquake-heat",
    "earthquakes",
    paint={
        "heatmap-weight": ["interpolate", ["linear"], ["get", "magnitude"], 0, 0, 6, 1],
        "heatmap-color": [
            "interpolate", ["linear"], ["heatmap-density"],
            0, "rgba(0,0,255,0)",
            0.5, "rgb(255,255,0)", 
            1, "rgb(255,0,0)"
        ]
    }
)

# Add circle layer for individual points
m.add_circle_layer(
    "earthquake-points", 
    "earthquakes",
    paint={
        "circle-radius": ["*", ["get", "magnitude"], 3],
        "circle-color": "#ff0000",
        "circle-opacity": 0.6
    }
)
```

### Clustering and Aggregation

```python
from maplibreum import ClusteredGeoJson

# Create clustered points
stores_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Store A", "sales": 1000},
            "geometry": {"type": "Point", "coordinates": [-74.0, 40.7]}
        },
        {
            "type": "Feature",
            "properties": {"name": "Store B", "sales": 1500}, 
            "geometry": {"type": "Point", "coordinates": [-74.01, 40.71]}
        }
    ]
}

m = Map(center=[-74.0, 40.7], zoom=10)
clustered = m.add_clustered_geojson(
    stores_data,
    name="stores",
    radius=50,  # cluster radius in pixels
    max_zoom=14  # max zoom for clustering
)

# Customize cluster appearance
for layer in m.layers:
    if layer["id"] == clustered.cluster_layer_id:
        layer["definition"]["paint"]["circle-color"] = [
            "step", ["get", "point_count"],
            "#51bbd6", 100, "#f1f075", 750, "#f28cb1"
        ]
```

### Interactive Controls and Events  

```python
from maplibreum.controls import MiniMapControl, MeasureControl, SearchControl

m = Map(center=[0, 0], zoom=2)

# Add various controls
m.add_control("navigation", "top-left")
m.add_control("scale", "bottom-left", options={"maxWidth": 200, "unit": "metric"})
m.add_control("fullscreen", "top-right")
m.add_control("geolocate", "top-right", options={"trackUserLocation": True})

# Add custom controls
m.add_control(MiniMapControl(toggle=True))
m.add_measure_control()

# Add search control (requires API key)
m.add_search_control(SearchControl(
    provider="maptiler", 
    api_key="YOUR_API_KEY",
    placeholder="Search places..."
))

# Event handling (Jupyter notebooks)
def handle_click(evt):
    coords = evt["lngLat"]
    print(f"Clicked at: {coords['lng']:.4f}, {coords['lat']:.4f}")

m.on_click(handle_click)

# Add popups on layer interactions
m.add_popup(layer_id="points", prop="name", events=["click", "hover"])
```

### 3D Terrain and Atmospheric Effects

```python
# 3D terrain visualization
m = Map(center=[-74.0, 40.7], zoom=12, pitch=60, bearing=45)

# Add terrain elevation
m.add_dem_source("terrain", "https://demotiles.maplibre.org/terrain/{z}/{x}/{y}.png")
m.set_terrain("terrain", exaggeration=1.5)

# Add atmospheric effects
m.add_sky_layer({
    "sky-type": "atmosphere",
    "sky-atmosphere-sun": [0.0, 0.0],
    "sky-atmosphere-sun-intensity": 15
})

m.set_fog({
    "color": "rgb(186, 210, 235)",
    "high-color": "rgb(36, 92, 223)",
    "horizon-blend": 0.02,
    "space-color": "rgb(11, 11, 25)",
    "star-intensity": 0.6
})
```

### Custom Projections and Globe View

```python
# Globe projection
m = Map(center=[0, 0], zoom=1, projection="globe")
m.add_source("countries", {
    "type": "vector", 
    "url": "https://demotiles.maplibre.org/countries.json"
})
m.add_fill_layer("countries-fill", "countries", paint={"fill-color": "#627BC1"})

# Custom Albers projection for US maps
m_us = Map(center=[-96, 37.8], zoom=4)
m_us.set_projection({
    "name": "albers",
    "center": [-96, 23],
    "parallels": [29.5, 45.5]
})

# Lambert conformal conic for regional maps
m_regional = Map(center=[-74.0, 40.7], zoom=8)
m_regional.set_projection({
    "name": "lambertConformalConic",
    "center": [-74.0, 40.7],
    "parallels": [33, 45]
})
```

### Right-to-Left and Mobile Support

```python
# Enable RTL text support
m = Map(center=[35.2, 31.8], zoom=10)  # Jerusalem
m.enable_rtl_text_plugin()

# Configure mobile-friendly behavior
m.set_mobile_behavior(
    cooperative_gestures=True,  # Require two fingers for pan/zoom
    touch_zoom_rotate=False,    # Disable touch rotation
    touch_pitch=False          # Disable touch pitch
)

# Add RTL text labels
m.add_source("places", {"type": "geojson", "data": arabic_places_geojson})
m.add_symbol_layer("place-labels", "places", layout={
    "text-field": ["get", "name_ar"],
    "text-font": ["Noto Sans Arabic Regular"],
    "text-size": 14
})
```

### Animation and Time-based Data

```python
from maplibreum import Map
# from maplibreum import AnimationLoop, TemporalInterval  # Future API

# Time-series data visualization concept
m = Map(center=[-95, 40], zoom=4)

# For now, demonstrate with TimeDimension if available
try:
    from maplibreum import TimeDimension
    
    # Add time dimension control for temporal data
    time_data = [
        {"time": "2023-01-01", "temperature": 5, "coordinates": [-95, 40]},
        {"time": "2023-07-01", "temperature": 25, "coordinates": [-95, 40]}
    ]
    
    # Example of how time-based visualization could work
    time_dimension = TimeDimension(
        times=["2023-01-01", "2023-07-01"],
        current_time="2023-01-01"
    )
    time_dimension.add_to(m)

except ImportError:
    # Simple demonstration with regular markers
    m.add_marker(coordinates=[-95, 40], popup="Winter: 5°C", color="blue")
    m.add_marker(coordinates=[-94, 40], popup="Summer: 25°C", color="red")
```
```

## Advanced Examples

### Choropleth Maps and Statistical Visualization

```python
from maplibreum import Map, Choropleth

# Population density choropleth
m = Map(center=[-96, 37.8], zoom=4)

# US states GeoJSON with population data
states_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "California", "population": 39538223, "density": 253.6},
            "geometry": {...}  # State boundary geometry
        },
        {
            "type": "Feature", 
            "properties": {"name": "Texas", "population": 29145505, "density": 112.8},
            "geometry": {...}  # State boundary geometry
        }
    ]
}

# Create choropleth with custom color scheme
choropleth = Choropleth(
    geo_data=states_data,
    data_property="density",
    key_on="feature.properties.name", 
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Population Density (per sq mi)"
)
choropleth.add_to(m)

# Add custom legend
legend_html = '''
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 150px; height: 90px; 
     background-color: white; border:2px solid grey; z-index:9999; 
     font-size:14px; ">
<h4>Population Density</h4>
<i class="fa fa-square" style="color:#ffffcc"></i> 0-50<br>
<i class="fa fa-square" style="color:#feb24c"></i> 50-200<br>
<i class="fa fa-square" style="color:#f03b20"></i> 200+
</div>
'''
# Note: Legend positioning would be handled by the Choropleth class in practice
```

### Real-time Data and WebSocket Integration

```python
import json
from datetime import datetime

# Real-time vehicle tracking
m = Map(center=[-74.0, 40.7], zoom=12)
m.add_source("vehicles", {"type": "geojson", "data": {"type": "FeatureCollection", "features": []}})

# Vehicle layer with direction arrows
m.add_symbol_layer("vehicle-icons", "vehicles", layout={
    "icon-image": "car",
    "icon-size": 0.8,
    "icon-rotation-alignment": "map",
    "icon-rotate": ["get", "bearing"]
}, paint={
    "icon-opacity": 0.8
})

# Add trails showing vehicle paths
m.add_line_layer("vehicle-trails", "vehicles", paint={
    "line-color": ["get", "color"],
    "line-width": 3,
    "line-opacity": 0.6
})

# JavaScript for WebSocket updates (would be added to template)
websocket_js = '''
const ws = new WebSocket('ws://localhost:8080/vehicles');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    map.getSource('vehicles').setData(data);
};
'''
# Note: Custom JavaScript integration depends on template customization
```

### Multi-layer Data Stories

```python
# Climate change visualization with multiple data layers
m = Map(center=[0, 20], zoom=2, projection="naturalEarth")

# Temperature anomaly layer
m.add_source("temperature", {
    "type": "raster",
    "tiles": ["https://climate-data.org/temperature/{z}/{x}/{y}.png"],
    "tileSize": 256
})
m.add_raster_layer("temperature-layer", "temperature", paint={
    "raster-opacity": 0.7
})

# Sea level rise points
m.add_source("sea-level", {
    "type": "geojson", 
    "data": "https://climate-data.org/sea-level.geojson"
})
m.add_circle_layer("sea-level-points", "sea-level", paint={
    "circle-radius": ["interpolate", ["linear"], ["get", "rise_cm"], 0, 2, 50, 15],
    "circle-color": ["interpolate", ["linear"], ["get", "rise_cm"], 
                     0, "#0080ff", 25, "#ff8000", 50, "#ff0000"],
    "circle-opacity": 0.8
})

# Precipitation contours
m.add_source("precipitation", {
    "type": "vector",
    "url": "https://climate-data.org/precipitation.json"
})
m.add_line_layer("precip-contours", "precipitation", 
                source_layer="contours", paint={
    "line-color": "#0066cc",
    "line-width": ["interpolate", ["linear"], ["get", "level"], 0, 1, 1000, 4]
})

# Add layer control for toggling
from maplibreum.controls import LayerControl
layer_control = LayerControl({
    "Temperature Anomaly": "temperature-layer",
    "Sea Level Rise": "sea-level-points", 
    "Precipitation": "precip-contours"
})
layer_control.add_to(m)
```

### Custom Styling and Expressions

```python
from maplibreum.expressions import interpolate, get, case, literal

# Dynamic restaurant ratings visualization
m = Map(center=[-74.0, 40.7], zoom=13)

restaurants_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Pizza Place", 
                "rating": 4.5, 
                "price": "$$",
                "cuisine": "Italian"
            },
            "geometry": {"type": "Point", "coordinates": [-74.0, 40.7]}
        }
    ]
}

m.add_source("restaurants", {"type": "geojson", "data": restaurants_data})

# Size based on rating, color based on price
m.add_circle_layer("restaurant-circles", "restaurants", paint={
    "circle-radius": interpolate(
        "linear", get("rating"), 
        [1, 3], [3, 8], [5, 15]
    ),
    "circle-color": case(
        ["==", get("price"), "$"], literal("#00ff00"),
        ["==", get("price"), "$$"], literal("#ffaa00"), 
        ["==", get("price"), "$$$"], literal("#ff0000"),
        literal("#666666")  # default
    ),
    "circle-stroke-width": 2,
    "circle-stroke-color": "#ffffff"
})

# Labels with custom fonts
m.add_symbol_layer("restaurant-labels", "restaurants", layout={
    "text-field": ["concat", ["get", "name"], "\n⭐", ["get", "rating"]],
    "text-font": ["Open Sans Bold"],
    "text-size": 12,
    "text-offset": [0, 2],
    "text-anchor": "top"
}, paint={
    "text-color": "#333333",
    "text-halo-color": "#ffffff",
    "text-halo-width": 1
})
```

### Performance Optimization for Large Datasets

```python
# Efficient rendering of millions of points
m = Map(center=[-74.0, 40.7], zoom=10)

# Use clustering for large point datasets
large_dataset = {
    "type": "FeatureCollection", 
    "features": []  # Millions of taxi pickup points
}

# Add with aggressive clustering
clustered = m.add_clustered_geojson(
    large_dataset,
    name="taxi-pickups",
    radius=80,           # Larger cluster radius
    max_zoom=12,         # Cluster up to zoom 12
    cluster_properties={ # Aggregate properties
        "sum_rides": ["+", ["get", "rides"]],
        "avg_fare": ["/", ["get", "total_fare"], ["get", "rides"]]
    }
)

# Use deck.gl integration (conceptual - would require custom implementation)
# This shows the structure for high-performance layer integration
deckgl_config = {
    "type": "ScatterplotLayer",
    "id": "taxi-points",
    "data": "/data/taxi-large.json",
    "getPosition": "coordinates", 
    "getRadius": 20,
    "getFillColor": [255, 140, 0, 160],
    "pickable": True,
    "radiusMinPixels": 2,
    "radiusMaxPixels": 5
}
# Note: Deck.gl integration would require custom template modifications
```

### Integration Patterns

```python
# Flask web application integration
from flask import Flask, render_template_string
from maplibreum import Map

app = Flask(__name__)

@app.route('/map')
def show_map():
    m = Map(center=[-74.0, 40.7], zoom=12)
    m.add_marker(popup="Dynamic marker from Flask!")
    
    # Embed in HTML template
    map_html = m._repr_html_()
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head><title>My Map App</title></head>
    <body>
        <h1>Welcome to My Map</h1>
        {{ map_html|safe }}
    </body>
    </html>
    ''', map_html=map_html)

# Jupyter dashboard with ipywidgets
import ipywidgets as widgets
from IPython.display import display

def create_interactive_map():
    # Control widgets
    center_lat = widgets.FloatSlider(value=40.7, min=-90, max=90, description='Latitude')
    center_lon = widgets.FloatSlider(value=-74.0, min=-180, max=180, description='Longitude') 
    zoom_level = widgets.IntSlider(value=10, min=1, max=20, description='Zoom')
    
    # Map output
    map_output = widgets.Output()
    
    def update_map(*args):
        with map_output:
            map_output.clear_output()
            m = Map(center=[center_lon.value, center_lat.value], zoom=zoom_level.value)
            m.add_marker(popup=f"Center: {center_lat.value:.2f}, {center_lon.value:.2f}")
            display(m)
    
    # Link widgets to update function
    center_lat.observe(update_map, 'value')
    center_lon.observe(update_map, 'value')
    zoom_level.observe(update_map, 'value')
    
    # Initial map
    update_map()
    
    return widgets.VBox([
        widgets.HBox([center_lat, center_lon, zoom_level]),
        map_output
    ])

# Streamlit integration
import streamlit as st

st.title("MapLibreum in Streamlit")

# Sidebar controls
st.sidebar.header("Map Configuration")
lat = st.sidebar.slider("Latitude", -90.0, 90.0, 40.7)
lon = st.sidebar.slider("Longitude", -180.0, 180.0, -74.0)
zoom = st.sidebar.slider("Zoom Level", 1, 20, 10)

# Create and display map
m = Map(center=[lon, lat], zoom=zoom)
m.add_marker(popup=f"Streamlit Map at {lat:.2f}, {lon:.2f}")

# Display using Streamlit's HTML component
st.components.v1.html(m._repr_html_(), height=600)
```

### Export and Deployment

```python
# Static image export for reports
m = Map(center=[-74.0, 40.7], zoom=12)
m.add_marker(popup="Report Location")

# Export to PNG (conceptual - would require additional setup)
# m.export_png("report_map.png", width=800, height=600, dpi=300)

# Export with custom styling for print (conceptual)
# m.set_print_styles({
#     "hide_controls": True,
#     "high_contrast": True, 
#     "remove_attribution": False  
# })

# Save map to file
m.save("report_map.html")

# Batch export multiple views
views = [
    {"center": [-74.0, 40.7], "zoom": 10, "name": "overview"},
    {"center": [-74.01, 40.71], "zoom": 15, "name": "detail"}
]

for view in views:
    m_view = Map(center=view["center"], zoom=view["zoom"])
    m_view.add_marker()
    m_view.save(f"map_{view['name']}.html")

# GitHub Pages deployment with automated builds
m = Map(center=[0, 0], zoom=2)
# m.add_geojson_layer("world", "./data/world-countries.geojson")  # conceptual
m.save("docs/index.html")
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
implemented = sum(1 for v in data.values() if v['task_status'])
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
    if not info['task_status']:
        print(f'Next unimplemented example: {name}')
        print(f'MapLibre URL: {info[\"url\"]}')
        break
"
```

For detailed information about the testing suite, see [misc/maplibre_examples/README.md](misc/maplibre_examples/README.md).

## Contributing

Contributions are welcome! Please see the [issues page](https://github.com/kauevestena/maplibreum_prototype/issues) to see what needs to be done.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
