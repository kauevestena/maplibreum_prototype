import pytest
from maplibreum.core import Map
from maplibreum.controls import ButtonControl

def test_button_control_init():
    label = "Click Me"
    action = "alert('hi')"
    position = "top-right"
    css_class = "my-btn"
    style = {"color": "red"}
    onclick_js = "console.log('click')"

    control = ButtonControl(
        label=label,
        action=action,
        position=position,
        css_class=css_class,
        style=style,
        onclick_js=onclick_js
    )

    assert control.label == label
    assert control.action == action
    assert control.position == position
    assert control.css_class == css_class
    assert control.style == style
    assert control.onclick_js == onclick_js
    assert control.id.startswith("button_")

def test_button_control_to_dict():
    label = "Click Me"
    control = ButtonControl(label=label)
    d = control.to_dict()

    assert d["label"] == label
    assert d["id"] == control.id
    assert "action" in d
    assert "position" in d
    assert "css_class" in d
    assert "style" in d
    assert "onclick_js" in d

def test_add_button_control_to_map():
    m = Map()
    control = ButtonControl(label="Test Button")
    m.add_control(control)

    assert len(m.controls) == 1
    entry = m.controls[0]
    assert entry["type"] == "button"
    assert entry["options"]["label"] == "Test Button"

def test_map_add_button_control_helper():
    m = Map()
    control = m.add_button_control(
        label="Helper Button",
        action="alert('helper')",
        position="bottom-right"
    )

    assert isinstance(control, ButtonControl)
    assert len(m.controls) == 1
    assert m.controls[0]["type"] == "button"
    assert m.controls[0]["options"]["label"] == "Helper Button"
    assert m.controls[0]["position"] == "bottom-right"

def test_button_control_rendering():
    m = Map()
    label = "RenderedButton"
    css_class = "unique-css-class"
    style = {"color": "red", "font-weight": "bold"}
    onclick_js = "alert('clicked')"

    # Use ButtonControl directly to ensure onclick_js is passed,
    # as add_button_control helper might not support all arguments.
    control = ButtonControl(
        label=label,
        action=None,
        position="top-left",
        css_class=css_class,
        style=style,
        onclick_js=onclick_js
    )
    m.add_control(control)

    html = m.render()

    # Verify values are present in the HTML
    assert label in html
    assert css_class in html
    # Check style properties - the template uses: buttonEl.style.{{ key }} = '{{ value }}'
    assert "buttonEl.style.color = 'red'" in html
    assert "buttonEl.style.font-weight = 'bold'" in html
    assert onclick_js in html
