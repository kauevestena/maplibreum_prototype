"""Test for display-line-that-crosses-180th-meridian example."""

import pytest
from maplibreum import Map


def test_display_line_that_crosses_180th_meridian():
    """Test displaying lines that cross the 180th meridian."""

    # Create map with same parameters as original
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-41.62667, 26.11598],
        zoom=0,
    )

    def create_geometry(does_cross_antimeridian=False):
        """Create line geometry, optionally crossing the antimeridian."""
        geometry = {
            "type": "LineString",
            "coordinates": [[-72.42187, -16.59408], [140.27343, 35.67514]],
        }

        # To draw a line across the 180th meridian,
        # if the longitude of the second point minus
        # the longitude of original (or previous) point is >= 180,
        # subtract 360 from the longitude of the second point.
        # If it is less than 180, add 360 to the second point.

        if does_cross_antimeridian:
            start_lng = geometry["coordinates"][0][0]
            end_lng = geometry["coordinates"][1][0]

            if end_lng - start_lng >= 180:
                geometry["coordinates"][1][0] -= 360
            elif end_lng - start_lng < 180:
                geometry["coordinates"][1][0] += 360

        return geometry

    # Add first route (normal line)
    route_data = {
        "type": "Feature",
        "properties": {},
        "geometry": create_geometry(False),
    }

    m.add_source("route", {"type": "geojson", "data": route_data})

    # Add route line layer
    m.add_layer(
        {
            "id": "route",
            "type": "line",
            "source": "route",
            "layout": {"line-cap": "round"},
            "paint": {"line-color": "#007296", "line-width": 4},
        }
    )

    # Add route label
    m.add_layer(
        {
            "id": "route-label",
            "type": "symbol",
            "source": "route",
            "layout": {
                "symbol-placement": "line-center",
                "text-field": "Crosses the world",
            },
        }
    )

    # Add second route (crosses 180th meridian)
    route_two_data = {
        "type": "Feature",
        "properties": {},
        "geometry": create_geometry(True),
    }

    m.add_source("route-two", {"type": "geojson", "data": route_two_data})

    # Add second route line layer
    m.add_layer(
        {
            "id": "route-two",
            "type": "line",
            "source": "route-two",
            "layout": {"line-cap": "round"},
            "paint": {"line-color": "#F06317", "line-width": 4},
        }
    )

    # Add second route label
    m.add_layer(
        {
            "id": "route-two-label",
            "type": "symbol",
            "source": "route-two",
            "layout": {
                "symbol-placement": "line-center",
                "text-field": "Crosses 180th meridian",
            },
        }
    )

    # Verify the components were added correctly
    source_names = [source["name"] for source in m.sources]
    assert "route" in source_names
    assert "route-two" in source_names

    # Verify we have 4 layers (2 lines + 2 labels)
    assert len(m.layers) == 4

    # Find each layer and verify properties
    route_layer = None
    route_label_layer = None
    route_two_layer = None
    route_two_label_layer = None

    for layer in m.layers:
        if layer["id"] == "route":
            route_layer = layer
        elif layer["id"] == "route-label":
            route_label_layer = layer
        elif layer["id"] == "route-two":
            route_two_layer = layer
        elif layer["id"] == "route-two-label":
            route_two_label_layer = layer

    # Verify route layer
    assert route_layer is not None
    assert route_layer["definition"]["type"] == "line"
    assert route_layer["definition"]["paint"]["line-color"] == "#007296"
    assert route_layer["definition"]["paint"]["line-width"] == 4
    assert route_layer["definition"]["layout"]["line-cap"] == "round"

    # Verify route label layer
    assert route_label_layer is not None
    assert route_label_layer["definition"]["type"] == "symbol"
    assert (
        route_label_layer["definition"]["layout"]["text-field"] == "Crosses the world"
    )
    assert (
        route_label_layer["definition"]["layout"]["symbol-placement"] == "line-center"
    )

    # Verify route-two layer
    assert route_two_layer is not None
    assert route_two_layer["definition"]["type"] == "line"
    assert route_two_layer["definition"]["paint"]["line-color"] == "#F06317"
    assert route_two_layer["definition"]["paint"]["line-width"] == 4
    assert route_two_layer["definition"]["layout"]["line-cap"] == "round"

    # Verify route-two label layer
    assert route_two_label_layer is not None
    assert route_two_label_layer["definition"]["type"] == "symbol"
    assert (
        route_two_label_layer["definition"]["layout"]["text-field"]
        == "Crosses 180th meridian"
    )
    assert (
        route_two_label_layer["definition"]["layout"]["symbol-placement"]
        == "line-center"
    )

    # Verify the coordinate transformation for the second route
    original_coords = route_data["geometry"]["coordinates"]
    transformed_coords = route_two_data["geometry"]["coordinates"]

    # First coordinate should be the same
    assert transformed_coords[0] == original_coords[0]

    # Second coordinate should be transformed
    # Since end_lng - start_lng = 140.27343 - (-72.42187) = 212.6953 >= 180,
    # we subtract 360: 140.27343 - 360 = -219.72657
    assert transformed_coords[1][0] == original_coords[1][0] - 360
    assert transformed_coords[1][1] == original_coords[1][1]  # latitude unchanged

    # Generate HTML and verify content
    html = m._repr_html_()

    # Should contain the map style and center
    assert "demotiles.maplibre.org/style.json" in html
    assert "-41.62667" in html
    assert "26.11598" in html

    # Should contain both routes
    assert "route" in html
    assert "route-two" in html

    # Should contain line colors
    assert "#007296" in html
    assert "#F06317" in html

    # Should contain labels
    assert "Crosses the world" in html
    assert "Crosses 180th meridian" in html


if __name__ == "__main__":
    test_display_line_that_crosses_180th_meridian()
    print("✓ display-line-that-crosses-180th-meridian test passed")
