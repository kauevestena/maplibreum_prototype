import requests_mock

from maplibreum import Map
from maplibreum.layers import LineLayer
from maplibreum.realtime import AnimatePointOnLine, RealTimeDataSource

HIKE_GEOJSON_URL = "https://maplibre.org/maplibre-gl-js/docs/assets/hike.geojson"


def test_update_a_feature_in_realtime_with_python_api():
    # Prepare the mock data
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-122.483696, 37.833818], [-122.483482, 37.833174]],
                },
            }
        ],
    }

    # Setup requests mock
    with requests_mock.Mocker() as m:
        m.get(HIKE_GEOJSON_URL, json=geojson_data)

        # Create the map
        map_ = Map(
            map_style="https://tiles.openfreemap.org/styles/bright",
            zoom=14,
            pitch=30,
        )

        # Create the real-time data source
        source_id = "trace"
        source = RealTimeDataSource.from_url(
            url=HIKE_GEOJSON_URL,
        )
        map_.add_source(source_id, source)

        # Add the layer to display the line
        layer = LineLayer(
            id="trace",
            source=source_id,
            paint={"line-color": "yellow", "line-opacity": 0.75, "line-width": 5},
        )
        map_.add_layer(layer)

        # Create and add the animation
        animation = AnimatePointOnLine(
            source_id=source_id,
            data=source.data,
            interval=10,
        )
        map_.add_on_load_js(animation.to_js())

        # Render the map
        html = map_.render()

        # Verify the output
        assert f"map.getSource('{source_id}')" in html
        assert "window.clearInterval(timer)" in html
        assert "setInterval" in html
        assert "map.panTo(coordinates[i])" in html
        assert "setData" in html
        assert "const coordinates =" in html
        assert "let data =" in html
        assert "let i = 1;" in html
        assert "var timer = setInterval" in html
        assert "function(){" in html
        assert "if (i < coordinates.length) {" in html
        assert "map.getSource('trace').setData(data)" in html
        assert "d3.json" not in html  # Should not use d3
        assert "window.setInterval(() => {" not in html  # Should use the generated function