"""Test for the add-a-canvas-source MapLibre example."""

from maplibreum import Map, layers, sources


def test_add_a_canvas_source_configuration():
    """Ensure canvas sources serialise correctly without live animation.

    The upstream example animates an HTML canvas element, which requires a
    browser event loop. Here we only validate the static configuration used by
    ``map.addSource`` to document the accessibility/performance trade-off in the
    Python port.
    """

    m = Map()
    canvas_source = sources.CanvasSource(
        canvas="canvas-id",
        bounds=[-76.54, 39.17, -76.52, 39.18],
        animate=True,
        attribution="Canvas demo",
    )
    m.add_source("canvas-source", canvas_source)
    m.add_layer(
        layers.RasterLayer(
            id="canvas-layer",
            source="canvas-source",
            paint={"raster-opacity": 0.7},
        ).to_dict()
    )

    html = m.render()
    assert '"type": "canvas"' in html
    definition = m.sources[0]["definition"]
    assert definition["canvas"] == "canvas-id"
    assert definition["animate"] is True
    assert definition["coordinates"][0] == [-76.54, 39.18]
    assert definition["attribution"] == "Canvas demo"
