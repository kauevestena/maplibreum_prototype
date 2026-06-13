"""Parity test for the navigate-the-map-with-game-like-controls example."""

from __future__ import annotations

import textwrap

from maplibreum.core import Map


def test_navigate_the_map_with_game_like_controls() -> None:
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
