# MapLibre Examples Gallery

This section showcases all the official MapLibre GL JS examples recreated using maplibreum. Each example demonstrates feature parity between the original JavaScript implementation and our Python API.

## About This Gallery

We have successfully recreated **all 123 official MapLibre GL JS examples** using maplibreum. This demonstrates complete feature coverage and validates that maplibreum can handle real-world mapping scenarios.

### How to Use This Gallery

For each example:
- **Original Example**: The reference implementation from [maplibre.org](https://maplibre.org/maplibre-gl-js/docs/examples/)
- **Reproduced Example**: Our Python/maplibreum implementation
- **Test Code**: Link to the Python test that generates the reproduced example

### Coverage Statistics

- **Total Examples**: 123/123 (100%)
- **Implementation Status**: Complete ✓
- **Test Coverage**: All examples have automated pytest tests

## Example Categories

The examples are organized by functionality:

### 3D and Terrain
- [3D Terrain](https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/) - [Test](../tests/test_examples/test_3d_terrain.py)
- [Add a 3D Model to Globe Using Three.js](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-3d-model-to-globe-using-threejs/) - [Test](../tests/test_examples/test_add_a_3d_model_to_globe_using_threejs.py)
- [Add a 3D Model Using Three.js](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-3d-model-using-threejs/) - [Test](../tests/test_examples/test_add_a_3d_model_using_threejs.py)
- [Add a 3D Model with Babylon.js](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-3d-model-with-babylonjs/) - [Test](../tests/test_examples/test_add_a_3d_model_with_babylonjs.py)
- [Add a 3D Model with Shadow Using Three.js](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-3d-model-with-shadow-using-threejs/) - [Test](../tests/test_examples/test_add_a_3d_model_with_shadow_using_threejs.py)
- [Adding 3D Models Using Three.js on Terrain](https://maplibre.org/maplibre-gl-js/docs/examples/adding-3d-models-using-threejs-on-terrain/) - [Test](../tests/test_examples/test_adding_3d_models_using_threejs_on_terrain.py)
- [Display Buildings in 3D](https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/) - [Test](../tests/test_examples/test_display_buildings_in_3d.py)
- [Extrude Polygons for 3D Indoor Mapping](https://maplibre.org/maplibre-gl-js/docs/examples/extrude-polygons-for-3d-indoor-mapping/) - [Test](../tests/test_examples/test_extrude_polygons_for_3d_indoor_mapping.py)

### Markers and Symbols
- [Add a Default Marker](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-default-marker/) - [Test](../tests/test_examples/test_add_a_default_marker.py)
- [Add a Generated Icon to the Map](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-generated-icon-to-the-map/) - [Test](../tests/test_examples/test_add_a_generated_icon_to_the_map.py)
- [Add an Icon to the Map](https://maplibre.org/maplibre-gl-js/docs/examples/add-an-icon-to-the-map/) - [Test](../tests/test_examples/test_add_an_icon_to_the_map.py)
- [Add an Animated Icon to the Map](https://maplibre.org/maplibre-gl-js/docs/examples/add-an-animated-icon-to-the-map/) - [Test](../tests/test_examples/test_add_an_animated_icon_to_the_map.py)
- [Add Custom Icons with Markers](https://maplibre.org/maplibre-gl-js/docs/examples/add-custom-icons-with-markers/) - [Test](../tests/test_examples/test_add_custom_icons_with_markers.py)
- [Animate a Marker](https://maplibre.org/maplibre-gl-js/docs/examples/animate-a-marker/) - [Test](../tests/test_examples/test_animate_a_marker.py)
- [Attach a Popup to a Marker Instance](https://maplibre.org/maplibre-gl-js/docs/examples/attach-a-popup-to-a-marker-instance/) - [Test](../tests/test_examples/test_attach_a_popup_to_a_marker_instance.py)

### Data Sources
- [Add a Canvas Source](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-canvas-source/) - [Test](../tests/test_examples/test_add_a_canvas_source.py)
- [Add a COG Raster Source](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-cog-raster-source/) - [Test](../tests/test_examples/test_add_a_cog_raster_source.py)
- [Add a Raster Tile Source](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-raster-tile-source/) - [Test](../tests/test_examples/test_add_a_raster_tile_source.py)
- [Add a Vector Tile Source](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-vector-tile-source/) - [Test](../tests/test_examples/test_add_a_vector_tile_source.py)
- [Add a WMS Source](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-wms-source/) - [Test](../tests/test_examples/test_add_a_wms_source.py)

### Layers and Styling
- [Add a GeoJSON Line](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-geojson-line/) - [Test](../tests/test_examples/test_add_a_geojson_line.py)
- [Add a GeoJSON Polygon](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-geojson-polygon/) - [Test](../tests/test_examples/test_add_a_geojson_polygon.py)
- [Add a Color Relief Layer](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-color-relief-layer/) - [Test](../tests/test_examples/test_add_a_color_relief_layer.py)
- [Add a Hillshade Layer](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-hillshade-layer/) - [Test](../tests/test_examples/test_add_a_hillshade_layer.py)
- [Add a Multidirectional Hillshade Layer](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-multidirectional-hillshade-layer/) - [Test](../tests/test_examples/test_add_a_multidirectional_hillshade_layer.py)
- [Add a New Layer Below Labels](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-new-layer-below-labels/) - [Test](../tests/test_examples/test_add_a_new_layer_below_labels.py)
- [Add a Pattern to a Polygon](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-pattern-to-a-polygon/) - [Test](../tests/test_examples/test_add_a_pattern_to_a_polygon.py)
- [Add a Stretchable Image to the Map](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-stretchable-image-to-the-map/) - [Test](../tests/test_examples/test_add_a_stretchable_image_to_the_map.py)
- [Add Contour Lines](https://maplibre.org/maplibre-gl-js/docs/examples/add-contour-lines/) - [Test](../tests/test_examples/test_add_contour_lines.py)
- [Add Multiple Geometries from One GeoJSON Source](https://maplibre.org/maplibre-gl-js/docs/examples/add-multiple-geometries-from-one-geojson-source/) - [Test](../tests/test_examples/test_add_multiple_geometries_from_one_geojson_source.py)

### Animation
- [Animate a Line](https://maplibre.org/maplibre-gl-js/docs/examples/animate-a-line/) - [Test](../tests/test_examples/test_animate_a_line.py)
- [Animate a Point](https://maplibre.org/maplibre-gl-js/docs/examples/animate-a-point/) - [Test](../tests/test_examples/test_animate_a_point.py)
- [Animate a Point Along a Route](https://maplibre.org/maplibre-gl-js/docs/examples/animate-a-point-along-a-route/) - [Test](../tests/test_examples/test_animate_a_point_along_a_route.py)
- [Animate a Series of Images](https://maplibre.org/maplibre-gl-js/docs/examples/animate-a-series-of-images/) - [Test](../tests/test_examples/test_animate_a_series_of_images.py)
- [Animate Map Camera Around a Point](https://maplibre.org/maplibre-gl-js/docs/examples/animate-map-camera-around-a-point/) - [Test](../tests/test_examples/test_animate_map_camera_around_a_point.py)
- [Animate Symbol to Follow the Mouse](https://maplibre.org/maplibre-gl-js/docs/examples/animate-symbol-to-follow-the-mouse/) - [Test](../tests/test_examples/test_animate_symbol_to_follow_the_mouse.py)

### Interactive Features
- [Center the Map on a Clicked Symbol](https://maplibre.org/maplibre-gl-js/docs/examples/center-the-map-on-a-clicked-symbol/) - [Test](../tests/test_examples/test_center_the_map_on_a_clicked_symbol.py)
- [Change a Layer's Color with Buttons](https://maplibre.org/maplibre-gl-js/docs/examples/change-a-layers-color-with-buttons/) - [Test](../tests/test_examples/test_change_a_layers_color_with_buttons.py)
- [Create a Draggable Marker](https://maplibre.org/maplibre-gl-js/docs/examples/create-a-draggable-marker/) - [Test](../tests/test_examples/test_create_a_draggable_marker.py)
- [Create a Draggable Point](https://maplibre.org/maplibre-gl-js/docs/examples/create-a-draggable-point/) - [Test](../tests/test_examples/test_create_a_draggable_point.py)

### Real-time Data
- [Add Live Realtime Data](https://maplibre.org/maplibre-gl-js/docs/examples/add-live-realtime-data/) - [Test](../tests/test_examples/test_add_live_realtime_data.py)
- [Update a Feature in Realtime](https://maplibre.org/maplibre-gl-js/docs/examples/update-a-feature-in-realtime/) - [Test](../tests/test_examples/test_update_a_feature_in_realtime.py)

### Video and Media
- [Add a Video](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-video/) - [Test](../tests/test_examples/test_add_a_video.py)

### Custom Layers
- [Add a Custom Layer with Tiles to a Globe](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-custom-layer-with-tiles-to-a-globe/) - [Test](../tests/test_examples/test_add_a_custom_layer_with_tiles_to_a_globe.py)
- [Add a Custom Style Layer](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-custom-style-layer/) - [Test](../tests/test_examples/test_add_a_custom_style_layer.py)

## Viewing Examples Locally

To view the original MapLibre examples:
```bash
# Navigate to the pages directory
cd development/maplibre_examples/pages/
# Open any example in your browser
```

To regenerate the reproduced examples:
```bash
# Run the example tests
pytest tests/test_examples/ -v
# The generated HTML files are in development/maplibre_examples/reproduced_pages/
```

## Full Example List

All 123 examples are fully implemented and tested. For a complete list with implementation status, see the [status.json](../development/maplibre_examples/status.json) file.

## Implementation Notes

### Feature Parity
Each example demonstrates that maplibreum provides complete feature parity with MapLibre GL JS, including:
- All layer types (raster, vector, 3D, etc.)
- Interactive controls and events
- Animation and transitions
- Custom styling and expressions
- Terrain, sky, and fog effects
- Video and canvas sources
- Real-time data updates
- And more!

### Testing Approach
Every example has:
1. An automated pytest test that generates the HTML
2. The test validates the generated configuration
3. Optional browser-based validation using Playwright

### Contributing New Examples
To add new MapLibre examples:
1. Run `python development/maplibre_examples/scrapping.py` to fetch the latest examples
2. Check `status.json` for unimplemented examples
3. Create a corresponding test in `tests/test_examples/`
4. Update `status.json` when complete

## Additional Resources

- [MapLibre GL JS Documentation](https://maplibre.org/maplibre-gl-js/docs/)
- [maplibreum GitHub Repository](https://github.com/kauevestena/maplibreum_prototype)
- [MapLibre Examples Testing Suite README](../development/maplibre_examples/README.md)
