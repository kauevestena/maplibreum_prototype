"""Test for the hash-routing MapLibre example."""

from maplibreum.core import Map


def test_enable_hash_routing():
    """Enable the hash flag so the URL reflects map position."""
    m = Map(map_options={"hash": True})

    html = m.render()
    assert '"hash": true' in html
