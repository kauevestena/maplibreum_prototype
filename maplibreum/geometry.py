"""Geometry classes for MapLibreum."""

import math
import uuid


class Circle:
    """Draw a circle with radius in meters."""

    def __init__(
        self,
        location,
        radius=1000,
        color="#3388ff",
        fill=True,
        fill_color=None,
        fill_opacity=0.5,
        popup=None,
        tooltip=None,
    ):
        """Initialize a Circle.

        Parameters
        ----------
        location : list or tuple
            The ``[lng, lat]`` center of the circle.
        radius : int, optional
            The radius of the circle in meters.
        color : str, optional
            The color of the circle's outline.
        fill : bool, optional
            Whether to fill the circle.
        fill_color : str, optional
            The fill color of the circle.
        fill_opacity : float, optional
            The fill opacity of the circle.
        popup : str, optional
            A popup to display when the circle is clicked.
        tooltip : str, optional
            A tooltip to display when hovering over the circle.
        """
        self.location = location
        self.radius = radius
        self.color = color
        self.fill = fill
        self.fill_color = fill_color if fill_color else color
        self.fill_opacity = fill_opacity
        self.popup = popup
        self.tooltip = tooltip

    def _circle_polygon(self, center, radius, num_sides=64):
        """Create a GeoJSON polygon for a circle."""
        lng, lat = center
        coords = []
        for i in range(num_sides):
            angle = 2 * math.pi * i / num_sides
            dx = radius * math.cos(angle)
            dy = radius * math.sin(angle)
            delta_lng = dx / (111320 * math.cos(math.radians(lat)))
            delta_lat = dy / 110540
            coords.append([lng + delta_lng, lat + delta_lat])
        coords.append(coords[0])
        return [coords]

    def add_to(self, map_instance):
        """Add the circle to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the circle will be added.
        """
        layer_id = f"circle_{uuid.uuid4().hex}"
        polygon = self._circle_polygon(self.location, self.radius)
        source = {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": polygon},
                        "properties": {},
                    }
                ],
            },
        }
        paint = {
            "fill-color": self.fill_color if self.fill else "rgba(0,0,0,0)",
            "fill-opacity": self.fill_opacity if self.fill else 0,
            "fill-outline-color": self.color,
        }
        layer = {"id": layer_id, "type": "fill", "source": layer_id, "paint": paint}
        map_instance.add_layer(layer, source=source)
        if self.popup:
            map_instance.add_popup(html=self.popup, layer_id=layer_id)
        if self.tooltip:
            map_instance.add_tooltip(self.tooltip, layer_id=layer_id)


class CircleMarker:
    """Circle marker with radius in pixels."""

    def __init__(
        self,
        location,
        radius=6,
        color="#3388ff",
        fill=True,
        fill_color=None,
        fill_opacity=1.0,
        popup=None,
        tooltip=None,
    ):
        """Initialize a CircleMarker.

        Parameters
        ----------
        location : list or tuple
            The ``[lng, lat]`` center of the circle marker.
        radius : int, optional
            The radius of the circle marker in pixels.
        color : str, optional
            The color of the circle marker's outline.
        fill : bool, optional
            Whether to fill the circle marker.
        fill_color : str, optional
            The fill color of the circle marker.
        fill_opacity : float, optional
            The fill opacity of the circle marker.
        popup : str, optional
            A popup to display when the circle marker is clicked.
        tooltip : str, optional
            A tooltip to display when hovering over the circle marker.
        """
        self.location = location
        self.radius = radius
        self.color = color
        self.fill = fill
        self.fill_color = fill_color if fill_color else color
        self.fill_opacity = fill_opacity
        self.popup = popup
        self.tooltip = tooltip

    def add_to(self, map_instance):
        """Add the circle marker to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the circle marker will be added.
        """
        layer_id = f"circlemarker_{uuid.uuid4().hex}"
        source = {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": self.location},
                        "properties": {},
                    }
                ],
            },
        }
        paint = {
            "circle-radius": self.radius,
            "circle-color": self.fill_color if self.fill else "rgba(0,0,0,0)",
            "circle-opacity": self.fill_opacity if self.fill else 0,
            "circle-stroke-color": self.color,
            "circle-stroke-width": 1,
        }
        layer = {"id": layer_id, "type": "circle", "source": layer_id, "paint": paint}
        map_instance.add_layer(layer, source=source)
        if self.popup:
            map_instance.add_popup(html=self.popup, layer_id=layer_id)
        if self.tooltip:
            map_instance.add_tooltip(self.tooltip, layer_id=layer_id)


