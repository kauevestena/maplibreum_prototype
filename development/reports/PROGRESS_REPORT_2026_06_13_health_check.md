# Progress Report - 2026-06-13

## Goal
Check general code health and evaluate if the goals of the project are being attended, particularly regarding achieving Python API parity for MapLibre examples and reducing raw JS injection.

## Project Standing
- **MapLibreum Feature Coverage**: 120/133 (90.2%) examples implemented (based on `development/maplibre_examples/status.json`).
- Many examples were previously relying on `add_on_load_js` or `add_external_script`. A significant effort was undertaken to rewrite these examples using native Python wrappers (e.g. `ThreeJSLayer`, `DeckGLLayer`, `PMTilesProtocol`, `SidebarControl`, `Map.add_hover_effect`, and camera functions).

## JavaScript Injection Refactoring
During this session, we actively refactored the following test examples to eliminate manual JS injections:
- `test_create_a_hover_effect.py` (added `add_hover_effect` to `Map` class)
- `test_create_deckgl_layer_using_rest_api.py` (replaced with `DeckGLLayer`)
- `test_adding_3d_models_using_threejs_on_terrain.py` (replaced with `ThreeJSLayer`)
- `test_offset_the_vanishing_point_using_padding.py` (replaced with `SidebarControl`)
- `test_pmtiles_source_and_protocol.py` (replaced with `PMTilesProtocol` and `PMTilesSource`)
- `test_add_a_3d_model_to_globe_using_threejs.py`
- `test_add_a_3d_model_using_threejs.py`
- `test_animate_map_camera_around_a_point.py`
- `test_add_a_custom_layer_with_tiles_to_a_globe.py`
- `test_sync_movement_of_multiple_maps.py`
- `test_add_a_video.py`
- `test_fly_to_a_location.py`
- `test_slowly_fly_to_a_location.py`
- `test_zoom_and_planet_size_relation_on_globe.py`
- `test_customize_camera_animations.py`
- `test_jump_to_a_series_of_locations.py`
- `test_navigate_the_map_with_game_like_controls.py`
- `test_fit_to_the_bounds_of_a_linestring.py`
- `test_get_features_under_the_mouse_pointer.py`
- `test_get_coordinates_of_the_mouse_pointer.py`
- `test_animate_a_point_along_a_route.py`
- `test_filter_layer_symbols_using_global_state.py`
- `test_measure_distances.py`

*All refactored tests pass successfully.*

## Structural / Architectural Review
A review of the Python codebase (primarily `maplibreum/core.py` and module boundaries) revealed several structural/architectural issues:

1. **God Object Anti-Pattern:** The `Map` class in `maplibreum/core.py` is extremely large (over 3400 lines of code) and acts as a "God Object." It handles initialization, state management (layers, sources, controls), event binding, rendering, and specific feature integrations (e.g., specific camera animations, hover effects, protocols).
2. **Missing Component Abstractions:** Too much JS logic is tightly coupled into Python classes instead of utilizing cleaner template inheritance or separating the component logic from the layout generation.
3. **State Management:** Class-level attributes like `_drawn_data`, `_event_callbacks`, `_marker_registry`, and `_search_data` are defined on the `Map` class. This could lead to shared state issues across different `Map` instances or cause memory leaks if instances are created frequently in an environment like a Jupyter notebook. These should likely be instance-level variables instead.
4. **Scattered Feature Implementations:** There are specific layer integrations like DeckGL and ThreeJS that are good steps forward, but the core engine still heavily relies on string manipulations and textwrap dedent for injecting JavaScript into the templates. As the project pushes towards 100% Python API parity, an Abstract Syntax Tree (AST) approach for JS generation or a more structured component-based rendering pipeline would be more maintainable.

## Conclusion
The project is making excellent progress towards its goal of full Python API parity for MapLibre capabilities. The active cleanup of JS injections in the test suite reflects a solid step toward a mature library. Future structural refactoring of the `Map` class and component separation will greatly improve long-term code health.
