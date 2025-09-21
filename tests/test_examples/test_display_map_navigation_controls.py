"""Test for display-map-navigation-controls MapLibre example."""

import pytest

from maplibreum import controls
from maplibreum.core import Map


def test_display_map_navigation_controls():
    """Test recreating the 'display-map-navigation-controls' MapLibre example.

    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [-74.5, 40],
        zoom: 2,
        rollEnabled: true
    });

    map.addControl(new maplibregl.NavigationControl({
        visualizePitch: true,
        visualizeRoll: true,
        showZoom: true,
        showCompass: true
    }));
    ```
    """

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-74.5, 40],
        zoom=2,
        map_options={"rollEnabled": True},
    )

    nav_control = controls.NavigationControl(
        visualizePitch=True,
        showZoom=True,
        showCompass=True,
    )
    nav_control.options["visualizeRoll"] = True
    expected_options = dict(nav_control.to_dict())

    m.add_control(nav_control, position="top-right")

    assert m.center[0] == pytest.approx(-74.5)
    assert m.center[1] == pytest.approx(40)
    assert m.zoom == pytest.approx(2)
    assert m.map_style == "https://demotiles.maplibre.org/style.json"
    assert m.additional_map_options["rollEnabled"] is True

    assert len(m.controls) == 1
    nav_control = m.controls[0]
    assert nav_control["type"] == "navigation"
    assert nav_control["position"] == "top-right"
    assert nav_control["options"] == expected_options

    html = m.render()
    assert "rollEnabled" in html
    for option_key in expected_options:
        assert option_key in html

