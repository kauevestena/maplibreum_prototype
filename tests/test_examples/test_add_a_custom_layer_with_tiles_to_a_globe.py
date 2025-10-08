import json

from maplibreum import Map
from maplibreum.layers import CustomLayer

HIGHLIGHT_LAYER_ID = "highlight"

ON_ADD = """
function(map, gl) {
    this.shaderMap = new Map();
    this.meshMap = new Map();
}
"""

RENDER = """
function(gl, args) {
    const EXTENT = 8192;
    const uniforms = [
        'u_matrix',
        'u_projection_fallback_matrix',
        'u_projection_matrix',
        'u_projection_clipping_plane',
        'u_projection_transition',
        'u_projection_tile_mercator_coords',
    ];
    const tilesToRender = [];

    function generateTileList(list, current) {
        list.push(current);
        const subdivide = current.z < 2 || (current.x === current.y && current.z < 3) || (current.x === 0 && current.y === 0 && current.z < 7);
        if (subdivide) {
            for (let x = 0; x < 2; x++) {
                for (let y = 0; y < 2; y++) {
                    generateTileList(list, {
                        x: current.x * 2 + x,
                        y: current.y * 2 + y,
                        z: current.z + 1,
                        wrap: current.wrap,
                    });
                }
            }
        }
    }

    for (let i = -1; i <= 1; i++) {
        generateTileList(tilesToRender, {x: 0, y: 0, z: 0, wrap: i});
    }

    const getShader = (gl, shaderDescription) => {
        if (this.shaderMap.has(shaderDescription.variantName)) {
            return this.shaderMap.get(shaderDescription.variantName);
        }

        const vertexSource = `#version 300 es
        ${shaderDescription.vertexShaderPrelude}
        ${shaderDescription.define}

        in vec2 a_pos;
        out mediump vec2 v_pos;

        void main() {

            gl_Position = projectTile(a_pos);
            v_pos = a_pos / float(${EXTENT});
        }`;

        const fragmentSource = `#version 300 es

        precision mediump float;

        in vec2 v_pos;

        out highp vec4 fragColor;
        void main() {
            float alpha = 0.5;
            fragColor = vec4(v_pos, 0.0, 1.0) * alpha;
        }`;

        const vertexShader = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vertexShader, vertexSource);
        gl.compileShader(vertexShader);

        const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fragmentShader, fragmentSource);
        gl.compileShader(fragmentShader);

        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);

        this.aPos = gl.getAttribLocation(program, 'a_pos');

        const locations = {};

        for (const uniform of uniforms) {
            locations[uniform] = gl.getUniformLocation(program, uniform);
        }

        const result = {
            program,
            locations
        };

        this.shaderMap.set(shaderDescription.variantName, result);

        return result;
    };

    const getTileMesh = (gl, x, y, z, border) => {
        const granularity = map.style.projection.subdivisionGranularity.tile.getGranularityForZoomLevel(z);
        const north = y === 0;
        const south = y === (1 << z) - 1;
        const key = `${granularity}_${north}_${south}_${border}`;
        if (this.meshMap.has(key)) {
            return this.meshMap.get(key);
        }

        const meshBuffers = maplibregl.createTileMesh({
            granularity,
            generateBorders: border,
            extendToNorthPole: north,
            extendToSouthPole: south,
        }, '16bit');

        const vbo = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
        gl.bufferData(
            gl.ARRAY_BUFFER,
            meshBuffers.vertices,
            gl.STATIC_DRAW
        );
        gl.bindBuffer(gl.ARRAY_BUFFER, null);
        const ibo = gl.createBuffer();
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ibo);
        gl.bufferData(
            gl.ELEMENT_ARRAY_BUFFER,
            meshBuffers.indices,
            gl.STATIC_DRAW
        );
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, null);

        const mesh = {
            vbo,
            ibo,
            indexCount: meshBuffers.indices.byteLength / 2,
        };
        this.meshMap.set(key, mesh);
        return mesh;
    };

    const {program, locations} = getShader(gl, args.shaderData);

    gl.disable(gl.DEPTH_TEST);
    gl.disable(gl.STENCIL_TEST);
    gl.disable(gl.CULL_FACE);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    gl.useProgram(program);

    const isGlobeProjection = args.shaderData.variantName === 'globe';

    for (const tile of tilesToRender) {
        if (isGlobeProjection && tile.wrap !== 0) {
            continue;
        }

        const tileID = {
            wrap: tile.wrap,
            canonical: {
                x: tile.x,
                y: tile.y,
                z: tile.z,
            }
        };

        const projectionData = map.transform.getProjectionData({overscaledTileID: tileID, applyGlobeMatrix: true});

        gl.uniform4f(
            locations['u_projection_clipping_plane'],
            ...projectionData.clippingPlane
        );
        gl.uniform1f(
            locations['u_projection_transition'],
            projectionData.projectionTransition
        );

        gl.uniform4f(
            locations['u_projection_tile_mercator_coords'],
            ...projectionData.tileMercatorCoords
        );

        gl.uniformMatrix4fv(
            locations['u_projection_matrix'],
            false,
            projectionData.mainMatrix
        );
        gl.uniformMatrix4fv(
            locations['u_projection_fallback_matrix'],
            false,
            projectionData.fallbackMatrix
        );
        const mesh = getTileMesh(gl, tile.x, tile.y, tile.z, false);
        gl.bindBuffer(gl.ARRAY_BUFFER, mesh.vbo);
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, mesh.ibo);
        gl.enableVertexAttribArray(this.aPos);
        gl.vertexAttribPointer(this.aPos, 2, gl.SHORT, false, 0, 0);
        gl.drawElements(gl.TRIANGLES, mesh.indexCount, gl.UNSIGNED_SHORT, 0);
    }
}
"""

highlight_layer = CustomLayer(id=HIGHLIGHT_LAYER_ID, on_add=ON_ADD, render=RENDER)


def test_add_a_custom_layer_with_tiles_to_a_globe():
    map_ = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[7.5, 58],
        zoom=2,
        map_options={"hash": False},
    )
    map_.add_on_load_js("map.setProjection({type: 'globe'});")
    map_.add_layer(highlight_layer)
    with open(
        "development/maplibre_examples/reproduced_pages/add-a-custom-layer-with-tiles-to-a-globe.html",
        "w",
    ) as f:
        f.write(map_.render())
