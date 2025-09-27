from maplibreum import Map


TRANSFORM_JS = """
(async () => {
    const protocolName = 'reverse';
    const [{ default: Protobuf }, { VectorTile }, { default: tileToProtobuf }] = await Promise.all([
        import('https://unpkg.com/pbf@4.0.1/dist/pbf.min.js'),
        import('https://esm.run/@mapbox/vector-tile@2.0.3/index.js'),
        import('https://esm.run/vt-pbf@3.1.3/index.js'),
    ]);
    maplibregl.addProtocol(protocolName, async (request) => {
        const url = request.url.replace(protocolName + '://', '');
        const response = await fetch(url);
        const data = await response.arrayBuffer();
        const tile = new VectorTile(new Protobuf(data));
        const layers = Object.fromEntries(
            Object.entries(tile.layers).map(([layerId, layer]) => [
                layerId,
                {
                    ...layer,
                    feature: (index) => {
                        const feature = layer.feature(index);
                        if (feature.properties && typeof feature.properties['NAME'] === 'string') {
                            feature.properties['NAME'] = feature.properties['NAME'].split('').reverse().join('');
                        }
                        if (feature.properties && typeof feature.properties['ABBREV'] === 'string') {
                            feature.properties['ABBREV'] = feature.properties['ABBREV'].split('').reverse().join('');
                        }
                        return feature;
                    },
                },
            ])
        );
        const encoded = tileToProtobuf({ layers });
        return { data: encoded.buffer };
    });
    map.setTransformRequest((url, resourceType) => {
        if (url.startsWith('https://demotiles.maplibre.org/tiles/') && resourceType === 'Tile') {
            return { url: protocolName + '://' + url };
        }
        return undefined;
    });
})();
"""


def test_use_addprotocol_to_transform_feature_properties():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[8, 47],
        zoom=5,
        map_options={"hash": "map"},
    )

    m.add_on_load_js(TRANSFORM_JS)

    html = m.render()

    assert "maplibregl.addProtocol(protocolName" in html
    assert "tileToProtobuf" in html
    assert "map.setTransformRequest" in html
    assert "split('').reverse().join('')" in html
    assert '"hash": "map"' in html.replace("\n", "")
