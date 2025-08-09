import unittest
from maplibreum.core import Map, Marker, GeoJson


class TestFeatures(unittest.TestCase):
    def test_map_style(self):
        m = Map(map_style="streets")
        self.assertEqual(
            m.map_style,
            "https://api.maptiler.com/maps/streets/style.json?key=get_your_own_OpIi9ZULNHzrESv6T2vL",
        )

    def test_marker(self):
        m = Map()
        marker = Marker(coordinates=[-74.5, 40], popup="A marker!", color="red")
        marker.add_to(m)
        self.assertEqual(len(m.layers), 1)
        self.assertEqual(len(m.popups), 1)
        self.assertEqual(m.layers[0]["definition"]["paint"]["circle-color"], "red")

    def test_add_marker_wrapper(self):
        m = Map()
        m.add_marker(coordinates=[-74.5, 40], popup="Wrapper marker", color="green")
        self.assertEqual(len(m.layers), 1)
        self.assertEqual(len(m.popups), 1)
        self.assertEqual(m.layers[0]["definition"]["paint"]["circle-color"], "green")

    def test_geojson(self):
        m = Map()
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[-74.6, 40.1], [-74.6, 39.9], [-74.4, 39.9], [-74.4, 40.1], [-74.6, 40.1]]],
                    },
                }
            ],
        }

        def style_function(feature):
            return {"fillColor": "blue", "fillOpacity": 0.5}

        geojson_layer = GeoJson(geojson_data, style_function=style_function)
        geojson_layer.add_to(m)
        self.assertEqual(len(m.layers), 1)
        self.assertEqual(m.layers[0]["definition"]["type"], "fill")
        self.assertEqual(
            m.layers[0]["definition"]["paint"]["fill-color"],
            ["get", "color", ["properties"]],
        )


if __name__ == "__main__":
    unittest.main()
