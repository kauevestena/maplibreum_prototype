"""Test for the add-a-3d-model-using-threejs MapLibre example."""

from textwrap import dedent

from maplibreum import Map
from maplibreum.threejs import ThreeJSLayer


def test_add_a_3d_model_using_threejs_configuration():
    """Ensure the custom three.js layer mirrors the reference example."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[148.9819, -35.3981],
        zoom=18,
        pitch=60,
        map_options={"canvasContextAttributes": {"antialias": True}},
    )

    map_instance.add_external_script(
        "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.min.js",
        defer=True,
    )
    map_instance.add_external_script(
        (
            "https://cdn.jsdelivr.net/"
            "npm/three@0.169.0/examples/js/loaders/GLTFLoader.js"
        ),
        defer=True,
    )

    custom_layer_js = dedent(
        """
        var modelOrigin = [148.9819, -35.39847];
        var modelAltitude = 0;
        var modelRotate = [Math.PI / 2, 0, 0];

        var modelAsMercatorCoordinate = maplibregl.MercatorCoordinate.fromLngLat(
            modelOrigin,
            modelAltitude
        );

        var modelTransform = {
            translateX: modelAsMercatorCoordinate.x,
            translateY: modelAsMercatorCoordinate.y,
            translateZ: modelAsMercatorCoordinate.z,
            rotateX: modelRotate[0],
            rotateY: modelRotate[1],
            rotateZ: modelRotate[2],
            scale: modelAsMercatorCoordinate.meterInMercatorCoordinateUnits()
        };

        var customLayer = {
            id: '3d-model',
            type: 'custom',
            renderingMode: '3d',
            onAdd: function(map, gl) {
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
                    'https://maplibre.org/maplibre-gl-js/docs/assets/34M_17/34M_17.gltf',
                    function(gltf) {
                        this.scene.add(gltf.scene);
                    }.bind(this)
                );

                this.map = map;
                this.renderer = new THREE.WebGLRenderer({
                    canvas: map.getCanvas(),
                    context: gl,
                    antialias: true
                });
                this.renderer.autoClear = false;
            },
            render: function(gl, args) {
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
            }
        };

        map.on('style.load', function() {
            map.addLayer(customLayer);
        });
        """
    ).strip()

    map_instance.add_on_load_js(custom_layer_js)

    html = map_instance.render()

    assert "three.min.js" in html
    assert "GLTFLoader.js" in html
    assert "\"canvasContextAttributes\": {\"antialias\": true}" in html
    assert "maplibregl.MercatorCoordinate.fromLngLat" in html
    assert "renderingMode: '3d'" in html
    assert "makeRotationAxis" in html
    assert "meterInMercatorCoordinateUnits" in html
    assert "map.addLayer(customLayer);" in html


def test_add_a_3d_model_using_threejs_with_python_api():
    """Test the ThreeJSLayer class for adding a 3D model."""
    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[148.9819, -35.3981],
        zoom=18,
        pitch=60,
        map_options={"canvasContextAttributes": {"antialias": True}},
    )

    threejs_layer = ThreeJSLayer(
        id="3d-model",
        model_uri="https://maplibre.org/maplibre-gl-js/docs/assets/34M_17/34M_17.gltf",
        model_origin=[148.9819, -35.39847],
        model_altitude=0.0,
        model_rotate=[90, 0, 0],
    )

    map_instance.add_layer(threejs_layer)

    html = map_instance.render()

    assert "three.min.js" in html
    assert "GLTFLoader.js" in html
    assert "const modelOrigin = [148.9819, -35.39847];" in html
    assert "const modelAltitude = 0.0;" in html
    assert "const modelRotate = [1.5707963267948966, 0.0, 0.0];" in html
    assert "id: '3d-model'" in html
    assert "type: 'custom'" in html
    assert "renderingMode: '3d'" in html


def test_threejslayer_backward_compatible_positional_args():
    """Ensure the legacy positional signature remains functional."""
    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[148.9819, -35.3981],
        zoom=18,
        pitch=60,
        map_options={"canvasContextAttributes": {"antialias": True}},
    )

    threejs_layer = ThreeJSLayer(
        "3d-model",
        "https://maplibre.org/maplibre-gl-js/docs/assets/34M_17/34M_17.gltf",
        [148.9819, -35.39847],
        0.0,
        [90, 0, 0],
    )

    map_instance.add_layer(threejs_layer)

    html = map_instance.render()

    assert "const scaling = 1.0;" in html
    assert "const modelRotate = [1.5707963267948966, 0.0, 0.0];" in html
