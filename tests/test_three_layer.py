import pytest

from maplibreum.core import Map
from maplibreum.three import ThreeLayer

def test_three_layer_init_defaults():
    """Test initialization with default values."""
    layer = ThreeLayer(
        id="test-three-layer",
        model_uri="https://example.com/model.gltf",
        model_origin=[-122.4194, 37.7749]
    )

    assert layer.id == "test-three-layer"
    assert layer.model_uri == "https://example.com/model.gltf"
    assert layer.model_origin == [-122.4194, 37.7749]
    assert layer.model_altitude == 0
    assert layer.model_rotate == [0, 0, 0]

def test_three_layer_init_custom():
    """Test initialization with custom values."""
    layer = ThreeLayer(
        id="test-three-layer-custom",
        model_uri="https://example.com/custom.gltf",
        model_origin=[0, 0],
        model_altitude=100.5,
        model_rotate=[90.0, 45.0, 180.0]
    )

    assert layer.id == "test-three-layer-custom"
    assert layer.model_uri == "https://example.com/custom.gltf"
    assert layer.model_origin == [0, 0]
    assert layer.model_altitude == 100.5
    assert layer.model_rotate == [90.0, 45.0, 180.0]

def test_three_layer_to_dict():
    """Test that to_dict includes custom rendering mode and base properties."""
    layer = ThreeLayer(
        id="test-three-layer-dict",
        model_uri="https://example.com/model.gltf",
        model_origin=[-122.4194, 37.7749]
    )

    d = layer.to_dict()
    assert d["id"] == "test-three-layer-dict"
    assert d["type"] == "custom"
    assert d["renderingMode"] == "3d"

def test_three_layer_js_code():
    """Test that js_code correctly generates javascript with variables injected."""
    layer = ThreeLayer(
        id="test-three-js",
        model_uri="https://example.com/model.gltf",
        model_origin=[-122.4194, 37.7749],
        model_altitude=50,
        model_rotate=[10, 20, 30]
    )

    js = layer.js_code

    # Check injected properties
    assert "const modelOrigin = [-122.4194, 37.7749];" in js
    assert "const modelAltitude = 50;" in js
    assert "const modelRotate = [10, 20, 30];" in js
    assert "id: 'test-three-js'" in js
    assert "'https://example.com/model.gltf'" in js
    assert "type: 'custom'" in js
    assert "renderingMode: '3d'" in js

    # Check map load trigger
    assert "map.on('style.load', () => {" in js
    assert "map.addLayer(customLayer);" in js

def test_three_layer_add_to_map():
    """Test that adding ThreeLayer to a map works as expected."""
    m = Map()
    layer = ThreeLayer(
        id="test-three-map",
        model_uri="https://example.com/model.gltf",
        model_origin=[-122.4194, 37.7749]
    )

    m.add_layer(layer)

    # In map.layers, it's stored as a dictionary, check if the id is present
    assert any(l.get('id') == "test-three-map" for l in m.layers)

    # Check that required scripts are included in external_scripts
    three_script_found = any('three.js' in s.get('src', '') for s in m.external_scripts)
    gltf_script_found = any('GLTFLoader.js' in s.get('src', '') for s in m.external_scripts)

    assert three_script_found, "three.js not found in external_scripts"
    assert gltf_script_found, "GLTFLoader.js not found in external_scripts"

    # Check that the custom js code is added to on_load_callbacks
    assert any("map.addLayer(customLayer);" in js for js in m._on_load_callbacks)
