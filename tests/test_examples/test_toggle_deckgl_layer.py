from maplibreum.controls import DeckGLLayerToggle
from maplibreum.core import Map
from maplibreum.deckgl import DeckGLLayer


DECKGL_SCRIPT = "https://unpkg.com/deck.gl@8.9.33/dist.min.js"


SAMPLE_DATA = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Jardins du Trocadéro", "district": 16},
            "geometry": {"type": "Point", "coordinates": [2.289207, 48.861561]},
        },
        {
            "type": "Feature",
            "properties": {"name": "Jardin des Plantes", "district": 5},
            "geometry": {"type": "Point", "coordinates": [2.359823, 48.843995]},
        },
        {
            "type": "Feature",
            "properties": {"name": "Jardins des Tuileries", "district": 1},
            "geometry": {"type": "Point", "coordinates": [2.327092, 48.863608]},
        },
        {
            "type": "Feature",
            "properties": {"name": "Parc de Bercy", "district": 12},
            "geometry": {"type": "Point", "coordinates": [2.382094, 48.835962]},
        },
        {
            "type": "Feature",
            "properties": {"name": "Jardin du Luxemburg", "district": 6},
            "geometry": {"type": "Point", "coordinates": [2.336975, 48.846421]},
        },
    ],
}


def test_toggle_deckgl_layer():
    layer = DeckGLLayer(
        id="paris-parks",
        data=SAMPLE_DATA,
        layer_type="ScatterplotLayer",
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=6,
        radius_min_pixels=20,
        radius_max_pixels=100,
        line_width_min_pixels=5,
        get_position="d => d.geometry.coordinates",
        get_fill_color="() => [49, 130, 206]",
        get_line_color="() => [175, 0, 32]",
        on_click=(
            "info => { const { coordinate, object } = info;"
            " const content = `<div><p><strong>Name: </strong>${object.properties.name}</p>"
            "<p><strong>District: </strong>${object.properties.district}</p></div>`;"
            " new maplibregl.Popup().setLngLat(coordinate).setHTML(content).addTo(map); }"
        ),
    )

    m = Map(
        map_style="https://maps.clockworkmicro.com/streets/v1/style?x-api-key=Dr4eW3s233rRkk8I_public",
        center=[2.345885, 48.860412],
        zoom=12,
    )

    layer_id = m.add_layer(layer)
    assert layer_id == "paris-parks"
    assert any(ov["id"] == layer_id for ov in m.deckgl_overlays)

    toggle = DeckGLLayerToggle(layer_id=layer_id, label="Deck.GL Parks", initial_state=True)
    m.add_control(toggle, position="top-left")

    html = m.render()

    assert DECKGL_SCRIPT in html
    assert "MaplibreumDeckGLOverlayManager" in html
    assert "window.maplibreumDeckOverlayManagers" in html
    assert "map.__deckOverlayManager" in html
    assert 'overlayManager.addOverlay("paris-parks")' in html
    assert 'overlayManager.removeOverlay("paris-parks")' in html
    assert "Deck.GL Parks" in html
    assert '"style": "https://maps.clockworkmicro.com/streets/v1/style?x-api-key=Dr4eW3s233rRkk8I_public"' in html.replace("\n", "")
    assert '"center": [2.345885, 48.860412]' in html
    assert '"zoom": 12' in html
