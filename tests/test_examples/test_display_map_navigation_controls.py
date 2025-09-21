"""Test for display-map-navigation-controls MapLibre example."""

import pytest

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

    control_options = {
        "visualizePitch": True,
        "visualizeRoll": True,
        "showZoom": True,
        "showCompass": True,
    }

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-74.5, 40],
        zoom=2,
        map_options={"rollEnabled": True},
    )

    m.add_control("navigation", position="top-right", options=control_options)

    assert m.center[0] == pytest.approx(-74.5)
    assert m.center[1] == pytest.approx(40)
    assert m.zoom == pytest.approx(2)
    assert m.map_style == "https://demotiles.maplibre.org/style.json"
    assert m.additional_map_options["rollEnabled"] is True

    assert len(m.controls) == 1
    nav_control = m.controls[0]
    assert nav_control["type"] == "navigation"
    assert nav_control["position"] == "top-right"
    assert nav_control["options"] == control_options

    html = m.render()
    assert "rollEnabled" in html
    for option_key in control_options:
        assert option_key in html

