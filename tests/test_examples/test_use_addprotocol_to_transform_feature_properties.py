from maplibreum import Map
from maplibreum.protocols import FeatureTransformProtocol


def test_use_addprotocol_to_transform_feature_properties():
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[8, 47],
        zoom=5,
        map_options={"hash": "map"},
    )

    protocol_name = "reverse"

    # JavaScript code to process each feature
    process_feature_js = """
    if (feature.properties && typeof feature.properties['NAME'] === 'string') {
        feature.properties['NAME'] = feature.properties['NAME'].split('').reverse().join('');
    }
    if (feature.properties && typeof feature.properties['ABBREV'] === 'string') {
        feature.properties['ABBREV'] = feature.properties['ABBREV'].split('').reverse().join('');
    }
    """

    protocol = FeatureTransformProtocol(name=protocol_name, process_feature_js=process_feature_js)
    m.add_protocol(protocol)

    transform_request_js = f"""(url, resourceType) => {{
        if (url.startsWith('https://demotiles.maplibre.org/tiles/') && resourceType === 'Tile') {{
            return {{ url: '{protocol_name}://' + url }};
        }}
        return undefined;
    }}"""

    m.set_transform_request(transform_request_js)

    html = m.render()

    assert f"maplibregl.addProtocol('{protocol_name}'" in html
    assert "tileToProtobuf" in html
    assert "map.setTransformRequest" in html
    assert "split('').reverse().join('')" in html
    assert '"hash": "map"' in html.replace("\n", "")
