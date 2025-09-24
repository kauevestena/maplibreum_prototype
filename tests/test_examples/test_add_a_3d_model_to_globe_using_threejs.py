"""Test for the add-a-3d-model-to-globe-using-threejs MapLibre example."""

from textwrap import dedent

from maplibreum import Map


def test_add_a_3d_model_to_globe_using_threejs_configuration():
    """Ensure the custom three.js layer and projection toggles are wired up."""

    map_instance = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[150.16546137527212, -35.017179237129994],
        zoom=5.5,
        pitch=70,
        map_options={
            "maxPitch": 80,
            "canvasContextAttributes": {"antialias": True},
        },
    )

    map_instance.custom_css = dedent(
        """
        .maplibreum-projection-toggle {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translate(-50%);
            width: 50%;
            height: 40px;
            padding: 10px;
            border: none;
            border-radius: 3px;
            font-size: 12px;
            text-align: center;
            color: #fff;
            background: #ee8a65;
            cursor: pointer;
        }
        """
    ).strip()

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
        map.once('style.load', function() {
            map.setProjection({ type: 'globe' });
        });

        var projectionToggle = document.getElementById('projection-toggle');
        if (!projectionToggle) {
            projectionToggle = document.createElement('button');
            projectionToggle.id = 'projection-toggle';
            projectionToggle.className = 'maplibreum-projection-toggle';
            projectionToggle.textContent = 'Toggle projection';
            document.body.appendChild(projectionToggle);
        }

        projectionToggle.addEventListener('click', function() {
            var current = map.getProjection();
            var next = current.type === 'globe' ? 'mercator' : 'globe';
            map.setProjection({ type: next });
        });

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
                    (gltf) => {
                        this.scene.add(gltf.scene);
                    }
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
                var modelOrigin = [148.9819, -35.39847];
                var modelAltitude = 0.0;
                var scaling = 10000.0;
                var modelMatrix = map.transform.getMatrixForModel(
                    modelOrigin,
                    modelAltitude
                );
                var projectionMatrix = new THREE.Matrix4().fromArray(
                    args.defaultProjectionData.mainMatrix
                );
                var transform = new THREE.Matrix4()
                    .fromArray(modelMatrix)
                    .scale(new THREE.Vector3(scaling, scaling, scaling));
                this.camera.projectionMatrix = projectionMatrix.multiply(transform);
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
    assert "\"maxPitch\": 80" in html
    assert "\"canvasContextAttributes\": {\"antialias\": true}" in html
    assert "map.setProjection({ type: 'globe' });" in html
    assert "renderingMode: '3d'" in html
    assert "map.transform.getMatrixForModel" in html
    assert "map.addLayer(customLayer);" in html
    assert ".maplibreum-projection-toggle" in html
