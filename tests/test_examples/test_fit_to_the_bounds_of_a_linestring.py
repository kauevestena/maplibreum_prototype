"""Parity test for the fit-to-the-bounds-of-a-linestring example."""

import json

from maplibreum.core import Map
from maplibreum import layers


def test_fit_to_the_bounds_of_a_linestring():
    button_css = """
    .maplibreum-zoomto {
        font: bold 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
        background-color: #3386c0;
        color: #fff;
        position: absolute;
        top: 20px;
        left: 50%;
        z-index: 1;
        border: none;
        width: 200px;
        margin-left: -100px;
        display: block;
        cursor: pointer;
        padding: 10px 20px;
        border-radius: 3px;
    }

    .maplibreum-zoomto:hover {
        background-color: #4ea0da;
    }
    """.strip()

    line_coordinates = [
        [-77.0366048812866, 38.89873175227713],
        [-77.03364372253417, 38.89876515143842],
        [-77.03364372253417, 38.89549195896866],
        [-77.02982425689697, 38.89549195896866],
        [-77.02400922775269, 38.89387200688839],
        [-77.01519012451172, 38.891416957534204],
        [-77.01521158218382, 38.892068305429156],
        [-77.00813055038452, 38.892051604275686],
        [-77.00832366943358, 38.89143365883688],
        [-77.00818419456482, 38.89082405874451],
        [-77.00815200805664, 38.88989712255097],
    ]

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-77.0214, 38.897],
        zoom=12,
        custom_css=button_css,
    )

    m.add_source(
        "LineString",
        {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": line_coordinates,
                        },
                    }
                ],
            },
        },
    )

    m.add_layer(
        layers.LineLayer(
            id="LineString",
            source="LineString",
            layout={"line-join": "round", "line-cap": "round"},
            paint={"line-color": "#BF93E4", "line-width": 5},
        ).to_dict()
    )

    coords_js = json.dumps(line_coordinates)

    m.add_on_load_js(
        "\n".join(
            [
                "const zoomButton = document.createElement('button');",
                "zoomButton.id = 'zoomto';",
                "zoomButton.className = 'maplibreum-zoomto';",
                "zoomButton.textContent = 'Zoom to bounds';",
                "document.body.appendChild(zoomButton);",
                f"const lineCoordinates = {coords_js};",
                "zoomButton.addEventListener('click', () => {",
                "    const bounds = lineCoordinates.reduce((acc, coord) => {",
                "        return acc.extend(coord);",
                "    }, new maplibregl.LngLatBounds(lineCoordinates[0], lineCoordinates[0]));",
                "    map.fitBounds(bounds, { padding: 20 });",
                "});",
            ]
        )
    )

    html = m.render()

    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-77.0214, 38.897]' in html
    assert '"zoom": 12' in html
    assert 'map.addSource("LineString"' in html
    assert "map.fitBounds(bounds, { padding: 20 });" in html
    assert "maplibregl.LngLatBounds" in html
