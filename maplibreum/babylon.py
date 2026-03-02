"""Dedicated support for babylon.js custom layers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .layers import Layer

BABYLON_JS_URL = "https://unpkg.com/babylonjs@5.42.2/babylon.js"
BABYLON_LOADERS_JS_URL = "https://unpkg.com/babylonjs-loaders@5.42.2/babylonjs.loaders.min.js"


class BabylonLayer(Layer):
    """Represents a babylon.js custom layer for rendering 3D models."""

    def __init__(
        self,
        id: str,
        model_uri: str,
        model_origin: List[float],
        model_altitude: float = 0,
        model_rotate: Optional[List[float]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a BabylonLayer.

        Parameters
        ----------
        id : str
            The ID of the layer.
        model_uri : str
            The URI of the 3D model (e.g., in GLTF format).
        model_origin : list of float
            The [longitude, latitude] pair for the model's origin.
        model_altitude : float, optional
            The altitude of the model's origin in meters.
        model_rotate : list of float, optional
            The rotation of the model as ``[x, y, z]`` Euler angles.
        """
        super().__init__(id, "custom", **kwargs)
        self.model_uri = model_uri
        self.model_origin = model_origin
        self.model_altitude = model_altitude
        self.model_rotate = model_rotate or [0, 0, 0]

    def to_dict(self) -> Dict[str, Any]:
        """Return the layer definition as a plain dictionary."""
        layer_dict = super().to_dict()
        layer_dict["renderingMode"] = "3d"
        return layer_dict

    @property
    def js_code(self) -> str:
        """Generate the JavaScript code for the custom layer."""
        return f"""
const worldOrigin = [{self.model_origin[0]}, {self.model_origin[1]}];
const worldAltitude = {self.model_altitude};
const worldRotate = [{self.model_rotate[0]}, {self.model_rotate[1]}, {self.model_rotate[2]}];
const worldOriginMercator = maplibregl.MercatorCoordinate.fromLngLat(
    worldOrigin,
    worldAltitude
);
const worldScale = worldOriginMercator.meterInMercatorCoordinateUnits();
const worldMatrix = BABYLON.Matrix.Compose(
    new BABYLON.Vector3(worldScale, worldScale, worldScale),
    BABYLON.Quaternion.FromEulerAngles(
        worldRotate[0],
        worldRotate[1],
        worldRotate[2]
    ),
    new BABYLON.Vector3(
        worldOriginMercator.x,
        worldOriginMercator.y,
        worldOriginMercator.z
    )
);

const customLayer = {{
    id: '{self.id}',
    type: 'custom',
    renderingMode: '3d',
    onAdd (map, gl) {{
        this.engine = new BABYLON.Engine(
            gl,
            true,
            {{
                useHighPrecisionMatrix: true
            }},
            true
        );
        this.scene = new BABYLON.Scene(this.engine);
        this.scene.autoClear = false;
        this.scene.detachControl();

        this.scene.beforeRender = () => {{
            this.engine.wipeCaches(true);
        }};
        this.camera = new BABYLON.Camera(
            'Camera',
            new BABYLON.Vector3(0, 0, 0),
            this.scene
        );
        const light = new BABYLON.HemisphericLight(
            'light1',
            new BABYLON.Vector3(0, 0, 100),
            this.scene
        );
        light.intensity = 0.7;
        new BABYLON.AxesViewer(this.scene, 10);
        BABYLON.SceneLoader.LoadAssetContainerAsync(
            '{self.model_uri}',
            '',
            this.scene
        ).then((modelContainer) => {{
            modelContainer.addAllToScene();
            const rootMesh = modelContainer.createRootMesh();
            const rootMesh2 = rootMesh.clone();
            rootMesh2.position.x = 25;
            rootMesh2.position.z = 25;
        }});

        this.map = map;
    }},
    render (gl, args) {{
        const cameraMatrix = BABYLON.Matrix.FromArray(args.defaultProjectionData.mainMatrix);
        const wvpMatrix = worldMatrix.multiply(cameraMatrix);
        this.camera.freezeProjectionMatrix(wvpMatrix);
        this.scene.render(false);
        this.map.triggerRepaint();
    }}
}};
map.on('style.load', () => {{
    map.addLayer(customLayer);
}});
"""