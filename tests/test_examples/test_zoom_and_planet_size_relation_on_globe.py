
from maplibreum import Map
from maplibreum.experimental import GlobeInteraction


def test_zoom_and_planet_size_relation_on_globe():
    button_html = '<button id="fly">Go to pole or equator</button>'
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[0, 0],
        zoom=2,
        extra_js=f"document.body.insertAdjacentHTML('beforeend', `{button_html}`)",
    )
    m.set_projection("globe")

    globe_interaction = GlobeInteraction(element_id="fly")
    globe_interaction.add_to(m)

    html = m.render()
    assert '"projection": {"name": "globe"}' in html
    assert "flyToWithGlobeCompensation" in html
    assert "Go to pole or equator" in html
