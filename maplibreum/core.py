import os
import json
import uuid
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from IPython.display import IFrame, display


# Predefined map styles
MAP_STYLES = {
    "basic": "https://demotiles.maplibre.org/style.json",
    "streets": "https://api.maptiler.com/maps/streets/style.json?key=get_your_own_OpIi9ZULNHzrESv6T2vL",
    "satellite": "https://api.maptiler.com/maps/satellite/style.json?key=get_your_own_OpIi9ZULNHzrESv6T2vL",
    "topo": "https://api.maptiler.com/maps/topo/style.json?key=get_your_own_OpIi9ZULNHzrESv6T2vL",
    "dark": "https://api.maptiler.com/maps/darkmatter/style.json?key=get_your_own_OpIi9ZULNHzrESv6T2vL",
    "light": "https://api.maptiler.com/maps/positron/style.json?key=get_your_own_OpIi9ZULNHzrESv6T2vL",
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
        self.layers = layers if layers is not None else []
        self.popups = popups if popups is not None else []
        self.extra_js = extra_js
        self.custom_css = custom_css

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

    def add_layer(self, layer_definition, source=None, before=None):
        """
        Add a layer to the map.
        layer_definition: dict describing a MapLibre GL style layer
        source: dict describing a MapLibre source (optional)
        before: the ID of an existing layer before which this layer should be placed
        """
        layer_id = layer_definition.get("id", f"layer_{uuid.uuid4().hex}")
        # Ensure layer has an id
        layer_definition["id"] = layer_id
        self.layers.append(
            {
                "id": layer_id,
                "definition": layer_definition,
                "source": source,
                "before": before,
            }
        )

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
            controls=self.controls,
            layers=self.layers,
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
    def __init__(self, data, style_function=None, name=None):
        self.data = data
        self.name = name if name else f"geojson_{uuid.uuid4().hex}"

        if style_function:
            self.style_function = style_function
        else:
            self.style_function = lambda x: {
                "color": "#007cbf",
                "weight": 2,
                "opacity": 1,
                "fillColor": "#007cbf",
                "fillOpacity": 0.6,
            }

    def add_to(self, map_instance):
        source = {"type": "geojson", "data": self.data}
        layer_id = self.name
        layer = {
            "id": layer_id,
            "type": "fill",  # Default to fill, can be customized
            "source": layer_id,
            "paint": {
                "fill-color": [
                    "get",
                    "color",
                    ["properties"],
                ],  # Example, needs more robust implementation
                "fill-opacity": ["get", "opacity", ["properties"]],
            },
        }

        # A more robust implementation would parse the style_function
        # and apply it to the paint properties.
        # For now, we'll keep it simple.

        # Process features to add style properties
        for feature in self.data["features"]:
            style = self.style_function(feature)
            feature["properties"]["color"] = style.get("fillColor", "#007cbf")
            feature["properties"]["opacity"] = style.get("fillOpacity", 0.6)

        map_instance.add_layer(layer, source=source)
