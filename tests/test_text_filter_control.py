import pytest
from maplibreum.core import Map
from maplibreum.controls import TextFilterControl

def test_text_filter_control_init():
    layer_ids = ["layer1", "layer2"]
    placeholder = "Search..."
    position = "top-left"
    match_mode = "startswith"

    control = TextFilterControl(
        layer_ids=layer_ids,
        placeholder=placeholder,
        position=position,
        match_mode=match_mode
    )

    assert control.layer_ids == layer_ids
    assert control.placeholder == placeholder
    assert control.position == position
    assert control.match_mode == match_mode
    assert control.id.startswith("text_filter_")

    d = control.to_dict()
    assert d["layer_ids"] == layer_ids
    assert d["placeholder"] == placeholder
    assert d["position"] == position
    assert d["match_mode"] == match_mode
    assert d["id"] == control.id

def test_text_filter_control_rendering():
    m = Map()
    layer_ids = ["test-layer"]
    control = TextFilterControl(layer_ids=layer_ids)
    m.add_control(control)

    # Verify it is registered in m.controls
    registered_control = next(c for c in m.controls if c["type"] == "textfilter")
    assert registered_control["options"]["layer_ids"] == layer_ids

    # Verify rendering
    html = m.render()
    assert "maplibreum-text-filter" in html
    assert '["test-layer"]' in html
    assert "contains" in html  # Default match_mode
