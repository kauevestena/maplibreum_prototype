"""Test for add-a-pattern-to-a-polygon MapLibre example."""

from maplibreum import Map, layers


def test_add_a_pattern_to_a_polygon():
    """Recreate the pattern fill example using MapLibreum helpers."""

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        zoom=1,
        center=[0, 0],
    )

    pattern_id = m.add_image(
        "pattern-cat",
        url=(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/"
            "Cat_silhouette.svg/64px-Cat_silhouette.svg.png"
        ),
    )

    polygon = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-30.0, -25.0],
                    [-30.0, 35.0],
                    [30.0, 35.0],
                    [30.0, -25.0],
                    [-30.0, -25.0],
                ]
            ],
        },
    }
    m.add_source("pattern-source", {"type": "geojson", "data": polygon})

    pattern_layer = layers.FillLayer(
        id="pattern-layer",
        source="pattern-source",
        paint={"fill-pattern": pattern_id},
    )
    m.add_layer(pattern_layer.to_dict())

    assert len(m.images) == 1
    assert m.layers[0]["definition"]["paint"]["fill-pattern"] == pattern_id

    html = m.render()
    assert "fill-pattern" in html
    assert "map.loadImage" in html
    assert pattern_id in html
