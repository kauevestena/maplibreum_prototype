"""Contract tests for the OpenSidewalkMap production field-test builders."""

from examples.opensidewalkmap.acquisition import build_map as build_acquisition
from examples.opensidewalkmap.completeness import (
    build_map as build_completeness,
    completeness_to_geojson,
)
from examples.opensidewalkmap.hazard_analysis import build_map as build_hazard
from examples.opensidewalkmap.main_webmap import build_map as build_main
from examples.opensidewalkmap.routing import build_map as build_routing


EMPTY_STYLE = {"version": 8, "sources": {}, "layers": []}


def test_main_webmap_reproduces_styles_pmtiles_hover_popups_and_native_modules():
    params = {
        "bounds": [-49.4, -25.7, -49.1, -25.3],
        "center": [-49.25, -25.5],
        "zoom": 13,
        "node_url": "https://example.test/node/",
        "styles": {
            "footway_categories": {**EMPTY_STYLE, "name": "Footways"},
            "surface": {**EMPTY_STYLE, "name": "Surface"},
        },
        "data_layers": ["sidewalks"],
        "layer_types": {"line": ["sidewalks"]},
        "legend_fragments": {
            "footway_categories": "<p>Footway legend</p>",
            "surface": "<p>Surface legend</p>",
        },
        "snapshot": {},
        "theme_charts": {},
    }

    map_object = build_main(params)
    html = map_object.render()

    assert map_object.bounds == params["bounds"]
    assert "pmtiles@4.5.0" in html
    assert "oswm-style-selector" in html
    assert "OswmLegendControl" in html
    assert "installThemeChartControl" in html
    assert "installSnapshotControl" in html
    assert {binding.id for binding in map_object.event_bindings} >= {
        "feature-state-hover:sidewalks:move",
        "feature-state-hover:sidewalks:leave",
    }
    assert "See on OpenStreetMap" in html
    assert "Footway legend" in html


def test_routing_builder_uses_python_sources_layers_terrain_and_pathfinding_modules():
    map_object = build_routing(
        data_url="https://example.test/routing.geojson",
        profiles_url="https://example.test/profiles.json",
    )
    html = map_object.render()

    assert {source["name"] for source in map_object.sources} == {
        "aws-terrain",
        "line",
        "boundaries",
    }
    assert {layer["id"] for layer in map_object.layers} == {
        "hills",
        "line-layer",
        "boundary-layer",
    }
    assert map_object.terrain == {"source": "aws-terrain", "exaggeration": 1.2}
    assert "geojson-path-finder@2.1.0" in html
    assert "profileWeight" in html
    assert "distance-comparison-path-layer" in html
    assert "nearestNetworkPoint" in html


def hazard_profiles_fixture():
    return {
        "profiles": {
            "wheelchair": {
                "label": "Wheelchair",
                "description": "Wheelchair screening",
            },
            "blind": {"label": "Blind", "description": "Blind screening"},
        },
        "categories": {"surface": {"label": "Surface"}},
        "severity_levels": {
            "0": {"label": "No detected hazard", "color": "#fff"},
            "1": {"label": "Uncomfortable", "color": "#fee08b"},
            "4": {"label": "Critical", "color": "#a50026"},
        },
        "rules": [
            {
                "id": "surface_bad",
                "category": "surface",
                "description": "Difficult surface",
                "effects": {"wheelchair": {"severity": 4}, "blind": {"severity": 1}},
            }
        ],
    }


def hazard_terrain_fixture():
    return {
        "available": True,
        "bounds": [-49.4, -25.7, -49.1, -25.3],
        "coordinates": [[-49.4, -25.3], [-49.1, -25.3], [-49.1, -25.7], [-49.4, -25.7]],
        "description": "Contextual terrain potential.",
        "source_attribution": "Terrain provider",
        "profiles": {
            "wheelchair": {"path": "terrain-wheelchair.png"},
            "blind": {"path": "terrain-blind.png"},
        },
    }


