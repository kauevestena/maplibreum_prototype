"""Test for fit-a-map-to-a-bounding-box MapLibre example."""

import pytest

from maplibreum.core import Map


def test_fit_a_map_to_a_bounding_box():
    """Test recreating the 'fit-a-map-to-a-bounding-box' MapLibre example.

    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://tiles.openfreemap.org/styles/bright',
        center: [-74.5, 40],
        zoom: 9
    });

    document.getElementById('fit').addEventListener('click', () => {
        map.fitBounds([
            [32.958984, -5.353521],
            [43.50585, 5.615985]
        ]);
    });
    ```
    """

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-74.5, 40],
        zoom=9,
    )

    kenya_bounds = [[32.958984, -5.353521], [43.50585, 5.615985]]
    m.fit_bounds(kenya_bounds)

    assert m.center == [-74.5, 40]
    assert m.zoom == pytest.approx(9)
    assert m.bounds == kenya_bounds
    assert m.bounds_padding is None

    html = m.render()
    assert "map.fitBounds([[32.958984, -5.353521], [43.50585, 5.615985]])" in html
    assert "tiles.openfreemap.org/styles/bright" in html
