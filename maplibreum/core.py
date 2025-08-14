import os
import json
import uuid
import math
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from IPython.display import IFrame, display


# Predefined map styles
MAP_STYLES = {
    "basic": "https://demotiles.maplibre.org/style.json",
    "streets": "https://api.maptiler.com/maps/streets/style.json?key=YOUR_API_KEY",
    "satellite": "https://api.maptiler.com/maps/satellite/style.json?key=YOUR_API_KEY",
    "topo": "https://api.maptiler.com/maps/topo/style.json?key=YOUR_API_KEY",
    "dark": "https://api.maptiler.com/maps/darkmatter/style.json?key=YOUR_API_KEY",
    "light": "https://api.maptiler.com/maps/positron/style.json?key=YOUR_API_KEY",
}


class Map:
    def __init__(
        self,
        title="MapLibreum Map",
        map_style="basic",
        center=[0, 0],
        zoom=2,
        width="100%",
        height="500px",
        controls=None,
        layers=None,
        popups=None,
        extra_js="",
        custom_css="",
    ):
        self.title = title
        if map_style in MAP_STYLES:
            self.map_style = MAP_STYLES[map_style]
        else:
            self.map_style = map_style
        self.center = center
        self.zoom = zoom
        self.width = width
        self.height = height
        self.controls = controls if controls is not None else []
        self.sources = []
        self.layers = layers if layers is not None else []
        self.tile_layers = []
        self.popups = popups if popups is not None else []
        self.extra_js = extra_js
        self.custom_css = custom_css
        self.layer_control = False

        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.filters["tojson"] = lambda value: json.dumps(value)
        self.template = self.env.get_template("map_template.html")

        # Unique ID for the map (important if multiple maps displayed in a notebook)
        self.map_id = f"maplibreum_{uuid.uuid4().hex}"

    def add_control(self, control_type, position="top-right", options=None):
        """
        Add a control to the map.
        control_type: str, one of ['navigation', 'scale', 'fullscreen']
        position: str, e.g. 'top-right', 'top-left', etc.
        options: dict, e.g. for scale control { "maxWidth": 80, "unit": "imperial" }
        """
        if options is None:
            options = {}
        self.controls.append(
            {"type": control_type, "position": position, "options": options}
        )

    def add_source(self, name, definition):
        """
        Add a source to the map.
        name: str, the name of the source
        definition: dict, the source definition
        """
        self.sources.append({"name": name, "definition": definition})

    def add_layer(self, layer_definition, source=None, before=None):
        """
        Add a layer to the map.
        layer_definition: dict describing a MapLibre GL style layer
        source: dict describing a MapLibre source (optional)
        before: the ID of an existing layer before which this layer should be placed
        """
        if isinstance(source, str):
            # Source is a string, so we assume it's a source name
            # that has already been added to the map.
            layer_definition["source"] = source
        elif source is not None:
            # Source is a dict, so we add it to the map's sources.
            source_name = f"source_{uuid.uuid4().hex}"
            self.add_source(source_name, source)
            layer_definition["source"] = source_name

        layer_id = layer_definition.get("id", f"layer_{uuid.uuid4().hex}")
        layer_definition["id"] = layer_id

        self.layers.append(
            {"id": layer_id, "definition": layer_definition, "before": before}
        )

    def add_tile_layer(self, url, name=None, attribution=None):
        """Add a raster tile layer to the map.

        Parameters
        ----------
        url : str
            Tile URL template.
        name : str, optional
            Name of the layer. If omitted, a unique ID is generated.
        attribution : str, optional
            Attribution text for the layer.
        """
        layer_id = name or f"tilelayer_{uuid.uuid4().hex}"
        source = {
            "type": "raster",
            "tiles": [url],
            "tileSize": 256,
        }
        if attribution:
            source["attribution"] = attribution
        layer = {"id": layer_id, "type": "raster", "source": layer_id}
        self.add_layer(layer, source=source)
        self.tile_layers.append({"id": layer_id, "name": name or layer_id})

    def add_popup(
        self, html, coordinates=None, layer_id=None, events=None, options=None
    ):
        """
        Add a popup to the map.
        html: HTML content of the popup
        coordinates: [lng, lat] for a fixed popup position
        layer_id: if popup is triggered by clicking a feature in a given layer
        events: list of events that trigger the popup (e.g. ['click'])
        options: dict of popup options (e.g. { "closeButton": true })
        """
        if options is None:
            options = {}
        if events is None:
            events = ["click"]  # default event
        self.popups.append(
            {
                "html": html,
                "coordinates": coordinates,
                "layer_id": layer_id,
                "events": events,
                "options": options,
            }
        )

    def add_marker(self, coordinates=None, popup=None, color="#007cbf"):

        """Add a marker to the map.

        Parameters
        ----------
        coordinates : list or tuple, optional
            [lng, lat] pair where the marker will be placed. Defaults to the
            map's center if not provided.
        popup : str, optional
            HTML content for a popup bound to the marker.
        color : str, optional
            Color of the marker, defaults to MapLibre blue.
        """
        if coordinates is None:
            coordinates = self.center

        marker = Marker(coordinates=coordinates, popup=popup, color=color)
        marker.add_to(self)
        return marker

    def add_circle_layer(
        self, name, source, paint=None, layout=None, before=None, filter=None
    ):
        """
        Add a circle layer to the map.
        """
        if paint is None:
            paint = {"circle-radius": 6, "circle-color": "#007cbf"}
        layer_definition = {"id": name, "type": "circle", "paint": paint}
        if layout:
            layer_definition["layout"] = layout
        if filter:
            layer_definition["filter"] = filter
        self.add_layer(layer_definition, source=source, before=before)

    def add_fill_layer(
        self, name, source, paint=None, layout=None, before=None, filter=None
    ):
        """
        Add a fill layer to the map.
        """
        if paint is None:
            paint = {"fill-color": "#007cbf", "fill-opacity": 0.5}
        layer_definition = {"id": name, "type": "fill", "paint": paint}
        if layout:
            layer_definition["layout"] = layout
        if filter:
            layer_definition["filter"] = filter
        self.add_layer(layer_definition, source=source, before=before)

    def add_line_layer(
        self, name, source, paint=None, layout=None, before=None, filter=None
    ):
        """
        Add a line layer to the map.
        """
        if paint is None:
            paint = {"line-color": "#007cbf", "line-width": 2}
        layer_definition = {"id": name, "type": "line", "paint": paint}
        if layout:
            layer_definition["layout"] = layout
        if filter:
            layer_definition["filter"] = filter
        self.add_layer(layer_definition, source=source, before=before)

    def add_heatmap_layer(
        self, name, source, paint=None, layout=None, before=None, filter=None
    ):
        """
        Add a heatmap layer to the map.

        Parameters
        ----------
        name : str
            Layer identifier.
        source : dict or str
            Source definition or the name of an existing source.
        paint : dict, optional
            Heatmap paint properties. Missing properties fall back to sensible
            defaults.
        layout : dict, optional
            Layout properties for the layer.
        before : str, optional
            ID of an existing layer before which this layer should be placed.
        filter : list, optional
            MapLibre filter expression.
        """
        default_paint = {
            "heatmap-radius": 20,
            "heatmap-intensity": 1,
            "heatmap-opacity": 1,
            "heatmap-color": [
                "interpolate",
                ["linear"],
                ["heatmap-density"],
                0,
                "rgba(0,0,255,0)",
                0.2,
                "blue",
                0.4,
                "cyan",
                0.6,
                "lime",
                0.8,
                "yellow",
                1,
                "red",
            ],
        }
        if paint:
            default_paint.update(paint)
        layer_definition = {
            "id": name,
            "type": "heatmap",
            "paint": default_paint,
        }
        if layout:
            layer_definition["layout"] = layout
        if filter:
            layer_definition["filter"] = filter
        self.add_layer(layer_definition, source=source, before=before)

    def add_symbol_layer(
        self, name, source, paint=None, layout=None, before=None, filter=None
    ):
        """
        Add a symbol layer to the map.
        """
        if layout is None:
            layout = {"icon-image": "marker-15"}
        layer_definition = {"id": name, "type": "symbol", "layout": layout}
        if paint:
            layer_definition["paint"] = paint
        if filter:
            layer_definition["filter"] = filter
        self.add_layer(layer_definition, source=source, before=before)

    def render(self):
        # Inject custom CSS to adjust the map div if needed
        # The template expects #map { width: ..., height: ... } to be set via custom_css if desired.
        dimension_css = f"#map {{ width: {self.width}; height: {self.height}; }}"
        final_custom_css = dimension_css + "\n" + self.custom_css

        return self.template.render(
            title=self.title,
            map_style=self.map_style,
            center=self.center,
            zoom=self.zoom,
            sources=self.sources,
            controls=self.controls,
            layers=self.layers,
            tile_layers=self.tile_layers,
            layer_control=self.layer_control,
            popups=self.popups,
            extra_js=self.extra_js,
            custom_css=final_custom_css,
        )

    def _repr_html_(self):
        # Jupyter Notebook display method
        # We'll save the HTML in a temp file and use an iframe, or directly return HTML as a raw iframe.
        html = self.render()
        # Note: Directly returning HTML strings is allowed in Jupyter,
        # but to avoid iframe sandboxing issues, we can just return the raw HTML.
        # However, returning raw HTML might not always display properly if it contains scripts.
        # A more stable approach is to write to a temporary file and display it in an IFrame.

        # For simplicity, just return the HTML:
        return html

    def display_in_notebook(self, width="100%", height="500px"):
        # More controlled display using IFrame approach
        from tempfile import NamedTemporaryFile

        f = NamedTemporaryFile(suffix=".html", delete=False)
        f.write(self.render().encode("utf-8"))
        f.close()
        return display(IFrame(src=f.name, width=width, height=height))

    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.render())


