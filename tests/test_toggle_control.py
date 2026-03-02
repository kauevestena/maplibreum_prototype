import pytest
from maplibreum.controls import ToggleControl

def test_toggle_control_init():
    ctrl = ToggleControl(
        label="My Toggle",
        on_action="alert('On');",
        off_action="alert('Off');",
        initial_state=True,
        position="bottom-right",
    )
    assert ctrl.label == "My Toggle"
    assert ctrl.on_action == "alert('On');"
    assert ctrl.off_action == "alert('Off');"
    assert ctrl.initial_state is True
    assert ctrl.position == "bottom-right"

def test_toggle_control_defaults():
    ctrl = ToggleControl(label="My Toggle")
    assert ctrl.label == "My Toggle"
    assert ctrl.on_action is None
    assert ctrl.off_action is None
    assert ctrl.initial_state is False
    assert ctrl.position == "top-left"

def test_toggle_control_to_dict():
    ctrl = ToggleControl(
        label="My Toggle",
        on_action="alert('On');",
        off_action="alert('Off');",
        initial_state=True,
        position="bottom-right",
    )
    d = ctrl.to_dict()
    assert d["label"] == "My Toggle"
    assert d["on_action"] == "alert('On');"
    assert d["off_action"] == "alert('Off');"
    assert d["initial_state"] is True
    assert d["position"] == "bottom-right"
