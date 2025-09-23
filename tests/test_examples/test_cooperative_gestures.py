"""Test for the cooperative-gestures MapLibre example."""

from maplibreum.core import Map


def test_cooperative_gestures_locale_support():
    """Enable cooperative gestures with localized helper copy."""
    locale_overrides = {
        "CooperativeGesturesHandler.WindowsHelpText": (
            "Use Ctrl + scroll to zoom the map."
        ),
        "CooperativeGesturesHandler.MacHelpText": (
            "Use ⌘ + scroll to zoom the map."
        ),
        "CooperativeGesturesHandler.MobileHelpText": (
            "Use two fingers to move the map."
        ),
    }

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-74.5, 40.0],
        zoom=4,
        map_options={"locale": locale_overrides},
    )
    m.set_mobile_behavior(cooperative_gestures=True)
    m.add_control("fullscreen")

    html = m.render()
    assert '"cooperativeGestures": true' in html
    assert "CooperativeGesturesHandler.WindowsHelpText" in html
    assert "map.addControl(new maplibregl.FullscreenControl()" in html
