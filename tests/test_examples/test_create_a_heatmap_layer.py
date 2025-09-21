"""Test for create-a-heatmap-layer MapLibre example."""
import pytest

from maplibreum.core import Map


def test_create_a_heatmap_layer():
    """Test recreating the 'create-a-heatmap-layer' MapLibre example.

    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [-120, 50],
        zoom: 2
    });

    map.on('load', () => {
        map.addSource('earthquakes', {
            'type': 'geojson',
            'data': 'https://maplibre.org/maplibre-gl-js/docs/assets/earthquakes.geojson'
        });

        map.addLayer({
            'id': 'earthquakes-heat',
            'type': 'heatmap',
            'source': 'earthquakes',
            'maxzoom': 9,
            'paint': {
                'heatmap-weight': ['interpolate', ['linear'], ['get', 'mag'], 0, 0, 6, 1],
                'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 9, 3],
                'heatmap-color': ['interpolate', ['linear'], ['heatmap-density'],
                                   0, 'rgba(33,102,172,0)',
                                   0.2, 'rgb(103,169,207)',
                                   0.4, 'rgb(209,229,240)',
                                   0.6, 'rgb(253,219,199)',
                                   0.8, 'rgb(239,138,98)',
                                   1, 'rgb(178,24,43)'],
                'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 2, 9, 20],
                'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 7, 1, 9, 0]
            }
        });

        map.addLayer({
            'id': 'earthquakes-point',
            'type': 'circle',
            'source': 'earthquakes',
            'minzoom': 7,
            'paint': {
                'circle-radius': ['interpolate', ['linear'], ['zoom'],
                                   7, ['interpolate', ['linear'], ['get', 'mag'], 1, 1, 6, 4],
                                   16, ['interpolate', ['linear'], ['get', 'mag'], 1, 5, 6, 50]],
                'circle-color': ['interpolate', ['linear'], ['get', 'mag'],
                                  1, 'rgba(33,102,172,0)',
                                  2, 'rgb(103,169,207)',
                                  3, 'rgb(209,229,240)',
                                  4, 'rgb(253,219,199)',
                                  5, 'rgb(239,138,98)',
                                  6, 'rgb(178,24,43)'],
                'circle-stroke-color': 'white',
                'circle-stroke-width': 1,
                'circle-opacity': ['interpolate', ['linear'], ['zoom'], 7, 0, 8, 1]
            }
        });
    });
    ```
    """

    earthquakes_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"mag": 1.5},
                "geometry": {"type": "Point", "coordinates": [-122.75, 38.2]},
            },
            {
                "type": "Feature",
                "properties": {"mag": 3.1},
                "geometry": {"type": "Point", "coordinates": [-120.0, 35.1]},
            },
            {
                "type": "Feature",
                "properties": {"mag": 5.4},
                "geometry": {"type": "Point", "coordinates": [-118.2, 34.05]},
            },
            {
                "type": "Feature",
                "properties": {"mag": 4.7},
                "geometry": {"type": "Point", "coordinates": [-123.0, 49.2]},
            },
        ],
    }

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-120, 50],
        zoom=2,
    )

    m.add_source("earthquakes", {"type": "geojson", "data": earthquakes_geojson})

    heatmap_paint = {
        "heatmap-weight": [
            "interpolate",
            ["linear"],
            ["get", "mag"],
            0,
            0,
            6,
            1,
        ],
        "heatmap-intensity": [
            "interpolate",
            ["linear"],
            ["zoom"],
            0,
            1,
            9,
            3,
        ],
        "heatmap-color": [
            "interpolate",
            ["linear"],
            ["heatmap-density"],
            0,
            "rgba(33,102,172,0)",
            0.2,
            "rgb(103,169,207)",
            0.4,
            "rgb(209,229,240)",
            0.6,
            "rgb(253,219,199)",
            0.8,
            "rgb(239,138,98)",
            1,
            "rgb(178,24,43)",
        ],
        "heatmap-radius": [
            "interpolate",
            ["linear"],
            ["zoom"],
            0,
            2,
            9,
            20,
        ],
        "heatmap-opacity": [
            "interpolate",
            ["linear"],
            ["zoom"],
            7,
            1,
            9,
            0,
        ],
    }

    m.add_heatmap_layer(
        name="earthquakes-heat",
        source="earthquakes",
        paint=heatmap_paint,
    )

    circle_paint = {
        "circle-radius": [
            "interpolate",
            ["linear"],
            ["zoom"],
            7,
            ["interpolate", ["linear"], ["get", "mag"], 1, 1, 6, 4],
            16,
            ["interpolate", ["linear"], ["get", "mag"], 1, 5, 6, 50],
        ],
        "circle-color": [
            "interpolate",
            ["linear"],
            ["get", "mag"],
            1,
            "rgba(33,102,172,0)",
            2,
            "rgb(103,169,207)",
            3,
            "rgb(209,229,240)",
            4,
            "rgb(253,219,199)",
            5,
            "rgb(239,138,98)",
            6,
            "rgb(178,24,43)",
        ],
        "circle-stroke-color": "white",
        "circle-stroke-width": 1,
        "circle-opacity": [
            "interpolate",
            ["linear"],
            ["zoom"],
            7,
            0,
            8,
            1,
        ],
    }

    m.add_circle_layer(
        name="earthquakes-point",
        source="earthquakes",
        paint=circle_paint,
    )

    heat_layer_id = "earthquakes-heat"
    circle_layer_id = "earthquakes-point"

    # Match the original layer metadata that lives outside helper defaults.
    for layer in m.layers:
        if layer["id"] == heat_layer_id:
            layer["definition"]["maxzoom"] = 9
        if layer["id"] == circle_layer_id:
            layer["definition"]["minzoom"] = 7

    assert m.center[0] == pytest.approx(-120)
    assert m.center[1] == pytest.approx(50)
    assert m.zoom == pytest.approx(2)
    assert m.map_style == "https://demotiles.maplibre.org/style.json"

    assert len(m.sources) == 1
    assert len(m.layers) == 2

    heat_layer = next(layer for layer in m.layers if layer["id"] == heat_layer_id)
    assert heat_layer["definition"]["type"] == "heatmap"
    assert heat_layer["definition"]["maxzoom"] == 9
    assert heat_layer["definition"]["paint"]["heatmap-weight"][0] == "interpolate"
    assert heat_layer["definition"]["paint"]["heatmap-color"][2] == ["heatmap-density"]

    circle_layer = next(layer for layer in m.layers if layer["id"] == circle_layer_id)
    assert circle_layer["definition"]["type"] == "circle"
    assert circle_layer["definition"]["minzoom"] == 7
    assert circle_layer["definition"]["paint"]["circle-radius"][0] == "interpolate"
    assert circle_layer["definition"]["paint"]["circle-color"][1] == ["linear"]
    assert circle_layer["definition"]["paint"]["circle-opacity"][0] == "interpolate"

    html = m.render()
    assert "earthquakes-heat" in html
    assert "heatmap-density" in html
    assert "circle-stroke-color" in html
    assert "FeatureCollection" in html
