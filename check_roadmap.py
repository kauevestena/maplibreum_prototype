import re
import os

roadmap = """- [ ] `tests/test_examples/test_disable_map_rotation.py`
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
- [ ] `tests/test_examples/test_customize_camera_animations.py`"""

files = re.findall(r'`(tests/test_examples/.*?)`', roadmap)

for f in files:
    if os.path.exists(f):
        content = open(f).read()
        has_js = "add_on_load_js" in content or "add_external_script" in content
        has_python_api = "with_python_api" in content
        print(f"{f}: JS={has_js}, PythonAPI={has_python_api}")
    else:
        print(f"{f}: Not found")
