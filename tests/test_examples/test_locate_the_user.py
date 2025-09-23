"""Test for the locate-the-user MapLibre example."""

from maplibreum.core import Map


def test_locate_the_user_geolocate_control():
    """Add a geolocate control with high-accuracy tracking enabled."""
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-96.0, 37.8],
        zoom=3,
    )
    m.add_control(
        "geolocate",
        position="top-left",
        options={
            "positionOptions": {"enableHighAccuracy": True},
            "trackUserLocation": True,
        },
    )

    html = m.render()
    assert "maplibregl.GeolocateControl" in html
    assert '"enableHighAccuracy": true' in html
    assert '"trackUserLocation": true' in html
