# TODO

## Backlog

- [ ] Benchmark marker clustering performance on large (>50k point) datasets and record guidance.
- [ ] Integrate GeoDataFrames -> geopandas will become a major requirement, and the library will mimic this functionality of folium, that makes for better integration with mainstream python geospatial tools;
- [ ] fix and expand the examples

## Completed

- [x] In the official documentation page, create a section with "recreated MapLibre examples" having at the top of each example page the original rendered maplibre example (available at development/maplibre_examples/pages ) and at the bottom the recreated one (development/maplibre_examples/reproduced_pages), and additional info such as a link for that on maplibre's documentation, so the user can check it. (more details at development/maplibre_examples/README.md )

- [x] Add notebook examples showcasing popup templating and floating image overlays.
- [x] Document the MiniMap, measure, and search controls in the README and Sphinx docs.
- [x] MiniMap plugin for overview map
- [x] Measure control to calculate distances and areas
- [x] TimeDimension support for time-enabled layers
- [x] Search control for geocoding and feature lookup
- [x] Optimized marker clustering for large datasets
- [x] Video overlay support
- [x] Terrain, sky, and fog helpers
- [x] Advanced popup class with templating
- [x] Floating image overlays similar to Folium's FloatImage plugin
- [x] Event callbacks for map interactions
- [x] Draggable markers with coordinate updates
- [x] Expression builder and validation utilities
