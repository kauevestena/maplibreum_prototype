"""Parity test for the restrict-map-panning-to-an-area example."""

from __future__ import annotations

from maplibreum.core import Map


def test_restrict_map_panning_to_an_area() -> None:
    """Configure a map with max bounds covering New York City."""

    bounds = [
        [-74.04728500751165, 40.68392799015035],
        [-73.91058699000139, 40.87764500765852],
    ]

    map_instance = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-73.9978, 40.7209],
        zoom=13,
        map_options={"maxBounds": bounds},
    )

    assert map_instance.center == [-73.9978, 40.7209]
    assert map_instance.zoom == 13
    assert map_instance.additional_map_options["maxBounds"] == bounds

    html = map_instance.render()
    assert "maxBounds" in html
    assert "-74.04728500751165" in html
