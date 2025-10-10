from maplibreum import CustomGlobeLayer, Map

HIGHLIGHT_LAYER_ID = "highlight"


def test_add_a_custom_layer_with_tiles_to_a_globe_with_python_api():
    """Validate the CustomGlobeLayer with a Python API approach."""
    map_ = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[7.5, 58],
        zoom=2,
        map_options={"hash": False},
    )
    map_.add_on_load_js("map.setProjection({type: 'globe'});")

    # Use the new CustomGlobeLayer
    highlight_layer = CustomGlobeLayer(id=HIGHLIGHT_LAYER_ID)
    map_.add_layer(highlight_layer)

    # Just render the map, no need to write to file for this test
    assert "custom" in map_.render()
