from maplibreum.core import Map


def test_repr_html_returns_iframe():
    m = Map()
    html = m._repr_html_()

    assert html.strip().startswith("<iframe")
    assert "srcdoc=" in html
    assert f'id="{m.map_id}_iframe"' in html
