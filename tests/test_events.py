import json

import pytest

from maplibreum import Map, StateToggle


def test_on_click_event_registration():
    m = Map()
    received = {}

    def cb(data):
        received["data"] = data

    binding_id = m.on_click(cb)
    html = m.render()
    assert binding_id == "click"
    assert "map.on('click'" in html
    Map._handle_event(m.map_id, "click", json.dumps({"lngLat": {"lng": 1, "lat": 2}}))
    assert received["data"]["lngLat"]["lng"] == 1


def test_on_move_event_registration():
    m = Map()
    received = {}

    def cb(data):
        received.update(data)

    binding_id = m.on_move(cb)
    html = m.render()
    assert binding_id == "move"
    assert "map.on('move'" in html
    Map._handle_event(m.map_id, "move", json.dumps({"center": {"lng": 4, "lat": 5}}))
    assert received["center"]["lng"] == 4


def test_layer_bound_event_with_js_and_toggle():
    m = Map()
    calls = []

    def cb(data):
        calls.append(data)

    binding_id = m.on(
        "mouseenter",
        cb,
        layer_id="cities",
        js="map.setPaintProperty('cities', 'circle-opacity', 0.5);",
        state_toggles=[StateToggle(selector="#status", class_name="is-hovering")],
    )

    html = m.render()
    assert binding_id == "mouseenter@cities"
    assert "map.on('mouseenter', 'cities'" in html
    assert "Map._handle_event('" in html and "mouseenter@cities" in html
    assert "setPaintProperty('cities', 'circle-opacity', 0.5)" in html
    assert "classList.toggle" in html
    Map._handle_event(m.map_id, binding_id, json.dumps({"center": {"lng": 0, "lat": 0}}))
    assert calls and calls[0]["center"]["lng"] == 0


def test_add_event_listener_generates_toggle_script():
    m = Map()
    event_id = m.add_event_listener(
        "click",
        js="console.log('clicked');",
        state_toggles=[{"selector": "#panel", "attribute": "data-open", "state": False}],
        once=True,
    )

    html = m.render()
    assert event_id == "click"
    assert "console.log('clicked');" in html
    assert '"attribute": "data-open"' in html
    assert "target.removeAttribute(tgl.attribute)" in html
    assert "map.off('click'" in html


def test_state_toggle_serialisation_and_validation():
    toggle = StateToggle(selector="#panel", dataset={"active": True}, text="Open")
    data = toggle.to_dict()
    assert data["dataset"]["active"] == "True"
    assert data["text"] == "Open"

    with pytest.raises(ValueError):
        StateToggle(selector="#panel")
