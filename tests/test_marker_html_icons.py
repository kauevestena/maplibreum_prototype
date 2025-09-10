from maplibreum import Map, Marker, DivIcon, BeautifyIcon


def test_div_icon_marker_renders_html_and_css():
    m = Map()
    icon = DivIcon(html="<b>Hello</b>", class_name="my-div-icon")
    Marker(coordinates=[0, 0], icon=icon).add_to(m)

    html = m.render()
    assert "<b>Hello</b>" in html
    assert "my-div-icon" in html
    # CSS should be injected
    assert ".maplibreum-div-icon" in html


def test_beautify_icon_injects_html_and_css():
    m = Map()
    icon = BeautifyIcon(icon="star", background_color="red", text_color="white", border_color="black")
    Marker(coordinates=[1, 1], icon=icon).add_to(m)

    html = m.render()
    assert "beautify-marker" in html
    assert "background-color:red" in html
    assert "star" in html
