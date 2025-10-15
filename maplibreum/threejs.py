"""Three.js integration for maplibreum."""

import math
from textwrap import dedent


class ThreeJSLayer:
    """Represents a custom layer for rendering 3D models using Three.js."""

    def __init__(
        self,
        id: str = None,
        model_uri: str = None,
        model_origin: list = None,
        model_altitude: float = 0,
        model_rotate: list = None,
        model_scale: float = 1.0,
        globe: bool = False,
        terrain: bool = False,
        models: list = None,
        scene_origin: list = None,
        *,
        layer_id: str = None,
        model_url: str = None,
    ):
        if id is None:
            id = layer_id
        elif layer_id is not None and id != layer_id:
            raise ValueError("Conflicting values provided for 'id' and 'layer_id'.")

        if model_uri is None:
            model_uri = model_url
        elif model_url is not None and model_uri != model_url:
            raise ValueError("Conflicting values provided for 'model_uri' and 'model_url'.")

        if id is None:
            raise ValueError("ThreeJSLayer requires an 'id' (or 'layer_id').")

        if not terrain:
            if model_uri is None:
                raise ValueError("ThreeJSLayer requires a 'model_uri' (or 'model_url').")

            if model_origin is None:
                raise ValueError("ThreeJSLayer requires 'model_origin'.")

        if model_scale is None:
            model_scale = 1.0

        if model_rotate is None:
            model_rotate = [math.pi / 2, 0, 0]
        else:
            model_rotate = [
                model_rotate[0] * math.pi / 180.0,
                model_rotate[1] * math.pi / 180.0,
                model_rotate[2] * math.pi / 180.0,
            ]

        self.id = id
        self.model_uri = model_uri
        self.model_origin = model_origin
        self.model_altitude = model_altitude
        self.model_scale = model_scale
        self.model_rotate = model_rotate
        self.globe = globe
        self.terrain = terrain
        self.models = models
        self.scene_origin = scene_origin

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

        if self.terrain:
            models_js = "[\n"
            for model in self.models:
                models_js += f"""                {{
                    uri: '{model["uri"]}',
                    location: new maplibregl.LngLat({model["location"][0]}, {model["location"][1]})
                }},\n"""
            models_js += "            ]"

            js_code = dedent(f"""
                async function main() {{
                    const THREE = window.THREE;
                    const GLTFLoader = window.GLTFLoader;
                    const map = maplibregl.getMap();

                    const sceneOrigin = new maplibregl.LngLat({self.scene_origin[0]}, {self.scene_origin[1]});
                    const models = {models_js};

                    function calculateDistanceMercatorToMeters(from, to) {{
                        const mercatorPerMeter = from.meterInMercatorCoordinateUnits();
                        const dEast = to.x - from.x;
                        const dEastMeter = dEast / mercatorPerMeter;
                        const dNorth = from.y - to.y;
                        const dNorthMeter = dNorth / mercatorPerMeter;
                        return {{dEastMeter, dNorthMeter}};
                    }}

                    async function loadModels() {{
                        const loader = new GLTFLoader();
                        const loadedModels = [];
                        for (const modelInfo of models) {{
                            const gltf = await loader.loadAsync(modelInfo.uri);
                            loadedModels.push({{ model: gltf.scene, location: modelInfo.location }});
                        }}
                        return loadedModels;
                    }}

                    const customLayer = {{
                        id: '{self.id}',
                        type: 'custom',
                        renderingMode: '3d',
                        onAdd: function(map, gl) {{
                            this.camera = new THREE.Camera();
                            this.scene = new THREE.Scene();
                            this.scene.rotateX(Math.PI / 2);
                            this.scene.scale.multiply(new THREE.Vector3(1, 1, -1));

                            const light = new THREE.DirectionalLight(0xffffff);
                            light.position.set(50, 70, -30).normalize();
                            this.scene.add(light);

                            const sceneElevation = map.queryTerrainElevation(sceneOrigin) || 0;

                            for (const loadedModel of this.loadedModels) {{
                                const modelElevation = map.queryTerrainElevation(loadedModel.location) || 0;
                                const modelUp = modelElevation - sceneElevation;

                                const sceneOriginMercator = maplibregl.MercatorCoordinate.fromLngLat(sceneOrigin);
                                const modelMercator = maplibregl.MercatorCoordinate.fromLngLat(loadedModel.location);
                                const {{dEastMeter: modelEast, dNorthMeter: modelNorth}} = calculateDistanceMercatorToMeters(sceneOriginMercator, modelMercator);

                                loadedModel.model.position.set(modelEast, modelUp, modelNorth);
                                this.scene.add(loadedModel.model);
                            }}

                            this.renderer = new THREE.WebGLRenderer({{
                                canvas: map.getCanvas(),
                                context: gl,
                                antialias: true
                            }});
                            this.renderer.autoClear = false;
                        }},
                        render: function(gl, args) {{
                            const offsetFromCenterElevation = map.queryTerrainElevation(sceneOrigin) || 0;
                            const sceneOriginMercator = maplibregl.MercatorCoordinate.fromLngLat(sceneOrigin, offsetFromCenterElevation);
                            const sceneTransform = {{
                                translateX: sceneOriginMercator.x,
                                translateY: sceneOriginMercator.y,
                                translateZ: sceneOriginMercator.z,
                                scale: sceneOriginMercator.meterInMercatorCoordinateUnits()
                            }};

                            const m = new THREE.Matrix4().fromArray(args.defaultProjectionData.mainMatrix);
                            const l = new THREE.Matrix4()
                                .makeTranslation(sceneTransform.translateX, sceneTransform.translateY, sceneTransform.translateZ)
                                .scale(new THREE.Vector3(sceneTransform.scale, -sceneTransform.scale, sceneTransform.scale));
                            this.camera.projectionMatrix = m.multiply(l);
                            this.renderer.resetState();
                            this.renderer.render(this.scene, this.camera);
                            map.triggerRepaint();
                        }}
                    }};

                    const results = await Promise.all([map.once('load'), loadModels()]);
                    customLayer.loadedModels = results[1];
                    map.addLayer(customLayer, '{before_layer_id if before_layer_id else ""}');
                }}
                main();
            """)
        else:
            js_code = dedent(f"""
                const modelOrigin = [{self.model_origin[0]}, {self.model_origin[1]}];
                const modelAltitude = {self.model_altitude};
                const modelRotate = [{self.model_rotate[0]}, {self.model_rotate[1]}, {self.model_rotate[2]}];
                const scaling = {self.model_scale};

                const customLayer = {{
                    id: '{self.id}',
                    type: 'custom',
                    renderingMode: '3d',
                    onAdd: function(map, gl) {{
                        this.camera = new THREE.Camera();
                        this.scene = new THREE.Scene();

                        const lightA = new THREE.DirectionalLight(0xffffff);
                        lightA.position.set(0, -70, 100).normalize();
                        this.scene.add(lightA);

                        const lightB = new THREE.DirectionalLight(0xffffff);
                        lightB.position.set(0, 70, 100).normalize();
                        this.scene.add(lightB);

                        const loader = new THREE.GLTFLoader();
                        loader.load(
                            '{self.model_uri}',
                            (gltf) => {{
                                this.scene.add(gltf.scene);
                            }}
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
                        if ({str(self.globe).lower()}) {{
                            const modelMatrix = map.transform.getMatrixForModel(
                                modelOrigin,
                                modelAltitude
                            );
                            const projectionMatrix = new THREE.Matrix4().fromArray(
                                args.defaultProjectionData.mainMatrix
                            );
                            const transform = new THREE.Matrix4()
                                .fromArray(modelMatrix)
                                .scale(new THREE.Vector3(scaling, scaling, scaling));
                            this.camera.projectionMatrix = projectionMatrix.multiply(transform);
                        }} else {{
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
                                scale: modelAsMercatorCoordinate.meterInMercatorCoordinateUnits() * scaling
                            }};

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

                            const projectionMatrix = new THREE.Matrix4().fromArray(
                                args.defaultProjectionData.mainMatrix
                            );
                            const translation = new THREE.Matrix4()
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
                        }}
                        this.renderer.resetState();
                        this.renderer.render(this.scene, this.camera);
                        this.map.triggerRepaint();
                    }}
                }};

                map.addLayer(customLayer, '{before_layer_id if before_layer_id else ""}');
            """)
        return js_code
