"""Tests for TextFilterControl."""
import pytest

from maplibreum import Map
from maplibreum.controls import TextFilterControl


def test_text_filter_control_init():
    ctrl = TextFilterControl(
        layer_ids=["layer-a", "layer-b"],
        placeholder="Search...",
        position="top-left",
        match_mode="startswith",
    )
    assert ctrl.layer_ids == ["layer-a", "layer-b"]
    assert ctrl.placeholder == "Search..."
    assert ctrl.position == "top-left"
    assert ctrl.match_mode == "startswith"

    d = ctrl.to_dict()
    assert d["layer_ids"] == ["layer-a", "layer-b"]
    assert d["placeholder"] == "Search..."
    assert d["position"] == "top-left"
    assert d["match_mode"] == "startswith"
    assert "id" in d


def test_text_filter_control_defaults():
    ctrl = TextFilterControl(layer_ids=["my-layer"])
    assert ctrl.placeholder == "Filter by name"
    assert ctrl.position == "top-right"
    assert ctrl.match_mode == "contains"


def test_text_filter_control_rendering():
    m = Map()
    ctrl = TextFilterControl(
        layer_ids=["poi-bar", "poi-music"],
        placeholder="Filter by name",
        position="top-right",
        match_mode="contains",
    )
    m.add_control(ctrl)

    html = m.render()
    assert "maplibreum-text-filter" in html
    assert "Filter by name" in html
    assert "map.setLayoutProperty" in html
    assert "poi-bar" in html
    assert "poi-music" in html
    assert "contains" in html
