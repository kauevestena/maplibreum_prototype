import subprocess

from maplibreum.core import Map


def test_camera_actions_serialization():
    m = Map()
    m.fly_to(center=[10, 20], zoom=5)
    m.ease_to(center=[0, 0], zoom=2)
    m.pan_to([1, 2], duration=1000)
    html = m.render()
    assert 'map.flyTo({"center": [10, 20], "zoom": 5});' in html
    assert 'map.easeTo({"center": [0, 0], "zoom": 2});' in html
    assert 'map.panTo([1, 2], {"duration": 1000});' in html


def test_export_png_invokes_cli(monkeypatch, tmp_path):
    m = Map()
    calls = {}

    def fake_run(cmd, check):
        calls["cmd"] = cmd
        calls["check"] = check

    monkeypatch.setattr(subprocess, "run", fake_run)
    output = tmp_path / "map.png"
    m.export_png(str(output), width=800, height=600)

    assert calls["cmd"][0] == "npx"
    assert "@maplibre/maplibre-gl-export" in calls["cmd"]
    assert "--output" in calls["cmd"]
    assert str(output) in calls["cmd"]
