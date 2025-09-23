"""Test for the display-a-non-interactive-map MapLibre example."""

from maplibreum.core import Map


def test_display_a_non_interactive_map():
    """Disable all user interactivity using the constructor flag."""
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[74.5, 40.0],
        zoom=3,
        map_options={"interactive": False},
    )

    html = m.render()
    assert '"interactive": false' in html
