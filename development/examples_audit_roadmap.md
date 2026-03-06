# Jupyter Notebook Examples Audit & Fixing Roadmap

This document outlines the step-by-step roadmap for fixing and updating the Jupyter Notebook examples located in the `examples/` directory.

These notebooks currently contain outdated code, broken links, or use deprecated patterns (like raw JavaScript injection) that need to be updated to rely strictly on the native Python API and modern, functional endpoints.

## 1. `examples/01_basic_usage.ipynb`
- [x] **1.1 Review and Validate:** This notebook generally looks solid as it mainly focuses on basic Map, Marker, Popup, and Vector shapes. Verify that the shapes correctly render on the map.
- [x] **1.2 Clean up unused imports:** Ensure all imports in the notebook cells are actually used.

## 2. `examples/02_layers_and_controls.ipynb`
- [x] **2.1 Replace Stamen Terrain Source:** Stamen tiles (`https://stamen-tiles.a.ssl.fastly.net/...`) are no longer functional/free to use in the same manner. Replace this `RasterSource` implementation with a working alternative, such as Stadia Maps (which took over Stamen tiles but requires an API key, so maybe an open alternative like OpenStreetMap or another public raster map tile source is better). Update the source and attribution accordingly.
- [x] **2.2 Refactor `GeocodingControl`:** The `GeocodingControl` section injects raw JavaScript and CSS:
    ```python
    m5.add_external_script('https://unpkg.com/@maplibre/maplibre-gl-geocoder@1.5.0/dist/maplibre-gl-geocoder.min.js')
    m5.custom_css += "@import url('https://unpkg.com/@maplibre/maplibre-gl-geocoder@1.5.0/dist/maplibre-gl-geocoder.css');"
    ```
    This needs to be replaced. Update `GeocodingControl` in MapLibreum's core to handle its own dependencies natively, or use the native Python API wrapper if it already exists, avoiding `add_external_script` and manual `custom_css` injection.

## 3. `examples/03_geojson_and_choropleth.ipynb`
- [x] **3.1 Update Folium Data URL:** The notebook relies on `https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/US_Unemployment_Oct2012.csv`. Verify this link is still active and stable, or consider hosting a small dummy dataset natively in the repo to prevent external dependency breakage.
- [x] **3.2 Validate Choropleth Rendering:** Ensure the `Choropleth` class correctly parses the dictionary and matches it against the GeoJSON properties without throwing JS errors.

## 4. `examples/04_advanced_layers.ipynb`
- [x] **4.1 Fix S3 Terrain URL:** The notebook uses `s3://elevation-tiles-prod/terrarium/`. S3 protocols are not natively supported by browsers without a protocol wrapper. Update the URL to use a standard `https` endpoint (e.g., `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`).
- [x] **4.2 Verify 3D Model URL:** The `ThreeJSLayer` example uses `https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Box/glTF-Binary/Box.glb`. Verify this model still exists at this URL, as Khronos frequently reorganizes its sample repos.
- [x] **4.3 Validate Protomaps PMTiles URL:** Ensure the Protomaps sample URL (`https://r2-public.protomaps.com/protomaps-sample-datasets/cb_2018_us_zcta510_500k.pmtiles`) is still active and functional.

## 5. `examples/05_realtime_and_events.ipynb`
- [ ] **5.1 Replace Wanderdrone API:** The `RealTimeDataSource` uses `https://wanderdrone.appspot.com/`, which is notoriously unstable and often returns 502 Bad Gateway. Create a local mock API using a simple Python server, or use a more stable public endpoint (like an ISS tracker API) for real-time coordinates.
- [ ] **5.2 Validate USGS Earthquakes API:** Ensure the USGS GeoJSON feed (`https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson`) is correctly rendering with the dynamic `style_quake` styling function.

## 6. `examples/06_clustering_and_performance.ipynb`
- [ ] **6.1 Verify Vega Datasets URL:** Ensure `https://raw.githubusercontent.com/vega/vega-datasets/master/data/us-state-capitals.json` correctly loads and clusters.
- [ ] **6.2 General Review:** The clustering implementation appears standard, but ensure the `clusterMaxZoom` and `clusterRadius` properties are still functioning correctly in the latest MapLibre GL JS version used by MapLibreum.

## General Tasks
- [ ] **7.1 Run all Notebooks:** After making the above changes, re-run all notebooks using `jupyter nbconvert --to notebook --execute` (or manually) to ensure no Python exceptions are thrown and the outputs are generated correctly.
- [ ] **7.2 Visual Inspection:** Manually inspect the HTML outputs of the Jupyter Notebooks to confirm the visual representation exactly matches the intended behavior (e.g., 3D terrain actually shows as 3D, choropleth colors correctly, etc.).
