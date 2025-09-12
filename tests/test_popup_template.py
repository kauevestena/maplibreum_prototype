import pytest

from maplibreum import Map, Popup


@pytest.fixture
def map_instance():
    return Map()


def test_popup_template_rendering(map_instance):
    map_instance.add_popup(
        template="Hello {{ name }}",
        coordinates=[0, 0],
        context={"name": "<World>"},
    )
    assert map_instance.popups[0]["html"] == "Hello &lt;World&gt;"
    html = map_instance.render()
    assert "Hello &lt;World&gt;" in html
    assert "<World>" not in html


def test_popup_object_render(map_instance):
    tpl = Popup(template="<div>{{ value }}</div>")
    map_instance.add_popup(html=tpl, coordinates=[0, 0], context={"value": "<b>X</b>"})
    assert map_instance.popups[0]["html"] == "<div>&lt;b&gt;X&lt;/b&gt;</div>"
    html = map_instance.render()
    assert "<div>&lt;b&gt;X&lt;/b&gt;</div>" in html