class Marker:
    def __init__(self, coordinates, popup=None, color="#007cbf"):
        self.coordinates = coordinates
        self.popup = popup
        self.color = color

    def add_to(self, map_instance):
        layer_id = f"marker_{uuid.uuid4().hex}"
        source = {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": self.coordinates,
                        },
                        "properties": {},
                    }
                ],
            },
        }
        layer = {
            "id": layer_id,
            "type": "circle",
            "source": layer_id,
            "paint": {
                "circle-radius": 8,
                "circle-color": self.color,
                "circle-stroke-width": 1,
                "circle-stroke-color": "#fff",
            },
        }
        map_instance.add_layer(layer, source=source)

        if self.popup:
            map_instance.add_popup(html=self.popup, layer_id=layer_id)


class GeoJson:
    """
    Representation of a GeoJSON overlay.

    Parameters
    ----------
    data : dict
        A GeoJSON ``FeatureCollection``.
    style_function : callable, optional
        Function called for each feature. It should return a dictionary with
        style properties similar to the Leaflet style specification. Supported
        keys include ``stroke`` (bool), ``color`` (stroke color), ``weight``
        (stroke width), ``opacity`` (stroke opacity), ``fill`` (bool),
        ``fillColor`` (fill color), ``fillOpacity`` (fill opacity) and
        ``radius`` (circle radius for point features). Missing keys fall back to
        sensible defaults.
    name : str, optional
        Base name for generated source and layer identifiers.
    """

    def __init__(self, data, style_function=None, name=None):
        self.data = data
        self.name = name if name else f"geojson_{uuid.uuid4().hex}"

        if style_function:
            self.style_function = style_function
        else:
            self.style_function = lambda feature: {
                "stroke": True,
                "color": "#007cbf",
                "weight": 2,
                "opacity": 1,
                "fill": True,
                "fillColor": "#007cbf",
                "fillOpacity": 0.6,
                "radius": 6,
            }

    def add_to(self, map_instance):
        """Add this GeoJSON object to a map instance.

        The geometry type of each feature is inspected and appropriate layers
        (``fill`` for polygons, ``line`` for polylines and ``circle`` for
        points) are created. The ``style_function`` is used to populate feature
        properties such as ``stroke``, ``weight`` and ``fillColor`` which are
        then referenced by the layer paint definitions.
        """
        # Apply the style function to each feature and update its properties
        features = self.data.get("features", [])
        for feature in features:
            style = self.style_function(feature)
            feature.setdefault("properties", {}).update(style)

        source_id = f"{self.name}_source"
        source = {"type": "geojson", "data": self.data}
        map_instance.add_source(source_id, source)

        def _get(prop):
            return ["get", prop, ["properties"]]

        geometry_types = [
            f.get("geometry", {}).get("type") for f in features if f.get("geometry")
        ]

        if any(t in ("Polygon", "MultiPolygon") for t in geometry_types):
            fill_layer = {
                "id": f"{self.name}_fill",
                "type": "fill",
                "paint": {
                    "fill-color": _get("fillColor"),
                    "fill-opacity": _get("fillOpacity"),
                    "fill-outline-color": _get("color"),
                },
            }
            map_instance.add_layer(fill_layer, source=source_id)

        if any(t in ("LineString", "MultiLineString") for t in geometry_types):
            line_layer = {
                "id": f"{self.name}_line",
                "type": "line",
                "paint": {
                    "line-color": _get("color"),
                    "line-width": _get("weight"),
                    "line-opacity": _get("opacity"),
                },
            }
            map_instance.add_layer(line_layer, source=source_id)

        if any(t in ("Point", "MultiPoint") for t in geometry_types):
            circle_layer = {
                "id": f"{self.name}_circle",
                "type": "circle",
                "paint": {
                    "circle-color": _get("fillColor"),
                    "circle-opacity": _get("fillOpacity"),
                    "circle-radius": _get("radius"),
                    "circle-stroke-color": _get("color"),
                    "circle-stroke-width": _get("weight"),
                    "circle-stroke-opacity": _get("opacity"),
                },
            }
            map_instance.add_layer(circle_layer, source=source_id)



