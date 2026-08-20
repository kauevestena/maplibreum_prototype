"""Regression coverage for APIs added by the OpenSidewalkMap field test."""

import pytest

from maplibreum import Map, StyleSwitcherControl
from maplibreum.controls import PanelControl
from maplibreum.sources import GeoJSONSource


def test_external_es_module_is_loaded_before_map_initialisation():
    map_object = Map()

    result = map_object.add_external_module(
        "https://example.test/module.js",
        "ExampleControl",
        export_name="default",
    )

    assert result == "ExampleControl"
    html = map_object.render()
    assert "await import(definition.src)" in html
    assert '"global_name": "ExampleControl"' in html
    assert '"export_name": "default"' in html
    assert html.index("externalModuleDefinitions") < html.index("initializeMap();")


def test_external_es_module_replaces_a_previous_global_definition():
    map_object = Map()
    map_object.add_external_module("first.js", "Shared")
    map_object.add_external_module("second.js", "Shared", export_name="named")

    assert map_object.external_modules == [
        {"src": "second.js", "global_name": "Shared", "export_name": "named"}
    ]


def test_external_stylesheet_is_deduplicated_and_renders_attributes():
    map_object = Map()
    map_object.add_external_stylesheet("https://example.test/app.css", media="screen")
    map_object.add_external_stylesheet(
        "https://example.test/app.css", crossorigin="anonymous", disabled=False
    )

    assert map_object.external_stylesheets == [
        {
            "href": "https://example.test/app.css",
            "attributes": {"crossorigin": "anonymous", "disabled": False},
        }
    ]
    html = map_object.render()
    assert html.count('href="https://example.test/app.css"') == 1
    assert 'crossorigin="anonymous"' in html
    assert " disabled" not in html


@pytest.mark.parametrize("global_name", ["not-valid", "two words", "2startsWrong"])
def test_external_es_module_validates_global_name(global_name):
    with pytest.raises(ValueError, match="JavaScript identifier"):
        Map().add_external_module("module.js", global_name)


def test_style_switcher_renders_labels_and_waits_for_style_load():
    control = StyleSwitcherControl(
        {"access": "access.json", "surface": {"version": 8, "sources": {}, "layers": []}},
        labels={"access": "Accessibility", "surface": "Surface"},
        initial_style="access",
        control_id="style-choice",
    )
    map_object = Map()
    map_object.add_control(control, "top-left")

    html = map_object.render()
    assert "style-choice" in html
    assert "Accessibility" in html
    assert "controlMap.once('style.load'" in html
    assert "maplibreum-style-change" in html


def test_style_switcher_rejects_inconsistent_configuration():
    with pytest.raises(ValueError, match="non-empty mapping"):
        StyleSwitcherControl({})
    with pytest.raises(ValueError, match="unknown style keys"):
        StyleSwitcherControl({"one": "one.json"}, labels={"two": "Two"})
    with pytest.raises(ValueError, match="initial_style"):
        StyleSwitcherControl({"one": "one.json"}, initial_style="two")


def test_structured_feature_popup_renders_fields_links_and_missing_value():
    map_object = Map()
    map_object.add_feature_popup(
        "sidewalks",
        ["surface", "width"],
        aliases=["Surface", "Width"],
        title="Way {osm_id}",
        links=[
            {
                "label": "OpenStreetMap",
                "url": "https://www.openstreetmap.org/way/{osm_id}",
            }
        ],
        missing="not mapped",
    )

    html = map_object.render()
    assert '"layer_id": "sidewalks"' in html
    assert '"alias": "Surface"' in html
    assert "Way {osm_id}" in html
    assert "www.openstreetmap.org/way/{osm_id}" in html
    assert "not mapped" in html
    assert "DOMPurify.sanitize(content)" in html


def test_structured_feature_popup_validates_fields_and_aliases():
    with pytest.raises(ValueError, match="at least one"):
        Map().add_feature_popup("layer", [])
    with pytest.raises(ValueError, match="same length"):
        Map().add_feature_popup("layer", ["one", "two"], aliases=["One"])
    with pytest.raises(ValueError, match="label and url"):
        Map().add_feature_popup("layer", ["one"], links=[{"label": "Missing URL"}])


def test_feature_state_hover_tracks_vector_source_layer_and_clears_state():
    map_object = Map()
    state_key = map_object.add_feature_state_hover(
        "main-footways",
        "footways-source",
        source_layer="main_footways",
    )

    assert state_key == "footways-source:main_footways:main-footways:hover"
    assert [binding.event for binding in map_object.event_bindings] == [
        "mousemove",
        "mouseleave",
    ]
    html = map_object.render()
    assert 'const nextSourceLayer = "main_footways" || feature.sourceLayer;' in html
    assert 'const previousTarget = {source: "footways-source", id: previous.id};' in html
    assert 'map.setFeatureState(nextTarget, {["hover"]: true});' in html
    assert "delete map.__maplibreumHoverStates[hoverKey]" in html


def test_panel_control_json_encodes_html_instead_of_using_template_literal():
    payload = "<p>` ${alert('not executable')}</p>"
    map_object = Map()
    panel = PanelControl(html_content=payload)
    map_object.add_control(panel)

    html = map_object.render()
    assert "overlay.innerHTML = `" not in html
    assert "overlay.innerHTML = \"<p>` ${alert('not executable')}</p>\";" in html
    assert "setTimeout" not in panel.to_js()


def test_original_source_definition_is_available_without_duplicate_serialisation():
    source_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1, 2]},
                "properties": {"sentinel": "large-source-value"},
            }
        ],
    }
    map_object = Map()
    map_object.add_source("measurements", GeoJSONSource(source_data))

    html = map_object.render()
    assert 'map.addSource("measurements"' in html
    assert 'map.__maplibreumSourceDefinitions["measurements"]' in html
    assert html.count("large-source-value") == 1


def test_page_elements_can_frame_the_map_for_dashboard_layouts():
    map_object = Map(container_id="dashboard-map")
    assert map_object.add_page_element("<header>Dashboard</header>", before_map=True) == 0
    assert map_object.add_page_element("<aside>Status</aside>") == 0

    html = map_object.render()
    assert html.index("<header>Dashboard</header>") < html.index('id="dashboard-map"')
    assert html.index("<aside>Status</aside>") > html.index('id="dashboard-map"')
    with pytest.raises(TypeError, match="must be a string"):
        map_object.add_page_element({"not": "html"})
