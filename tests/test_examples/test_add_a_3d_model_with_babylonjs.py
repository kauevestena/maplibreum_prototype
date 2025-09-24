"""Test for the add-a-3d-model-with-babylonjs MapLibre example."""
import math

from maplibreum import Map
from maplibreum.babylon import BabylonLayer


def test_add_a_3d_model_with_babylonjs():
    """Validate that a custom babylon.js layer can be added."""
    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[148.9819, -35.3981],
        zoom=18,
        pitch=60,
        map_options={"canvasContextAttributes": {"antialias": True}},
    )

    layer = BabylonLayer(
        id="3d-model",
        model_uri="https://maplibre.org/maplibre-gl-js/docs/assets/34M_17/34M_17.gltf",
        model_origin=[148.9819, -35.39847],
        model_rotate=[math.pi / 2, 0, 0],
    )

    map_instance.add_layer(layer)

    html = map_instance.render()
    assert "babylon.js" in html
    assert "babylonjs.loaders.min.js" in html
    assert "new BABYLON.Engine" in html
    assert "BABYLON.SceneLoader.LoadAssetContainerAsync" in html
    assert "map.addLayer(customLayer);" in html