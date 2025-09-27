from maplibreum import Map
from maplibreum.layers import LineLayer
from maplibreum.sources import GeoJSONSource


D3_SCRIPT = "https://d3js.org/d3.v3.min.js"


TRACE_TEMPLATE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {"type": "LineString", "coordinates": []},
        }
    ],
}


REALTIME_JS = """
map.on('load', () => {
    d3.json('https://maplibre.org/maplibre-gl-js/docs/assets/hike.geojson', (err, data) => {
        if (err) {
            throw err;
        }
        const coordinates = data.features[0].geometry.coordinates;
        data.features[0].geometry.coordinates = [coordinates[0]];
        map.getSource('trace').setData(data);
        map.jumpTo({ center: coordinates[0], zoom: 14 });
        map.setPitch(30);
        let i = 0;
        const timer = window.setInterval(() => {
            if (i < coordinates.length) {
                data.features[0].geometry.coordinates.push(coordinates[i]);
                map.getSource('trace').setData(data);
                map.panTo(coordinates[i]);
                i++;
            } else {
                window.clearInterval(timer);
            }
        }, 10);
    });
});
"""


def test_update_a_feature_in_realtime():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        zoom=0,
    )

    m.add_source("trace", GeoJSONSource(data=TRACE_TEMPLATE))
    m.add_layer(
        LineLayer(
            id="trace",
            source="trace",
            paint={
                "line-color": "yellow",
                "line-opacity": 0.75,
                "line-width": 5,
            },
        )
    )
    m.add_external_script(D3_SCRIPT)
    m.add_on_load_js(REALTIME_JS)

    html = m.render()

    assert D3_SCRIPT in html
    assert "d3.json" in html
    assert any(source["name"] == "trace" for source in m.sources)
    assert any(layer["definition"]["id"] == "trace" for layer in m.layers)
    assert "map.getSource('trace').setData" in html
    assert "window.setInterval" in html
    assert "map.getSource('trace').setData(data);" in html
