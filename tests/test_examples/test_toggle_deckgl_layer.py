from maplibreum import Map


DECKGL_SCRIPT = "https://unpkg.com/deck.gl@8.9.33/dist.min.js"


TOGGLE_JS = """
const apiUrl = 'https://maps.clockworkmicro.com/streets/v1/style?x-api-key=';
const apiKey = 'Dr4eW3s233rRkk8I_public';
let overlay;
const sampleData = {
    type: 'FeatureCollection',
    features: [
        {
            type: 'Feature',
            properties: { name: 'Jardins du Trocadéro', district: 16 },
            geometry: { type: 'Point', coordinates: [2.289207, 48.861561] },
        },
        {
            type: 'Feature',
            properties: { name: 'Jardin des Plantes', district: 5 },
            geometry: { type: 'Point', coordinates: [2.359823, 48.843995] },
        },
        {
            type: 'Feature',
            properties: { name: 'Jardins das Tulherias', district: 1 },
            geometry: { type: 'Point', coordinates: [2.327092, 48.863608] },
        },
        {
            type: 'Feature',
            properties: { name: 'Parc de Bercy', district: 12 },
            geometry: { type: 'Point', coordinates: [2.382094, 48.835962] },
        },
        {
            type: 'Feature',
            properties: { name: 'Jardin du Luxemburg', district: 6 },
            geometry: { type: 'Point', coordinates: [2.336975, 48.846421] },
        },
    ],
};
function initialiseOverlay() {
    const layer = new deck.ScatterplotLayer({
        id: 'scatterplot-layer',
        data: sampleData.features,
        pickable: true,
        opacity: 0.8,
        stroked: true,
        filled: true,
        radiusScale: 6,
        radiusMinPixels: 20,
        radiusMaxPixels: 100,
        lineWidthMinPixels: 5,
        getPosition: (d) => d.geometry.coordinates,
        getFillColor: () => [49, 130, 206],
        getLineColor: () => [175, 0, 32],
        onClick: (info) => {
            const { coordinate, object } = info;
            const description = `<div><p><strong>Name: </strong>${object.properties.name}</p><p><strong>District: </strong>${object.properties.district}</p></div>`;
            new maplibregl.Popup().setLngLat(coordinate).setHTML(description).addTo(map);
        },
    });
    overlay = new deck.MapboxOverlay({ layers: [layer] });
    map.addControl(overlay);
}
map.on('load', () => {
    initialiseOverlay();
    const toggleButton = document.createElement('button');
    toggleButton.id = 'toggle-button';
    toggleButton.textContent = 'Hide';
    toggleButton.addEventListener('click', () => {
        if (toggleButton.textContent === 'Hide') {
            map.removeControl(overlay);
            toggleButton.textContent = 'Show';
        } else {
            initialiseOverlay();
            toggleButton.textContent = 'Hide';
        }
    });
    map.getContainer().appendChild(toggleButton);
});
"""


def test_toggle_deckgl_layer():
    m = Map(
        map_style="https://maps.clockworkmicro.com/streets/v1/style?x-api-key=Dr4eW3s233rRkk8I_public",
        center=[2.345885, 48.860412],
        zoom=12,
    )

    m.add_external_script(DECKGL_SCRIPT)
    m.add_on_load_js(TOGGLE_JS)

    html = m.render()

    assert DECKGL_SCRIPT in html
    assert "toggleButton" in html
    assert "map.removeControl(overlay)" in html
    assert "initialiseOverlay" in html
    assert '"style": "https://maps.clockworkmicro.com/streets/v1/style?x-api-key=Dr4eW3s233rRkk8I_public"' in html.replace("\n", "")
    assert '"center": [2.345885, 48.860412]' in html
    assert '"zoom": 12' in html
