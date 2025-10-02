"""Parity test for the navigate-the-map-with-game-like-controls example."""

from __future__ import annotations

import textwrap

from maplibreum.core import Map


def test_navigate_the_map_with_game_like_controls() -> None:
    """Register keyboard interactions that pan or rotate the map."""

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/liberty",
        center=[-87.6298, 41.8781],
        zoom=19,
        bearing=-12,
        pitch=60,
        map_options={"interactive": False},
    )

    control_js = textwrap.dedent(
        """
        var canvas = map.getCanvas();
        if (!canvas) { return; }
        if (!canvas.hasAttribute('tabindex')) {
            canvas.setAttribute('tabindex', '0');
        }
        canvas.focus();

        var deltaDistance = 100;
        var deltaDegrees = 25;

        function easing(t) {
            return t * (2 - t);
        }

        canvas.addEventListener('keydown', function(e) {
            e.preventDefault();
            if (e.which === 38) {
                map.panBy([0, -deltaDistance], { easing: easing });
            } else if (e.which === 40) {
                map.panBy([0, deltaDistance], { easing: easing });
            } else if (e.which === 37) {
                map.easeTo({ bearing: map.getBearing() - deltaDegrees, easing: easing });
            } else if (e.which === 39) {
                map.easeTo({ bearing: map.getBearing() + deltaDegrees, easing: easing });
            }
        }, true);
        """
    ).strip()

    map_instance.add_on_load_js(control_js)

    assert map_instance.center == [-87.6298, 41.8781]
    assert map_instance.zoom == 19
    assert map_instance.bearing == -12
    assert map_instance.pitch == 60
    assert map_instance.additional_map_options["interactive"] is False

    html = map_instance.render()
    assert "deltaDistance = 100" in html
    assert "map.panBy([0, -deltaDistance]" in html
    assert "map.easeTo({ bearing: map.getBearing() - deltaDegrees" in html


def test_navigate_the_map_with_game_like_controls_with_python_api() -> None:
    """Validate the Map.add_keyboard_navigation() method."""
    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/liberty",
        center=[-87.6298, 41.8781],
        zoom=19,
        bearing=-12,
        pitch=60,
        map_options={"interactive": False},
    )

    map_instance.add_keyboard_navigation(pan_distance=150, rotate_degrees=30)
    html = map_instance.render()
    assert "deltaDistance = 150" in html
    assert "deltaDegrees = 30" in html
    assert "map.panBy([0, -deltaDistance]" in html
    assert "map.easeTo({ bearing: map.getBearing() - deltaDegrees" in html
