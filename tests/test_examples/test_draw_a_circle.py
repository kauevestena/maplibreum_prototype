"""Regression test for the draw-a-circle gallery example."""

from __future__ import annotations

import math

from maplibreum import Map


_RADIUS_CENTER = [2.3454, 48.8452]


def _geodesic_circle(center: list[float], radius_km: float, steps: int) -> dict:
    """Generate a GeoJSON polygon approximating a circle on Earth."""

    if steps < 3:
        raise ValueError("steps must be at least 3 to form a polygon")

    lng_rad = math.radians(center[0])
    lat_rad = math.radians(center[1])
    angular_distance = radius_km / 6371.0
    coordinates: list[list[float]] = []

    for index in range(steps):
        bearing = 2.0 * math.pi * index / steps
        lat_point = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance)
            + math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing)
        )
        lng_point = lng_rad + math.atan2(
            math.sin(bearing) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(lat_point),
        )
        coordinates.append([math.degrees(lng_point), math.degrees(lat_point)])

    coordinates.append(coordinates[0])

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [coordinates]},
                "properties": {},
            }
        ],
    }


def test_draw_a_circle() -> None:
    """Reproduce drawing a circle using a GeoJSON source."""

    map_style = {
        "version": 8,
        "sources": {
            "osm": {
                "type": "raster",
                "tiles": ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                "tileSize": 256,
                "attribution": "&copy; OpenStreetMap Contributors",
                "maxzoom": 19,
            }
        },
        "layers": [{"id": "osm", "type": "raster", "source": "osm"}],
    }

    m = Map(
        map_style=map_style,
        center=_RADIUS_CENTER,
        zoom=13,
        map_options={"maxZoom": 18, "maxPitch": 85},
    )

    circle_data = _geodesic_circle(_RADIUS_CENTER, radius_km=1, steps=64)
    m.add_source("location-radius", circle_data)

    m.add_layer(
        {
            "id": "location-radius",
            "type": "fill",
            "source": "location-radius",
            "paint": {"fill-color": "#8CCFFF", "fill-opacity": 0.5},
        }
    )
    m.add_layer(
        {
            "id": "location-radius-outline",
            "type": "line",
            "source": "location-radius",
            "paint": {"line-color": "#0094ff", "line-width": 3},
        }
    )

    assert m.map_style == map_style
    assert m.additional_map_options == {"maxZoom": 18, "maxPitch": 85}

    assert m.sources[0]["name"] == "location-radius"
    polygon = m.sources[0]["definition"]["features"][0]["geometry"]
    assert polygon["type"] == "Polygon"
    assert len(polygon["coordinates"][0]) == 65

    fill_layer = next(layer for layer in m.layers if layer["id"] == "location-radius")
    assert fill_layer["definition"]["paint"]["fill-color"] == "#8CCFFF"
    assert fill_layer["definition"]["paint"]["fill-opacity"] == 0.5

    outline_layer = next(
        layer for layer in m.layers if layer["id"] == "location-radius-outline"
    )
    assert outline_layer["definition"]["paint"]["line-width"] == 3

    html = m.render()
    assert "tile.openstreetmap.org" in html
    assert "location-radius" in html
    assert "fill-opacity" in html
