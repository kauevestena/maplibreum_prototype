"""Test for create-and-style-clusters MapLibre example."""

import pytest

from maplibreum.core import Map


def test_create_and_style_clusters():
    """Test recreating the 'create-and-style-clusters' MapLibre example.

    Original JavaScript:
    ```
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [-103.59179687498357, 40.66995747013945],
        zoom: 3
    });

    map.on('load', () => {
        map.addSource('earthquakes', {
            type: 'geojson',
            data: 'https://maplibre.org/maplibre-gl-js/docs/assets/earthquakes.geojson',
            cluster: true,
            clusterMaxZoom: 14,
            clusterRadius: 50
        });

        map.addLayer({
            id: 'clusters',
            type: 'circle',
            source: 'earthquakes',
            filter: ['has', 'point_count'],
            paint: {
                'circle-color': ['step', ['get', 'point_count'], '#51bbd6', 100, '#f1f075', 750, '#f28cb1'],
                'circle-radius': ['step', ['get', 'point_count'], 20, 100, 30, 750, 40]
            }
        });

        map.addLayer({
            id: 'cluster-count',
            type: 'symbol',
            source: 'earthquakes',
            filter: ['has', 'point_count'],
            layout: {
                'text-field': '{point_count_abbreviated}',
                'text-font': ['Noto Sans Regular'],
                'text-size': 12
            }
        });

        map.addLayer({
            id: 'unclustered-point',
            type: 'circle',
            source: 'earthquakes',
            filter: ['!', ['has', 'point_count']],
            paint: {
                'circle-color': '#11b4da',
                'circle-radius': 4,
                'circle-stroke-width': 1,
                'circle-stroke-color': '#fff'
            }
        });

        map.on('click', 'clusters', (e) => {
            const features = map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
            const clusterId = features[0].properties.cluster_id;
            map.getSource('earthquakes').getClusterExpansionZoom(clusterId, (err, zoom) => {
                if (err) return;
                map.easeTo({ center: features[0].geometry.coordinates, zoom: zoom });
            });
        });

        map.on('click', 'unclustered-point', (e) => {
            const { coordinates } = e.features[0].geometry;
            const { mag, tsunami } = e.features[0].properties;
            new maplibregl.Popup()
                .setLngLat(coordinates)
                .setHTML(`magnitude: ${mag}<br>Was there a tsunami?: ${tsunami}`)
                .addTo(map);
        });

        map.on('mouseenter', 'clusters', () => {
            map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', 'clusters', () => {
            map.getCanvas().style.cursor = '';
        });
    });
    ```
    """

    earthquakes = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"mag": 1.8, "tsunami": "no", "color": "#11b4da"},
                "geometry": {"type": "Point", "coordinates": [-104.99, 39.74]},
            },
            {
                "type": "Feature",
                "properties": {"mag": 2.6, "tsunami": "no", "color": "#11b4da"},
                "geometry": {"type": "Point", "coordinates": [-103.45, 41.1]},
            },
            {
                "type": "Feature",
                "properties": {"mag": 3.9, "tsunami": "yes", "color": "#11b4da"},
                "geometry": {"type": "Point", "coordinates": [-101.89, 40.72]},
            },
            {
                "type": "Feature",
                "properties": {"mag": 4.3, "tsunami": "no", "color": "#11b4da"},
                "geometry": {"type": "Point", "coordinates": [-102.5, 39.5]},
            },
            {
                "type": "Feature",
                "properties": {"mag": 5.1, "tsunami": "yes", "color": "#11b4da"},
                "geometry": {"type": "Point", "coordinates": [-104.2, 42.0]},
            },
        ],
    }

    for feature in earthquakes["features"]:
        props = feature.setdefault("properties", {})
        props["description"] = (
            f"magnitude: {props['mag']}<br>Was there a tsunami?: {props['tsunami']}"
        )

    m = Map(
        map_style="https://demotiles.maplibre.org/style.json",
        center=[-103.59179687498357, 40.66995747013945],
        zoom=3,
    )

    cluster = m.add_clustered_geojson(
        earthquakes,
        name="earthquakes",
        radius=50,
        max_zoom=14,
    )

    cluster_layer = next(
        layer for layer in m.layers if layer["id"] == cluster.cluster_layer_id
    )
    cluster_layer["definition"]["paint"]["circle-color"] = [
        "step",
        ["get", "point_count"],
        "#51bbd6",
        100,
        "#f1f075",
        750,
        "#f28cb1",
    ]

    count_layer = next(
        layer for layer in m.layers if layer["id"] == cluster.count_layer_id
    )
    count_layer["definition"]["layout"] = {
        "text-field": "{point_count_abbreviated}",
        "text-font": ["Noto Sans Regular"],
        "text-size": 12,
    }

    unclustered_layer = next(
        layer for layer in m.layers if layer["id"] == cluster.unclustered_layer_id
    )
    unclustered_layer["definition"]["paint"].update(
        {
            "circle-color": "#11b4da",
            "circle-radius": 4,
            "circle-stroke-width": 1,
            "circle-stroke-color": "#fff",
        }
    )

    m.add_popup(
        layer_id=cluster.unclustered_layer_id,
        prop="description",
        events=["click"],
    )

    assert m.center[0] == pytest.approx(-103.59179687498357)
    assert m.center[1] == pytest.approx(40.66995747013945)
    assert m.zoom == pytest.approx(3)

    assert len(m.sources) == 1
    assert len(m.layers) == 3
    assert cluster.cluster_layer_id in {layer["id"] for layer in m.layers}
    assert cluster.count_layer_id in {layer["id"] for layer in m.layers}
    assert cluster.unclustered_layer_id in {layer["id"] for layer in m.layers}

    assert cluster_layer["definition"]["filter"] == ["has", "point_count"]
    assert count_layer["definition"]["filter"] == ["has", "point_count"]
    assert unclustered_layer["definition"]["filter"] == ["!", ["has", "point_count"]]

    html = m.render()
    assert "getClusterExpansionZoom" in html
    assert "{point_count_abbreviated}" in html
    assert "magnitude:" in html
