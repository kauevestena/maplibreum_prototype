from maplibreum import Map
from maplibreum.deckgl import DeckGLLayer
from maplibreum.datasources import RESTDataSource


DECKGL_SCRIPT = "https://unpkg.com/deck.gl@8.9.33/dist.min.js"


FETCH_JS = """
map.addControl(new maplibregl.NavigationControl(), 'top-right');
const colorPalette = [
    [255, 102, 51],
    [255, 179, 153],
    [255, 51, 255],
    [255, 255, 153],
    [0, 179, 230],
    [230, 179, 51],
    [51, 102, 230],
    [153, 153, 102],
    [153, 255, 153],
    [179, 77, 77],
    [128, 179, 0],
    [128, 153, 0],
    [230, 179, 179],
    [102, 128, 179],
    [102, 153, 26],
    [255, 153, 230],
    [204, 255, 26],
    [255, 26, 102],
    [230, 51, 26],
    [51, 255, 204],
    [102, 153, 77],
];
const limit = 100;
const parisSights = `https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/principaux-sites-touristiques-en-ile-de-france0/records?limit=${limit}`;
map.on('load', async () => {
    const response = await fetch(parisSights);
    const responseJSON = await response.json();
    const layer = new deck.ScatterplotLayer({
        id: 'scatterplot-layer',
        data: responseJSON.results,
        pickable: true,
        opacity: 0.7,
        stroked: true,
        filled: true,
        radiusMinPixels: 14,
        radiusMaxPixels: 100,
        lineWidthMinPixels: 5,
        getPosition: (d) => [d.geo_point_2d.lon, d.geo_point_2d.lat],
        getFillColor: (d) => {
            if ('insee' in d && d.insee.startsWith('75')) {
                return colorPalette[parseInt(d.insee.substring(3))];
            }
            return colorPalette[20];
        },
        getLineColor: (d) => [14, 16, 255],
        onClick: (info) => {
            const { coordinate, object } = info;
            const description = `<p>${object.nom_carto || 'Unknown'}</p>`;
            new maplibregl.Popup().setLngLat(coordinate).setHTML(description).addTo(map);
        },
    });
    const overlay = new deck.MapboxOverlay({ layers: [layer] });
    map.addControl(overlay);
});
"""


def test_create_deckgl_layer_using_rest_api():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/liberty",
        center=[2.343957, 48.862011],
        zoom=10.5,
    )

    m.add_external_script(DECKGL_SCRIPT)
    m.add_on_load_js(FETCH_JS)

    html = m.render()

    assert DECKGL_SCRIPT in html
    assert "ScatterplotLayer" in html
    assert "MapboxOverlay" in html
    assert "fetch(parisSights)" in html
    assert "map.addControl(overlay)" in html
    assert '"style": "https://tiles.openfreemap.org/styles/liberty"' in html.replace("\n", "")
    assert '"center": [2.343957, 48.862011]' in html
    assert '"zoom": 10.5' in html


def test_create_deckgl_layer_using_rest_api_with_python_api():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/liberty",
        center=[2.343957, 48.862011],
        zoom=10.5,
    )

    color_palette = [
        [255, 102, 51], [255, 179, 153], [255, 51, 255], [255, 255, 153],
        [0, 179, 230], [230, 179, 51], [51, 102, 230], [153, 153, 102],
        [153, 255, 153], [179, 77, 77], [128, 179, 0], [128, 153, 0],
        [230, 179, 179], [102, 128, 179], [102, 153, 26], [255, 153, 230],
        [204, 255, 26], [255, 26, 102], [230, 51, 26], [51, 255, 204],
        [102, 153, 77],
    ]

    get_fill_color_js = f"""d => {{
        const colorPalette = {color_palette};
        if ('insee' in d && d.insee.startsWith('75')) {{
            return colorPalette[parseInt(d.insee.substring(3))];
        }}
        return colorPalette[20];
    }}"""

    on_click_js = """info => {
        const { coordinate, object } = info;
        const description = `<p>${object.nom_carto || 'Unknown'}</p>`;
        new maplibregl.Popup().setLngLat(coordinate).setHTML(description).addTo(map);
    }"""

    limit = 100
    paris_sights = f"https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/principaux-sites-touristiques-en-ile-de-france0/records?limit={limit}"
    deckgl_layer = DeckGLLayer(
        id="deckgl-layer",
        data=RESTDataSource(paris_sights),
        data_accessor=".results",
        layer_type="ScatterplotLayer",
        pickable=True,
        opacity=0.7,
        stroked=True,
        filled=True,
        radius_min_pixels=14,
        radius_max_pixels=100,
        line_width_min_pixels=5,
        get_position="d => [d.geo_point_2d.lon, d.geo_point_2d.lat]",
        get_fill_color=get_fill_color_js,
        get_line_color=[14, 16, 255],
        on_click=on_click_js,
    )

    m.add_layer(deckgl_layer)
    html = m.render()

    assert DECKGL_SCRIPT in html
    assert '"layerType": "ScatterplotLayer"' in html
    assert "fetch('https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/principaux-sites-touristiques-en-ile-de-france0/records?limit=100')" in html
    assert ".then(data => data.results)" in html
    assert "getFillColor" in html
    assert "onClick" in html
    assert "map.addControl(overlay)" not in html
