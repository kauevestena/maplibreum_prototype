"""Dedicated support for three.js custom layers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .layers import Layer


class ThreeLayer(Layer):
    """Represents a three.js custom layer for rendering 3D models."""

    def __init__(
        self,
        id: str,
        model_uri: str,
        model_origin: List[float],
        model_altitude: float = 0,
        model_rotate: Optional[List[float]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a ThreeLayer.

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
const modelOrigin = [{self.model_origin[0]}, {self.model_origin[1]}];
const modelAltitude = {self.model_altitude};
const modelRotate = [{self.model_rotate[0]}, {self.model_rotate[1]}, {self.model_rotate[2]}];

const modelAsMercatorCoordinate = maplibregl.MercatorCoordinate.fromLngLat(
    modelOrigin,
    modelAltitude
);

const modelTransform = {{
    translateX: modelAsMercatorCoordinate.x,
    translateY: modelAsMercatorCoordinate.y,
    translateZ: modelAsMercatorCoordinate.z,
    rotateX: modelRotate[0],
    rotateY: modelRotate[1],
    rotateZ: modelRotate[2],
    scale: modelAsMercatorCoordinate.meterInMercatorCoordinateUnits()
}};

const customLayer = {{
    id: '{self.id}',
    type: 'custom',
    renderingMode: '3d',
    onAdd: function (map, gl) {{
        this.camera = new THREE.Camera();
        this.scene = new THREE.Scene();

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(100, 100, 100);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);

        directionalLight.shadow.camera.near = 0.1;
        directionalLight.shadow.camera.far = 2000;
        directionalLight.shadow.camera.left = -500;
        directionalLight.shadow.camera.right = 500;
        directionalLight.shadow.camera.top = 500;
        directionalLight.shadow.camera.bottom = -500;

        directionalLight.shadow.mapSize.width = 4096;
        directionalLight.shadow.mapSize.height = 4096;

        const groundGeometry = new THREE.PlaneGeometry(1000, 1000);
        const groundMaterial = new THREE.ShadowMaterial({{ opacity: 0.5 }});
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = modelAsMercatorCoordinate.z;
        ground.receiveShadow = true;
        this.scene.add(ground);

        const loader = new THREE.GLTFLoader();
        loader.load(
            '{self.model_uri}',
            (gltf) => {{
                gltf.scene.traverse(function (node) {{
                    if (node.isMesh || node.isLight) {{
                        node.castShadow = true;
                        node.receiveShadow = true;
                    }}
                }});
                this.scene.add(gltf.scene);
            }}
        );
        this.map = map;

        this.renderer = new THREE.WebGLRenderer({{
            canvas: map.getCanvas(),
            context: gl,
            antialias: true
        }});
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        this.renderer.autoClear = false;
    }},
    render: function (gl, args) {{
        const rotationX = new THREE.Matrix4().makeRotationAxis(
            new THREE.Vector3(1, 0, 0),
            modelTransform.rotateX
        );
        const rotationY = new THREE.Matrix4().makeRotationAxis(
            new THREE.Vector3(0, 1, 0),
            modelTransform.rotateY
        );
        const rotationZ = new THREE.Matrix4().makeRotationAxis(
            new THREE.Vector3(0, 0, 1),
            modelTransform.rotateZ
        );

        const m = new THREE.Matrix4().fromArray(args.defaultProjectionData.mainMatrix);
        const l = new THREE.Matrix4()
            .makeTranslation(
                modelTransform.translateX,
                modelTransform.translateY,
                modelTransform.translateZ
            )
            .scale(
                new THREE.Vector3(
                    modelTransform.scale,
                    -modelTransform.scale,
                    modelTransform.scale
                )
            )
            .multiply(rotationX)
            .multiply(rotationY)
            .multiply(rotationZ);

        this.camera.projectionMatrix = m.multiply(l);
        this.renderer.resetState();
        this.renderer.render(this.scene, this.camera);
        this.map.triggerRepaint();
    }}
}};

map.on('style.load', () => {{
    map.addLayer(customLayer);
}});
"""