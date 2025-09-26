import json
from maplibreum import Map
from maplibreum.three import ThreeLayer

def test_add_a_3d_model_with_shadow_using_threejs():
    model_origin = [148.9819, -35.39847]
    model_altitude = 0
    model_rotate = [1.5707963267948966, 0, 0]

    map_obj = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[148.9819, -35.3981],
        zoom=18,
        pitch=60,
        map_options={"canvasContextAttributes": {"antialias": True}},
    )

    three_layer = ThreeLayer(
        id="3d-model",
        model_uri="https://maplibre.org/maplibre-gl-js/docs/assets/34M_17/34M_17.gltf",
        model_origin=model_origin,
        model_altitude=model_altitude,
        model_rotate=model_rotate,
    )

    map_obj.add_layer(three_layer)
    html = map_obj.render()
    assert "three.js" in html
    assert "GLTFLoader.js" in html
    assert '"renderingMode": "3d"' in html
    assert "directionalLight.castShadow = true;" in html
    assert "renderer.shadowMap.enabled = true;" in html
    assert "ground.receiveShadow = true;" in html