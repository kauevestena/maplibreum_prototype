import pytest
from maplibreum.core import Map


def test_render_includes_pitch_and_bearing():
    m = Map(pitch=45, bearing=90)
    html = m.render()
    assert '"pitch": 45' in html
    assert '"bearing": 90' in html
