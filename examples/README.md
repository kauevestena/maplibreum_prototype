# MapLibreum Examples

This directory contains Jupyter Notebooks that showcase the features and capabilities of MapLibreum, grouped by theme.

These notebooks replace older, brittle examples with updated code that demonstrates how to use the latest Python API methods, avoiding raw JavaScript injection wherever possible.

## Interactive Notebooks

To explore these examples interactively, you can run them directly within Jupyter Notebook or JupyterLab.

1. **`01_basic_usage.ipynb`**: Learn how to initialize maps, set the initial view, add simple markers, popups, and draw basic vector geometry (lines, polygons, circles).
2. **`02_layers_and_controls.ipynb`**: Explore how to use different raster and vector tiles, integrate WMS layers, and add interactive controls like navigation, fullscreen, geolocation, scale bars, and geocoding.
3. **`03_geojson_and_choropleth.ipynb`**: See how to load external GeoJSON datasets (local files or URLs), apply dynamic styling, add interactive tooltips based on properties, and create choropleth maps to visualize data distributions.
4. **`04_advanced_layers.ipynb`**: Discover advanced rendering features including 3D terrain visualization, PMTiles (Cloud-Optimized Vector Tiles), Deck.GL integrations for massive dataset visualization, and rendering glTF 3D models using Three.js.
5. **`05_realtime_and_events.ipynb`**: Understand how to stream real-time data onto your map, animate camera movements natively, and configure popups or custom event handling.
6. **`06_clustering_and_performance.ipynb`**: Learn how to efficiently handle large datasets (10k-50k+ points) by using WebGL-accelerated marker clustering.

## Displaying Maps inside Notebooks

Simply create a `Map` instance (e.g., `m = Map(...)`) and evaluate `m` as the last line in a notebook cell. MapLibreum will automatically render the map inside an embedded `<iframe>` using the object's `_repr_html_` implementation.

If you need fine-grained control over the map's dimensions, you can call `m.display_in_notebook(width="100%", height="500px")`.