class PolyLine:
    """A polyline on the map."""

    def __init__(self, locations, color="#3388ff", weight=2, popup=None, tooltip=None):
        """Initialize a PolyLine.

        Parameters
        ----------
        locations : list
            A list of ``[lng, lat]`` coordinates.
        color : str, optional
            The color of the polyline.
        weight : int, optional
            The width of the polyline.
        popup : str, optional
            A popup to display when the polyline is clicked.
        tooltip : str, optional
            A tooltip to display when hovering over the polyline.
        """
        self.locations = locations
        self.color = color
        self.weight = weight
        self.popup = popup
        self.tooltip = tooltip

    def add_to(self, map_instance):
        """Add the polyline to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the polyline will be added.
        """
        layer_id = f"polyline_{uuid.uuid4().hex}"
        source = {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": self.locations,
                        },
                        "properties": {},
                    }
                ],
            },
        }
        paint = {"line-color": self.color, "line-width": self.weight}
        layer = {"id": layer_id, "type": "line", "source": layer_id, "paint": paint}
        map_instance.add_layer(layer, source=source)
        if self.popup:
            map_instance.add_popup(html=self.popup, layer_id=layer_id)
        if self.tooltip:
            map_instance.add_tooltip(self.tooltip, layer_id=layer_id)


class Polygon:
    """A polygon on the map."""

    def __init__(
        self,
        locations,
        color="#3388ff",
        weight=2,
        fill=True,
        fill_color=None,
        fill_opacity=0.5,
        popup=None,
        tooltip=None,
    ):
        """Initialize a Polygon.

        Parameters
        ----------
        locations : list
            A list of ``[lng, lat]`` coordinates.
        color : str, optional
            The color of the polygon's outline.
        weight : int, optional
            The width of the polygon's outline.
        fill : bool, optional
            Whether to fill the polygon.
        fill_color : str, optional
            The fill color of the polygon.
        fill_opacity : float, optional
            The fill opacity of the polygon.
        popup : str, optional
            A popup to display when the polygon is clicked.
        tooltip : str, optional
            A tooltip to display when hovering over the polygon.
        """
        self.locations = locations
        self.color = color
        self.weight = weight
        self.fill = fill
        self.fill_color = fill_color if fill_color else color
        self.fill_opacity = fill_opacity
        self.popup = popup
        self.tooltip = tooltip

    def add_to(self, map_instance):
        """Add the polygon to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the polygon will be added.
        """
        layer_id = f"polygon_{uuid.uuid4().hex}"
        coords = self.locations
        if coords[0] != coords[-1]:
            coords = coords + [coords[0]]
        source = {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": [coords]},
                        "properties": {},
                    }
                ],
            },
        }
        paint = {
            "fill-color": self.fill_color if self.fill else "rgba(0,0,0,0)",
            "fill-opacity": self.fill_opacity if self.fill else 0,
            "fill-outline-color": self.color,
        }
        fill_layer = {
            "id": layer_id,
            "type": "fill",
            "source": layer_id,
            "paint": paint,
        }
        map_instance.add_layer(fill_layer, source=source)
        if self.weight:
            outline_layer = {
                "id": f"{layer_id}_outline",
                "type": "line",
                "source": layer_id,
                "paint": {"line-color": self.color, "line-width": self.weight},
            }
            map_instance.add_layer(outline_layer, source=layer_id)
        if self.popup:
            map_instance.add_popup(html=self.popup, layer_id=layer_id)
        if self.tooltip:
            map_instance.add_tooltip(self.tooltip, layer_id=layer_id)


class Rectangle:
    """Axis-aligned rectangle defined by southwest and northeast corners."""

    def __init__(
        self,
        southwest,
        northeast,
        color="#3388ff",
        weight=2,
        fill=True,
        fill_color=None,
        fill_opacity=0.5,
        popup=None,
        tooltip=None,
    ):
        """Initialize a Rectangle.

        Parameters
        ----------
        southwest : list or tuple
            The southwest corner of the rectangle as ``[lng, lat]``.
        northeast : list or tuple
            The northeast corner of the rectangle as ``[lng, lat]``.
        color : str, optional
            The color of the rectangle's outline.
        weight : int, optional
            The width of the rectangle's outline.
        fill : bool, optional
            Whether to fill the rectangle.
        fill_color : str, optional
            The fill color of the rectangle.
        fill_opacity : float, optional
            The fill opacity of the rectangle.
        popup : str, optional
            A popup to display when the rectangle is clicked.
        tooltip : str, optional
            A tooltip to display when hovering over the rectangle.
        """
        self.southwest = southwest
        self.northeast = northeast
        self.color = color
        self.weight = weight
        self.fill = fill
        self.fill_color = fill_color if fill_color else color
        self.fill_opacity = fill_opacity
        self.popup = popup
        self.tooltip = tooltip

    def add_to(self, map_instance):
        """Add the rectangle to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the rectangle will be added.
        """
        sw_lng, sw_lat = self.southwest
        ne_lng, ne_lat = self.northeast
        coords = [
            [sw_lng, sw_lat],
            [sw_lng, ne_lat],
            [ne_lng, ne_lat],
            [ne_lng, sw_lat],
        ]
        polygon = Polygon(
            coords,
            color=self.color,
            weight=self.weight,
            fill=self.fill,
            fill_color=self.fill_color,
            fill_opacity=self.fill_opacity,
            popup=self.popup,
            tooltip=self.tooltip,
        )
        polygon.add_to(map_instance)
