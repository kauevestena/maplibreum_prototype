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

    js_code = f"""
    const map = {m.map_id};

    function getZoomAdjustment(oldLatitude, newLatitude) {{
        return Math.log2(Math.cos(newLatitude / 180 * Math.PI) / Math.cos(oldLatitude / 180 * Math.PI));
    }}

    let zoomIn = false;
    const zoomDelta = 1.5;

    document.getElementById('fly').addEventListener('click', () => {{
        const center = [
            map.getCenter().lng,
            zoomIn ? 0 : 80,
        ];
        const mapZoom = map.getZoom();
        const delta = (zoomIn ? zoomDelta : -zoomDelta);
        const zoom = map.getZoom() + delta + getZoomAdjustment(map.getCenter().lat, center[1]);
        map.flyTo({{
            center,
            zoom,
            essential: true
        }});
        zoomIn = !zoomIn;
    }});
    """

    m.add_on_load_js(js_code)
    html = m.render()
    assert '"projection": "globe"' in html
    assert "const map =" in html
    assert "Go to pole or equator" in html


def test_zoom_and_planet_size_relation_on_globe_with_python_api():
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
    assert '"projection": "globe"' in html
    assert "flyToWithGlobeCompensation" in html
    assert "Go to pole or equator" in html