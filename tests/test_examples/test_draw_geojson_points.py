"""Test for draw-geojson-points example."""

import pytest
from maplibreum import Map


def test_draw_geojson_points():
    """Test drawing points from a GeoJSON collection."""

    # Create map with same parameters as original
    m = Map(
        map_style="https://demotiles.maplibre.org/style.json", center=[0, 0], zoom=1
    )

    # Add custom marker image
    m.add_image(
        "custom-marker",
        url="https://maplibre.org/maplibre-gl-js/docs/assets/osgeo-logo.png",
    )

    # GeoJSON data from the original example (subset for testing)
    conferences_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [100.4933, 13.7551]},
                "properties": {"year": "2004"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [6.6523, 46.5535]},
                "properties": {"year": "2006"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-123.3596, 48.4268]},
                "properties": {"year": "2007"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [18.4264, -33.9224]},
                "properties": {"year": "2008"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [151.195, -33.8552]},
                "properties": {"year": "2009"},
            },
        ],
    }

    # Add the conferences source
    m.add_source("conferences", conferences_data)

    # Add symbol layer
    m.add_layer(
        {
            "id": "conferences",
            "type": "symbol",
            "source": "conferences",
            "layout": {
                "icon-image": "custom-marker",
                # get the year from the source's "year" property
                "text-field": ["get", "year"],
                "text-font": ["Noto Sans Regular"],
                "text-offset": [0, 1.25],
                "text-anchor": "top",
            },
        }
    )

    # Verify the components were added correctly
    source_names = [source["name"] for source in m.sources]
    assert "conferences" in source_names

    # Find the conferences source
    conferences_source_def = None
    for source in m.sources:
        if source["name"] == "conferences":
            conferences_source_def = source["definition"]
            break

    assert conferences_source_def is not None
    # When passing GeoJSON data directly, it becomes the source definition
    assert conferences_source_def["type"] == "FeatureCollection"
    assert len(conferences_source_def["features"]) == 5

    # Check first feature
    first_feature = conferences_source_def["features"][0]
    assert first_feature["geometry"]["type"] == "Point"
    assert first_feature["geometry"]["coordinates"] == [100.4933, 13.7551]
    assert first_feature["properties"]["year"] == "2004"

    # Verify layer was added
    assert len(m.layers) == 1
    layer = m.layers[0]
    assert layer["id"] == "conferences"
    assert layer["definition"]["type"] == "symbol"
    assert layer["definition"]["source"] == "conferences"
    assert layer["definition"]["layout"]["icon-image"] == "custom-marker"
    assert layer["definition"]["layout"]["text-field"] == ["get", "year"]
    assert layer["definition"]["layout"]["text-font"] == ["Noto Sans Regular"]
    assert layer["definition"]["layout"]["text-offset"] == [0, 1.25]
    assert layer["definition"]["layout"]["text-anchor"] == "top"

    # Verify image was added
    assert len(m.images) == 1
    assert m.images[0]["id"] == "custom-marker"
    assert "osgeo-logo.png" in m.images[0]["url"]

    # Generate HTML and verify content
    html = m._repr_html_()

    # Should contain the map style and center
    assert "demotiles.maplibre.org/style.json" in html
    assert "[0, 0]" in html or "[0,0]" in html

    # Should contain conferences source and layer
    assert "conferences" in html
    assert "custom-marker" in html

    # Should contain some coordinates and years
    assert "100.4933" in html
    assert "2004" in html


if __name__ == "__main__":
    test_draw_geojson_points()
    print("✓ draw-geojson-points test passed")
