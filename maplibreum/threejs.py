"""Three.js integration for maplibreum."""

import math
from textwrap import dedent


class ThreeJSLayer:
    """Represents a custom layer for rendering 3D models using Three.js."""

    def __init__(
        self,
        layer_id: str,
        model_url: str,
        model_origin: list,
        model_altitude: float = 0,
        model_rotate: list = None,
    ):
        if model_rotate is None:
            model_rotate = [90, 0, 0]

        self.layer_id = layer_id
        self.model_url = model_url
        self.model_origin = model_origin
        self.model_altitude = model_altitude
        self.model_rotate_rad = [
            model_rotate[0] * math.pi / 180.0,
            model_rotate[1] * math.pi / 180.0,
            model_rotate[2] * math.pi / 180.0,
        ]

    @property
    def scripts(self) -> list[str]:
        """Returns the list of Three.js scripts required for the layer."""
        return [
            "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.min.js",
            "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/js/loaders/GLTFLoader.js",
        ]

    def add_to(self, before_layer_id: str = None) -> str:
        """Generates the JavaScript code to add the Three.js layer to the map.

        Args:
            before_layer_id (str, optional): The ID of an existing layer to insert the new layer before.

        Returns:
            str: The JavaScript code to add the layer.
        """
        js_code = dedent(
            f'''
            var modelOrigin = [{self.model_origin[0]}, {self.model_origin[1]}];
            var modelAltitude = {self.model_altitude};
            var modelRotate = [{self.model_rotate_rad[0]}, {self.model_rotate_rad[1]}, {self.model_rotate_rad[2]}];

            var modelAsMercatorCoordinate = maplibregl.MercatorCoordinate.fromLngLat(
                modelOrigin,
                modelAltitude
            );

            var modelTransform = {{
                translateX: modelAsMercatorCoordinate.x,
                translateY: modelAsMercatorCoordinate.y,
                translateZ: modelAsMercatorCoordinate.z,
                rotateX: modelRotate[0],
                rotateY: modelRotate[1],
                rotateZ: modelRotate[2],
                scale: modelAsMercatorCoordinate.meterInMercatorCoordinateUnits()
            }};

            var customLayer = {{
                id: '{self.layer_id}',
                type: 'custom',
                renderingMode: '3d',
                onAdd: function(map, gl) {{
                    this.camera = new THREE.Camera();
                    this.scene = new THREE.Scene();

                    var lightA = new THREE.DirectionalLight(0xffffff);
                    lightA.position.set(0, -70, 100).normalize();
                    this.scene.add(lightA);

                    var lightB = new THREE.DirectionalLight(0xffffff);
                    lightB.position.set(0, 70, 100).normalize();
                    this.scene.add(lightB);

                    var loader = new THREE.GLTFLoader();
                    loader.load(
                        '{self.model_url}',
                        function(gltf) {{
                            this.scene.add(gltf.scene);
                        }}.bind(this)
                    );

                    this.map = map;
                    this.renderer = new THREE.WebGLRenderer({{
                        canvas: map.getCanvas(),
                        context: gl,
                        antialias: true
                    }});
                    this.renderer.autoClear = false;
                }},
                render: function(gl, args) {{
                    var rotationX = new THREE.Matrix4().makeRotationAxis(
                        new THREE.Vector3(1, 0, 0),
                        modelTransform.rotateX
                    );
                    var rotationY = new THREE.Matrix4().makeRotationAxis(
                        new THREE.Vector3(0, 1, 0),
                        modelTransform.rotateY
                    );
                    var rotationZ = new THREE.Matrix4().makeRotationAxis(
                        new THREE.Vector3(0, 0, 1),
                        modelTransform.rotateZ
                    );

                    var projectionMatrix = new THREE.Matrix4().fromArray(
                        args.defaultProjectionData.mainMatrix
                    );
                    var translation = new THREE.Matrix4()
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

                    this.camera.projectionMatrix = projectionMatrix.multiply(translation);
                    this.renderer.resetState();
                    this.renderer.render(this.scene, this.camera);
                    this.map.triggerRepaint();
                }}
            }};

            map.addLayer(customLayer, '{before_layer_id if before_layer_id else ""
            }');
        '''
        )
        return js_code
