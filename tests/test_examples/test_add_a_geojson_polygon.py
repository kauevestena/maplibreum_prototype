"""Test for add-a-geojson-polygon MapLibre example."""

import pytest

from maplibreum.core import Map


def test_add_a_geojson_polygon():
    """Test recreating the 'add-a-geojson-polygon' MapLibre example.

    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [-68.13734351262877, 45.137451890638886],
        zoom: 5
    });

    map.on('load', () => {
        map.addSource('maine', {
            'type': 'geojson',
            'data': {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            [-67.13734351262877, 45.137451890638886],
                            [-66.96466, 44.8097],
                            [-68.03252, 44.3252],
                            [-69.06, 43.98],
                            [-70.11617, 43.68405],
                            [-70.64573401557249, 43.090083319667144],
                            [-70.75102474636725, 43.08003225358635],
                            [-70.79761105007827, 43.21973948828747],
                            [-70.98176001655037, 43.36789581966826],
                            [-70.94416541205806, 43.46633942318431],
                            [-71.08482, 45.3052400000002],
                            [-70.6600225491012, 45.46022288673396],
                            [-70.30495378282376, 45.914794623389355],
                            [-70.00014034695016, 46.69317088478567],
                            [-69.23708614772835, 47.44777598732787],
                            [-68.90478084987546, 47.184794623394396],
                            [-68.23430497910454, 47.35462921812177],
                            [-67.79035274928509, 47.066248887716995],
                            [-67.79141211614706, 45.702585354182816],
                            [-67.13734351262877, 45.137451890638886]
                        ]
                    ]
                }
            }
        });
        map.addLayer({
            'id': 'maine',
            'type': 'fill',
            'source': 'maine',
            'layout': {},
            'paint': {
                'fill-color': '#088',
                'fill-opacity': 0.8
            }
        });
    });
    ```
    """
    polygon_coordinates = [
        [-67.13734351262877, 45.137451890638886],
        [-66.96466, 44.8097],
        [-68.03252, 44.3252],
        [-69.06, 43.98],
        [-70.11617, 43.68405],
        [-70.64573401557249, 43.090083319667144],
        [-70.75102474636725, 43.08003225358635],
        [-70.79761105007827, 43.21973948828747],
        [-70.98176001655037, 43.36789581966826],
        [-70.94416541205806, 43.46633942318431],
        [-71.08482, 45.3052400000002],
        [-70.6600225491012, 45.46022288673396],
        [-70.30495378282376, 45.914794623389355],
        [-70.00014034695016, 46.69317088478567],
        [-69.23708614772835, 47.44777598732787],
        [-68.90478084987546, 47.184794623394396],
        [-68.23430497910454, 47.35462921812177],
        [-67.79035274928509, 47.066248887716995],
        [-67.79141211614706, 45.702585354182816],
        [-67.13734351262877, 45.137451890638886],
    ]

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-68.13734351262877, 45.137451890638886],
        zoom=5,
    )

    geojson_data = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [polygon_coordinates],
        },
    }

    m.add_fill_layer(
        name="maine",
        source={"type": "geojson", "data": geojson_data},
        paint={
            "fill-color": "#088",
            "fill-opacity": 0.8,
        },
    )

    assert m.center[0] == pytest.approx(-68.13734351262877)
    assert m.center[1] == pytest.approx(45.137451890638886)
    assert m.zoom == pytest.approx(5)
    assert m.map_style == "https://demotiles.maplibre.org/style.json"

    assert len(m.layers) == 1
    assert len(m.sources) == 1

    fill_layer = m.layers[0]
    source = m.sources[0]

    assert fill_layer["definition"]["type"] == "fill"
    assert fill_layer["definition"]["paint"]["fill-color"] == "#088"
    assert fill_layer["definition"]["paint"]["fill-opacity"] == pytest.approx(0.8)
    assert fill_layer["definition"].get("layout", {}) == {}
    assert fill_layer["definition"]["source"] == source["name"]

    assert source["definition"]["type"] == "geojson"
    geometry = source["definition"]["data"]["geometry"]
    assert geometry["type"] == "Polygon"
    assert len(geometry["coordinates"]) == 1
    first_point = geometry["coordinates"][0][0]
    last_point = geometry["coordinates"][0][-1]
    assert first_point[0] == pytest.approx(polygon_coordinates[0][0])
    assert first_point[1] == pytest.approx(polygon_coordinates[0][1])
    assert last_point[0] == pytest.approx(polygon_coordinates[-1][0])
    assert last_point[1] == pytest.approx(polygon_coordinates[-1][1])
    assert len(geometry["coordinates"][0]) == len(polygon_coordinates)

    html = m.render()
    assert "demotiles.maplibre.org/style.json" in html
    assert "fill-color" in html
    assert "Polygon" in html
