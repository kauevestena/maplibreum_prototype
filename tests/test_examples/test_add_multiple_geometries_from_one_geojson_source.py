"""Test for add-multiple-geometries-from-one-geojson-source MapLibre example."""

import pytest

from maplibreum.core import Map


def test_add_multiple_geometries_from_one_geojson_source():
    """Test recreating the 'add-multiple-geometries-from-one-geojson-source' example.

    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://tiles.openfreemap.org/styles/bright',
        center: [-121.403732, 40.492392],
        zoom: 10
    });

    map.on('load', () => {
        map.addSource('national-park', {
            'type': 'geojson',
            'data': '.../lassen-volcano.geojson'
        });

        map.addLayer({
            'id': 'park-boundary',
            'type': 'fill',
            'source': 'national-park',
            'paint': {'fill-color': '#888888', 'fill-opacity': 0.4},
            'filter': ['==', '$type', 'Polygon']
        });

        map.addLayer({
            'id': 'park-boundary-outline',
            'type': 'line',
            'source': 'national-park',
            'paint': {'line-color': '#000000', 'line-width': 2},
            'filter': ['==', '$type', 'Polygon']
        });

        map.addLayer({
            'id': 'park-trails',
            'type': 'line',
            'source': 'national-park',
            'layout': {'line-join': 'round', 'line-cap': 'round'},
            'paint': {'line-color': '#ff69b4', 'line-width': 4},
            'filter': ['==', '$type', 'LineString']
        });

        map.addLayer({
            'id': 'park-volcanoes',
            'type': 'circle',
            'source': 'national-park',
            'paint': {'circle-radius': 6, 'circle-color': '#B42222'},
            'filter': ['==', '$type', 'Point']
        });
    });
    ```
    """

    park_boundary = [
        [-121.353637, 40.584978],
        [-121.284551, 40.584758],
        [-121.275349, 40.541646],
        [-121.246768, 40.541017],
        [-121.251343, 40.423383],
        [-121.32687, 40.423768],
        [-121.360619, 40.43479],
        [-121.363694, 40.409124],
        [-121.439713, 40.409197],
        [-121.439711, 40.423791],
        [-121.572133, 40.423548],
        [-121.577415, 40.550766],
        [-121.539486, 40.558107],
        [-121.520284, 40.572459],
        [-121.487219, 40.550822],
        [-121.446951, 40.56319],
        [-121.370644, 40.563267],
        [-121.353637, 40.584978],
    ]

    trail_coordinates = [
        [-121.4004, 40.5080],
        [-121.4250, 40.5120],
        [-121.4510, 40.5225],
        [-121.4850, 40.5340],
    ]

    volcanoes = [
        [-121.415061, 40.506229],
        [-121.505184, 40.488084],
        [-121.354465, 40.488737],
    ]

    national_park = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Lassen Volcanic National Park"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [park_boundary],
                },
            },
            {
                "type": "Feature",
                "properties": {"name": "Primary Trail"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": trail_coordinates,
                },
            },
            {
                "type": "Feature",
                "properties": {"name": "Cinder Cone"},
                "geometry": {"type": "Point", "coordinates": volcanoes[0]},
            },
            {
                "type": "Feature",
                "properties": {"name": "Brokeoff"},
                "geometry": {"type": "Point", "coordinates": volcanoes[1]},
            },
            {
                "type": "Feature",
                "properties": {"name": "Chaos Crags"},
                "geometry": {"type": "Point", "coordinates": volcanoes[2]},
            },
        ],
    }

    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-121.403732, 40.492392],
        zoom=10,
    )

    m.add_source("national-park", {"type": "geojson", "data": national_park})

    m.add_fill_layer(
        name="park-boundary",
        source="national-park",
        paint={"fill-color": "#888888", "fill-opacity": 0.4},
        filter=["==", "$type", "Polygon"],
    )

    m.add_line_layer(
        name="park-boundary-outline",
        source="national-park",
        paint={"line-color": "#000000", "line-width": 2},
        filter=["==", "$type", "Polygon"],
    )

    m.add_line_layer(
        name="park-trails",
        source="national-park",
        layout={"line-join": "round", "line-cap": "round"},
        paint={"line-color": "#ff69b4", "line-width": 4},
        filter=["==", "$type", "LineString"],
    )

    m.add_circle_layer(
        name="park-volcanoes",
        source="national-park",
        paint={"circle-radius": 6, "circle-color": "#B42222"},
        filter=["==", "$type", "Point"],
    )

    assert m.center[0] == pytest.approx(-121.403732)
    assert m.center[1] == pytest.approx(40.492392)
    assert m.zoom == pytest.approx(10)

    assert len(m.sources) == 1
    assert len(m.layers) == 4

    layer_ids = {layer["id"] for layer in m.layers}
    assert {"park-boundary", "park-boundary-outline", "park-trails", "park-volcanoes"} <= layer_ids

    fill_layer = next(layer for layer in m.layers if layer["id"] == "park-boundary")
    assert fill_layer["definition"]["filter"] == ["==", "$type", "Polygon"]

    line_layer = next(layer for layer in m.layers if layer["id"] == "park-trails")
    assert line_layer["definition"]["filter"] == ["==", "$type", "LineString"]
    assert line_layer["definition"]["layout"]["line-join"] == "round"

    circle_layer = next(layer for layer in m.layers if layer["id"] == "park-volcanoes")
    assert circle_layer["definition"]["filter"] == ["==", "$type", "Point"]

    html = m.render()
    assert "FeatureCollection" in html
    assert "Polygon" in html
    assert "LineString" in html
    assert "circle-radius" in html
