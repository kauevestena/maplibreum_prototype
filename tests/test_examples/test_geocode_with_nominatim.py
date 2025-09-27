from maplibreum import Map


GEOCODER_SCRIPT = "https://unpkg.com/@maplibre/maplibre-gl-geocoder@1.5.0/dist/maplibre-gl-geocoder.min.js"


GEOCODER_JS = """
const nominatimResponse = {
    features: [
        {
            bbox: [-87.627815, 41.867576, -87.615211, 41.87221],
            properties: { display_name: 'Museum Campus, Chicago, Illinois, United States' },
        },
    ],
};
const geocoderApi = {
    forwardGeocode: async (config) => {
        const query = config.query;
        console.log('Mock forwardGeocode query', query);
        const featureCollection = nominatimResponse.features.map((feature) => {
            const center = [
                feature.bbox[0] + (feature.bbox[2] - feature.bbox[0]) / 2,
                feature.bbox[1] + (feature.bbox[3] - feature.bbox[1]) / 2,
            ];
            return {
                type: 'Feature',
                geometry: { type: 'Point', coordinates: center },
                place_name: feature.properties.display_name,
                properties: feature.properties,
                text: feature.properties.display_name,
                place_type: ['place'],
                center,
            };
        });
        return { features: featureCollection };
    },
};
map.addControl(new MaplibreGeocoder(geocoderApi, { maplibregl }));
"""


def test_geocode_with_nominatim():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-87.61694, 41.86625],
        zoom=15.99,
        pitch=40,
        bearing=20,
        map_options={"canvasContextAttributes": {"antialias": True}},
    )

    m.add_external_script(GEOCODER_SCRIPT)
    m.add_on_load_js(GEOCODER_JS)

    html = m.render()

    assert GEOCODER_SCRIPT in html
    assert "MaplibreGeocoder" in html
    assert "forwardGeocode" in html
    assert "Mock forwardGeocode query" in html
    assert '"canvasContextAttributes":{"antialias":true}' in html.replace("\n", "").replace(" ", "")