def test_hazard_builder_reproduces_dynamic_profiles_filters_terrain_and_evidence_popup():
    map_object = build_hazard(
        profiles=hazard_profiles_fixture(),
        terrain=hazard_terrain_fixture(),
    )
    html = map_object.render()

    assert {source["name"] for source in map_object.sources} == {
        "boundary",
        "terrain-source",
        "hazards",
    }
    assert "pmtiles://" in html
    assert '"source-layer": "hazard_wheelchair"' in html
    assert "switchHazardProfile" in html
    assert "category_${category}" in html
    assert "terrain-wheelchair.png" in html
    assert "Difficult surface" in html
    assert {binding.id for binding in map_object.event_bindings} >= {
        "feature-state-hover:hazard-hit:move",
        "feature-state-hover:hazard-hit:leave",
    }


def completeness_fixture():
    return {
        "metadata": {
            "city": "Test City",
            "bounds": [-49.4, -25.7, -49.1, -25.3],
        },
        "timestamps": ["2026-01-01", "2026-02-01"],
        "zoom_levels": {
            "12": {
                "tiles": {
                    "12/1/2": {
                        "bbox": [-49.4, -25.7, -49.3, -25.6],
                        "data": [
                            {
                                "road_length": 100,
                                "footway_length": 20,
                                "sidewalk_length": 10,
                                "footway_ratio": 0.2,
                                "sidewalk_ratio": 0.1,
                            },
                            {
                                "road_length": 100,
                                "footway_length": 30,
                                "sidewalk_length": 20,
                                "footway_ratio": 0.3,
                                "sidewalk_ratio": 0.2,
                            },
                        ],
                    }
                }
            }
        },
    }


def test_completeness_transform_preserves_zoom_history_and_tile_geometry():
    geojson = completeness_to_geojson(completeness_fixture())
    feature = geojson["features"][0]

    assert feature["properties"]["tile_id"] == "12/1/2"
    assert feature["properties"]["zoom"] == 12
    assert feature["properties"]["footway_ratio_t1"] == 0.3
    assert feature["properties"]["_color"].startswith("rgba(")
    assert feature["geometry"]["coordinates"][0][0] == [-49.4, -25.7]
    assert feature["geometry"]["coordinates"][0][-1] == [-49.4, -25.7]


def test_completeness_builder_reproduces_temporal_zoom_and_statistics_controls():
    map_object = build_completeness(completeness_fixture())
    html = map_object.render()

    assert len(map_object.layers) == 7
    assert "completenessTimestampSlider" in html
    assert "activeCompletenessZoom" in html
    assert "Ratio Histogram" in html
    assert "type:'boxplot'" in html
    assert "completenessGeoJSON = map.__maplibreumSourceDefinitions.tiles.data" in html
    assert html.count("12/1/2") == 1


def acquisition_fixture():
    return {
        "node_name": "Test City",
        "generated_at": "2026-08-20T08:05:54Z",
        "bbox": [-25.7, -49.4, -25.3, -49.1],
        "service_status": {"MapRoulette": {"status": "ok"}},
        "projects": [
            {
                "id": 1,
                "title": "Sidewalk survey",
                "service": "MapRoulette",
                "instance": "https://maproulette.org/",
                "url": "https://maproulette.org/challenge/1",
                "status": "Ready",
                "description": "Map missing sidewalks",
                "matched_keywords": ["sidewalk"],
                "bbox": [-49.3, -25.6, -49.2, -25.5],
            }
        ],
    }


def test_acquisition_builder_reproduces_dashboard_list_map_filters_and_footprints():
    map_object = build_acquisition(acquisition_fixture())
    html = map_object.render()

    assert map_object.bounds == [-49.4, -25.7, -49.1, -25.3]
    assert {layer["id"] for layer in map_object.layers} == {
        "boundary-layer",
        "project-fills",
        "project-borders",
    }
    assert "OSWM Data Acquisition — Test City" in html
    assert "acquisitionListView" in html
    assert "acquisitionMapView" in html
    assert "acquisitionFilteredProjects" in html
    assert "Sidewalk survey" in html
    assert "acquisition-marker" in html
    assert html.index("acquisition-header") < html.index('id="oswm-acquisition-map"')
