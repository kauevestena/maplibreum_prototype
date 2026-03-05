# March 2026 Roadmap: Achieving True Python API Parity

This roadmap, that is based upon development/maplibre_examples/README.md outlines the steps required to achieve 100% Python API parity in MapLibreum and align our testing suite with the upstream MapLibre examples.

## Phase 1: Reconcile Examples

The goal of this phase is to align our generated examples with the upstream MapLibre examples.

- [x] Map existing test outputs exactly to upstream file names.
- [x] Implement the remaining missing MapLibre examples (e.g., `3d-terrain.html`, `add-a-custom-style-layer.html`).
- [x] Clean up custom test outputs that don't belong in `reproduced_pages/` (e.g., `change-a-maps-language-with-python-api.html`, `create-a-basic-circle-layer.html`).

## Phase 2: Fix Tracking

The goal of this phase is to fix the reporting and tracking metrics.

- [ ] Repair the `status.json` tracking system to accurately reflect `task_status: true` for implemented examples, ensuring the command-line metrics are correct.

## Phase 3: True Python API Parity

The goal of this phase is to eliminate the use of raw JavaScript injection (`add_on_load_js`, `add_external_script`) in all example test scripts, replacing them with proper native Python wrappers and engine improvements (e.g., proper WebGL layer hooks, custom UI control implementations).

- [ ] `tests/test_examples/test_create_a_time_slider.py`
- [ ] `tests/test_examples/test_change_a_layers_color_with_buttons.py`
- [ ] `tests/test_examples/test_add_live_realtime_data.py`
- [ ] `tests/test_examples/test_update_a_feature_in_realtime.py`
- [ ] `tests/test_examples/test_add_an_animated_icon_to_the_map.py`
- [ ] `tests/test_examples/test_filter_symbols_by_text_input.py`
- [ ] `tests/test_examples/test_view_local_geojson.py`
- [ ] `tests/test_examples/test_disable_map_rotation.py`
- [ ] `tests/test_examples/test_animate_map_camera_around_a_point.py`
- [ ] `tests/test_examples/test_add_a_custom_layer_with_tiles_to_a_globe.py`
- [ ] `tests/test_examples/test_add_a_3d_model_using_threejs.py`
- [ ] `tests/test_examples/test_update_a_feature_in_realtime_with_python_api.py`
- [ ] `tests/test_examples/test_pmtiles_source_and_protocol.py`
- [ ] `tests/test_examples/test_sync_movement_of_multiple_maps.py`
- [ ] `tests/test_examples/test_add_a_video.py`
- [ ] `tests/test_examples/test_create_a_hover_effect.py`
- [ ] `tests/test_examples/test_fly_to_a_location.py`
- [ ] `tests/test_examples/test_zoom_and_planet_size_relation_on_globe.py`
- [ ] `tests/test_examples/test_create_deckgl_layer_using_rest_api.py`
- [ ] `tests/test_examples/test_fit_to_the_bounds_of_a_linestring.py`
- [ ] `tests/test_examples/test_geocode_with_nominatim.py`
- [ ] `tests/test_examples/test_get_features_under_the_mouse_pointer.py`
- [ ] `tests/test_examples/test_adding_3d_models_using_threejs_on_terrain.py`
- [ ] `tests/test_examples/test_animate_a_point_along_a_route.py`
- [ ] `tests/test_examples/test_filter_layer_symbols_using_global_state.py`
- [ ] `tests/test_examples/test_add_a_3d_model_to_globe_using_threejs.py`
- [ ] `tests/test_examples/test_get_coordinates_of_the_mouse_pointer.py`
- [ ] `tests/test_examples/test_jump_to_a_series_of_locations.py`
- [ ] `tests/test_examples/test_slowly_fly_to_a_location.py`
- [ ] `tests/test_examples/test_measure_distances.py`
- [ ] `tests/test_examples/test_offset_the_vanishing_point_using_padding.py`
- [ ] `tests/test_examples/test_navigate_the_map_with_game_like_controls.py`
- [ ] `tests/test_examples/test_customize_camera_animations.py`
