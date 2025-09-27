import json

from maplibreum import Map, layers, sources

SCRIPT = """
async function main() {
    const THREE = window.THREE;
    const GLTFLoader = window.GLTFLoader;
    const map = maplibregl.getMap();
    function calculateDistanceMercatorToMeters(from, to) {
        const mercatorPerMeter = from.meterInMercatorCoordinateUnits();
        // mercator x: 0=west, 1=east
        const dEast = to.x - from.x;
        const dEastMeter = dEast / mercatorPerMeter;
        // mercator y: 0=north, 1=south
        const dNorth = from.y - to.y;
        const dNorthMeter = dNorth / mercatorPerMeter;
        return {dEastMeter, dNorthMeter};
    }
    async function loadModel() {
        const loader = new GLTFLoader();
        const gltf = await loader.loadAsync('https://maplibre.org/maplibre-gl-js/docs/assets/34M_17/34M_17.gltf');
        const model = gltf.scene;
        return model;
    }
    // Known locations. We'll infer the elevation of those locations once terrain is loaded.
    const sceneOrigin = new maplibregl.LngLat(11.5255, 47.6677);
    const model1Location = new maplibregl.LngLat(11.527, 47.6678);
    const model2Location = new maplibregl.LngLat(11.5249, 47.6676);
    // Configuration of the custom layer for a 3D model, implementing `CustomLayerInterface`.
    const customLayer = {
        id: '3d-model',
        type: 'custom',
        renderingMode: '3d',
        onAdd(map, gl) {
            this.camera = new THREE.Camera();
            this.scene = new THREE.Scene();
            // In threejs, y points up - we're rotating the scene such that it's y points along maplibre's up.
            this.scene.rotateX(Math.PI / 2);
            // In threejs, z points toward the viewer - mirroring it such that z points along maplibre's north.
            this.scene.scale.multiply(new THREE.Vector3(1, 1, -1));
            // We now have a scene with (x=east, y=up, z=north)
            const light = new THREE.DirectionalLight(0xffffff);
            // Making it just before noon - light coming from south-east.
            light.position.set(50, 70, -30).normalize();
            this.scene.add(light);
            // Axes helper to show how threejs scene is oriented.
            const axesHelper = new THREE.AxesHelper(60);
            this.scene.add(axesHelper);
            // Getting model elevations in meters above sea level
            const sceneElevation = map.queryTerrainElevation(sceneOrigin) || 0;
            const model1Elevation = map.queryTerrainElevation(model1Location) || 0;
            const model2Elevation = map.queryTerrainElevation(model2Location) || 0;
            const model1up = model1Elevation - sceneElevation;
            const model2up = model2Elevation - sceneElevation;
            // Getting model x and y (in meters) relative to scene origin.
            const sceneOriginMercator = maplibregl.MercatorCoordinate.fromLngLat(sceneOrigin);
            const model1Mercator = maplibregl.MercatorCoordinate.fromLngLat(model1Location);
            const model2Mercator = maplibregl.MercatorCoordinate.fromLngLat(model2Location);
            const {dEastMeter: model1east, dNorthMeter: model1north} = calculateDistanceMercatorToMeters(sceneOriginMercator, model1Mercator);
            const {dEastMeter: model2east, dNorthMeter: model2north} = calculateDistanceMercatorToMeters(sceneOriginMercator, model2Mercator);
            model1.position.set(model1east, model1up, model1north);
            model2.position.set(model2east, model2up, model2north);
            this.scene.add(model1);
            this.scene.add(model2);
            // Use the MapLibre GL JS map canvas for three.js.
            this.renderer = new THREE.WebGLRenderer({
                canvas: map.getCanvas(),
                context: gl,
                antialias: true
            });
            this.renderer.autoClear = false;
        },
        render(gl, args) {
            const offsetFromCenterElevation = map.queryTerrainElevation(sceneOrigin) || 0;
            const sceneOriginMercator = maplibregl.MercatorCoordinate.fromLngLat(sceneOrigin, offsetFromCenterElevation);
            const sceneTransform = {
                translateX: sceneOriginMercator.x,
                translateY: sceneOriginMercator.y,
                translateZ: sceneOriginMercator.z,
                scale: sceneOriginMercator.meterInMercatorCoordinateUnits()
            };
            const m = new THREE.Matrix4().fromArray(args.defaultProjectionData.mainMatrix);
            const l = new THREE.Matrix4()
                .makeTranslation(sceneTransform.translateX, sceneTransform.translateY, sceneTransform.translateZ)
                .scale(new THREE.Vector3(sceneTransform.scale, -sceneTransform.scale, sceneTransform.scale));
            this.camera.projectionMatrix = m.multiply(l);
            this.renderer.resetState();
            this.renderer.render(this.scene, this.camera);
            map.triggerRepaint();
        }
    };
    const results = await Promise.all([map.once('load'), loadModel()]);
    const model1 = results[1];
    const model2 = model1.clone();
    map.addLayer(customLayer);
}
main();
"""


def test_adding_3d_models_using_threejs_on_terrain():
    map_options = dict(
        center=[11.5257, 47.668],
        zoom=16.27,
        pitch=60,
        bearing=-28.5,
        antialias=True,
    )
    terrain_source = sources.RasterDemSource(
        url="https://demotiles.maplibre.org/terrain-tiles/tiles.json",
        tileSize=256,
    )
    hillshade_source = sources.RasterDemSource(
        url="https://demotiles.maplibre.org/terrain-tiles/tiles.json",
        tileSize=256,
    )
    base_color_layer = layers.Layer(
        id="baseColor",
        type="background",
        paint={"background-color": "#fff", "background-opacity": 1.0},
    )
    hills_layer = layers.HillshadeLayer(
        id="hills",
        source="hillshadeSource",
        layout={"visibility": "visible"},
        paint={"hillshade-shadow-color": "#473B24"},
    )
    map_style = {
        "version": 8,
        "layers": [base_color_layer.to_dict(), hills_layer.to_dict()],
        "terrain": {"source": "terrainSource", "exaggeration": 1},
        "sources": {
            "terrainSource": terrain_source.to_dict(),
            "hillshadeSource": hillshade_source.to_dict(),
        },
    }
    map_object = Map(map_options=map_options, map_style=map_style)
    map_object.add_external_script(
        "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.min.js"
    )
    map_object.add_external_script(
        "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/js/loaders/GLTFLoader.js"
    )
    map_object.add_on_load_js(SCRIPT)
    map_object.render()