class Circle:
    """Draw a circle with radius in meters."""

    def __init__(
        self,
        location,
        radius=1000,
        color="#3388ff",
        fill=True,
        fill_color=None,
        popup=None,
    ):
        self.location = location
        self.radius = radius
        self.color = color
        self.fill = fill
        self.fill_color = fill_color if fill_color else color
        self.popup = popup

    def _circle_polygon(self, center, radius, num_sides=64):
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
            "fill-opacity": 0.5 if self.fill else 0,
            "fill-outline-color": self.color,
        }
        layer = {"id": layer_id, "type": "fill", "source": layer_id, "paint": paint}
        map_instance.add_layer(layer, source=source)
        if self.popup:
            map_instance.add_popup(html=self.popup, layer_id=layer_id)


class CircleMarker:
    """Circle marker with radius in pixels."""

    def __init__(
        self,
        location,
        radius=6,
        color="#3388ff",
        fill=True,
        fill_color=None,
        popup=None,
    ):
        self.location = location
        self.radius = radius
        self.color = color
        self.fill = fill
        self.fill_color = fill_color if fill_color else color
        self.popup = popup

    def add_to(self, map_instance):
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
            "circle-stroke-color": self.color,
            "circle-stroke-width": 1,
        }
        layer = {"id": layer_id, "type": "circle", "source": layer_id, "paint": paint}
        map_instance.add_layer(layer, source=source)
        if self.popup:
            map_instance.add_popup(html=self.popup, layer_id=layer_id)


class PolyLine:
    def __init__(self, locations, color="#3388ff", weight=2, popup=None):
        self.locations = locations
        self.color = color
        self.weight = weight
        self.popup = popup

    def add_to(self, map_instance):
        layer_id = f"polyline_{uuid.uuid4().hex}"
        source = {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "LineString", "coordinates": self.locations},
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


class LayerControl:
    """Simple layer control to toggle tile layers."""

    def add_to(self, map_instance):
        map_instance.layer_control = True
        return self

