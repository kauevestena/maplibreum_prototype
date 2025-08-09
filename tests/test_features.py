import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from maplibreum.core import (
    Map,
    Marker,
    GeoJson,
    Circle,
    CircleMarker,
    PolyLine,
    LayerControl,
)


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

    def test_geojson_line_and_point(self):
        m = Map()
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[0, 0], [1, 1]],
                    },
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {"type": "Point", "coordinates": [2, 2]},
                },
            ],
        }

        def style_function(feature):
            return {
                "color": "green",
                "weight": 5,
                "opacity": 0.7,
                "fillColor": "yellow",
                "fillOpacity": 0.4,
            }

        geojson_layer = GeoJson(geojson_data, style_function=style_function)
        geojson_layer.add_to(m)

        layer_types = {layer["definition"]["type"] for layer in m.layers}
        self.assertIn("line", layer_types)
        self.assertIn("circle", layer_types)

        line_layer = next(
            l for l in m.layers if l["definition"]["type"] == "line"
        )
        self.assertEqual(
            line_layer["definition"]["paint"]["line-color"],
            ["get", "color", ["properties"]],
        )
        self.assertEqual(
            line_layer["definition"]["paint"]["line-width"],
            ["get", "weight", ["properties"]],
        )

        circle_layer = next(
            l for l in m.layers if l["definition"]["type"] == "circle"
        )
        self.assertEqual(
            circle_layer["definition"]["paint"]["circle-color"],
            ["get", "fillColor", ["properties"]],
        )
        self.assertEqual(
            circle_layer["definition"]["paint"]["circle-stroke-width"],
            ["get", "weight", ["properties"]],
        )

    def test_tile_layer_and_control(self):
        m = Map()
        m.add_tile_layer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            name="OSM",
            attribution="© OpenStreetMap contributors",
        )
        html_no_control = m.render()
        self.assertIn("OSM", html_no_control)
        self.assertNotIn("layer-control", html_no_control)

        LayerControl().add_to(m)
        html_with_control = m.render()
        self.assertIn("layer-control", html_with_control)
        self.assertEqual(len(m.tile_layers), 1)
        self.assertTrue(m.layer_control)

    def test_shapes(self):
        m = Map()
        Circle([0, 0], radius=1000).add_to(m)
        CircleMarker([1, 1], radius=5).add_to(m)
        PolyLine([[0, 0], [1, 1]]).add_to(m)
        self.assertEqual(len(m.layers), 3)


if __name__ == "__main__":
    unittest.main()
