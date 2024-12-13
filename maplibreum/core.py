import os
import json
import uuid
from jinja2 import Environment, FileSystemLoader, Markup
from IPython.display import IFrame, display


class Map:
    def __init__(
        self,
        title="MapLibreum Map",
        map_style="https://demotiles.maplibre.org/style.json",
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
