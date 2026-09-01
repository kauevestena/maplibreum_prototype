# MapLibreum tutorial notebooks

These notebooks form a progressive, story-driven introduction to MapLibreum. Each one produces a useful map rather than a disconnected collection of API calls.

They are designed to be dependable:

- synthetic teaching data is embedded or generated with fixed random seeds;
- no notebook requires an API key;
- maps use OpenFreeMap Liberty by default, providing roads, places, land use, and buildings instead of a sparse demonstration basemap;
- core tutorials do not download mutable datasets at execution time;
- outputs and execution counters are not committed;
- CI executes every code cell and renders every resulting map;
- the gallery deployment stops if a notebook fails instead of publishing a broken page.

## Interactive Notebooks

To explore these examples interactively, you can run them directly within Jupyter Notebook or JupyterLab.

1. **`01_basic_usage.ipynb` — Your first MapLibreum map:** create and export a polished walking tour with markers, popups, a route, automatic bounds, and controls.
2. **`02_layers_and_controls.ipynb` — Data-driven styling:** turn an accessibility audit into a map styled by MapLibre expressions, with tooltips, structured popups, and a legend.
3. **`03_geojson_and_choropleth.ipynb` — Thematic mapping:** combine a choropleth with candidate projects to support an investment decision.
4. **`04_advanced_layers.ipynb` — Terrain and cloud-native tiles:** render pitched 3D terrain and a vector map streamed from a single PMTiles archive.
5. **`05_realtime_and_events.ipynb` — Interaction that survives export:** add filtering, restyling, measurement, popups, and coordinate inspection that work without a Python kernel.
6. **`06_clustering_and_performance.ipynb` — Thousands of points:** generate and cluster 6,000 deterministic observations, then measure the rendered artifact.
7. **`07_pmtiles_world_basemap.ipynb` — One file, the whole planet:** render Protomaps' world PMTiles build with a handful of hand-written style layers.

## Displaying Maps inside Notebooks

Simply create a `Map` instance (e.g., `m = Map(...)`) and evaluate `m` as the last line in a notebook cell. MapLibreum will automatically render the map inside an embedded `<iframe>` using the object's `_repr_html_` implementation.

If you need fine-grained control over the map's dimensions, pass `width` and `height` to `Map`, or call `m.display_in_notebook(width="100%", height="500px")`.

The first three notebooks use embedded teaching data over the public OpenFreeMap Liberty style. OpenFreeMap requires no API key, but its public instance does not provide an availability guarantee; use infrastructure with an appropriate service level for production deployments. Notebooks 4 and 7 intentionally fetch public demonstration terrain and PMTiles data in the browser; replace those endpoints with production infrastructure before deploying a real application.

## Production field tests

- [`opensidewalkmap/`](opensidewalkmap/) contains five standalone Python applications that reproduce the distinct MapLibre maps deployed by the OpenSidewalkMap beta node.
