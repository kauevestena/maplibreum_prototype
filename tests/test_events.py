import json

from maplibreum import Map


def test_on_click_event_registration():
    m = Map()
    received = {}

    def cb(data):
        received["data"] = data

    m.on_click(cb)
    html = m.render()
    assert "map.on('click'" in html
    Map._handle_event(m.map_id, "click", json.dumps({"lngLat": {"lng": 1, "lat": 2}}))
    assert received["data"]["lngLat"]["lng"] == 1


def test_on_move_event_registration():
    m = Map()
    received = {}

    def cb(data):
        received.update(data)

    m.on_move(cb)
    html = m.render()
    assert "map.on('move'" in html
    Map._handle_event(m.map_id, "move", json.dumps({"center": {"lng": 4, "lat": 5}}))
    assert received["center"]["lng"] == 4
