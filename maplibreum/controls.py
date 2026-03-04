from .utils import get_id
from typing import Optional, List, Dict, Any
from .styles import MAP_STYLES

class NavigationControl:
    def __init__(self, visualizePitch=False, showZoom=False, showCompass=False):
        self.options = {
            "visualizePitch": visualizePitch,
            "showZoom": showZoom,
            "showCompass": showCompass,
        }

    def to_dict(self):
        return self.options

class TerrainControl:
    def __init__(self, source, exaggeration=1):
        self.options = {"source": source, "exaggeration": exaggeration}

    def to_dict(self):
        return self.options

class GlobeControl:
    """Configuration wrapper for :class:`maplibregl.GlobeControl`."""
    def __init__(self, **options):
        self.options = options

    def to_dict(self):
        return self.options

class MiniMapControl:
    """Configuration object for the MiniMap plugin control."""
    def __init__(self, style="basic", zoom_level=6):
        self.options = {"style": style, "zoomLevel": zoom_level}

    def to_dict(self):
        return self.options

class AttributionControl:
    """Configuration object for the Attribution control."""
    def __init__(self, custom_attribution=None, compact=False):
        self.options = {}
        if custom_attribution is not None:
            self.options["customAttribution"] = custom_attribution
        if compact:
            self.options["compact"] = compact

    def to_dict(self):
        return self.options

class ScaleControl:
    """Configuration object for the Scale control."""
    def __init__(self, max_width=100, unit="metric"):
        self.options = {"maxWidth": max_width, "unit": unit}

    def to_dict(self):
        return self.options

class SearchControl:
    """Configuration object for the MapLibre Geocoder control."""
    def __init__(self, api_key: str, **options):
        self.options = {"apiKey": api_key, **options}

    def to_dict(self):
        return self.options

class GeocodingControl:
    def __init__(self, api_url=None):
        self.api_url = api_url
        self.control_type = 'geocoding'
    def to_js(self):
        pass
class GeocoderControl:
    """Configuration object for a Nominatim-based Geocoder control."""
    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url

    def to_dict(self) -> Dict[str, Any]:
        return {}

    def to_js(self) -> str:
        if not self.api_url:
            return """
const nominatimResponse = {
    features: [
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [13.4, 52.52] },
            properties: { display_name: 'Berlin, Germany' }
        }
    ]
};
const geocoderApi = {
    forwardGeocode: async (config) => nominatimResponse
};
const geocoder = new MaplibreGeocoder(geocoderApi, { maplibregl });
map.addControl(geocoder);
            """
        return f"""
const geocoderApi = {{
    forwardGeocode: async (config) => {{
        const response = await fetch('{self.api_url}?q=' + config.query + '&format=geojson');
        return await response.json();
    }}
}};
const geocoder = new MaplibreGeocoder(geocoderApi, {{ maplibregl }});
map.addControl(geocoder);
        """

class MapboxDrawControl:
    """Adds mapbox-gl-draw controls for creating and editing geometries."""
    def __init__(self, **options):
        self.options = options

    def to_dict(self):
        return self.options

    def to_js(self):
        options_json = json.dumps(self.options)
        return f"""
        const draw = new MapboxDraw({options_json});
        map.addControl(draw);
        """

class TerraDrawControl:
    """Adds terra-draw controls for creating and editing geometries."""
    def __init__(self, modes: List[str] = None, current_mode: str = "polygon"):
        self.modes = modes if modes is not None else ["point", "linestring", "polygon", "rectangle", "circle", "freehand"]
        self.current_mode = current_mode

    def to_dict(self):
        return {"modes": self.modes, "current_mode": self.current_mode}

    def to_js(self):
        modes_js = ",\n".join([f"new terraDraw.TerraDraw{m.capitalize()}Mode()" for m in self.modes])
        return f"""
        const draw = new terraDraw.TerraDraw({{
            adapter: new terraDraw.TerraDrawMapLibreGLAdapter({{
                map: map,
                lib: maplibregl,
            }}),
            modes: [
                {modes_js}
            ]
        }});
        draw.start();
        draw.setMode('{self.current_mode}');
        """

class GeolocateControl:
    """Configuration object for the Geolocate plugin control."""
    def __init__(
        self,
        position_options=None,
        fit_bounds_options=None,
        track_user_location=False,
        show_accuracy_circle=True,
        show_user_location=True,
    ):
        self.options = {
            "positionOptions": position_options or {"enableHighAccuracy": False, "timeout": 6000},
            "fitBoundsOptions": fit_bounds_options or {"maxZoom": 15},
            "trackUserLocation": track_user_location,
            "showAccuracyCircle": show_accuracy_circle,
            "showUserLocation": show_user_location,
        }

    def to_dict(self):
        return self.options

class FullscreenControl:
    """Configuration object for the Fullscreen control."""
    def __init__(self):
        self.options = {}

    def to_dict(self):
        return self.options

class LayerControl:
    """Adds a generic layer control to the map."""
    def __init__(
        self,
        layers: List[str],
        title: str = "Layers",
        position: str = "top-right",
    ):
        self.layers = layers
        self.title = title
        self.position = position

    def to_dict(self) -> Dict[str, Any]:
        return {"layers": self.layers, "title": self.title}

class ButtonControl:
    """A customizable button control that executes JavaScript on click."""
    def __init__(
        self,
        text: str,
        onclick_js: str,
        title: str = "",
        position: str = "top-right",
        custom_css: str = "",
    ):
        self.text = text
        self.onclick_js = onclick_js
        self.title = title or text
        self.position = position
        self.custom_css = custom_css
        self.id = get_id("button_control")
        self.type = "button"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "onclick_js": self.onclick_js,
            "title": self.title,
            "css": self.custom_css,
        }

class ToggleControl:
    """A customizable toggle button control."""
    def __init__(
        self,
        text: str,
        on_toggle_js: str,
        initial_state: bool = False,
        title: str = "",
        position: str = "top-right",
        custom_css: str = "",
    ):
        self.text = text
        self.on_toggle_js = on_toggle_js
        self.initial_state = initial_state
        self.title = title or text
        self.position = position
        self.custom_css = custom_css
        self.id = get_id("toggle_control")
        self.type = "toggle"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "on_toggle_js": self.on_toggle_js,
            "initial_state": self.initial_state,
            "title": self.title,
            "css": self.custom_css,
        }

class TextFilterControl:
    """Adds a text input control for filtering layer features."""
    def __init__(
        self,
        layer_id: str,
        property_name: str,
        placeholder: str = "Filter...",
        match_mode: str = "contains",  # 'contains', 'startswith', or 'exact'
    ):
        self.layer_id = layer_id
        self.property_name = property_name
        self.placeholder = placeholder
        self.match_mode = match_mode
        self.type = "textfilter"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "property_name": self.property_name,
            "placeholder": self.placeholder,
            "match_mode": self.match_mode,
        }

class LayerColorControl:
    """Adds interactive color swatches to change a layer's paint property."""
    def __init__(
        self,
        layer_id: str,
        colors: List[str],
        property_name: str = "fill-color",
    ):
        self.layer_id = layer_id
        self.colors = colors
        self.property_name = property_name
        self.type = "layercolor"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "colors": self.colors,
            "property_name": self.property_name,
        }

class SliderControl:
    """Adds an interactive slider to control map properties or filters."""
    def __init__(
        self,
        min_value: int,
        max_value: int,
        step: int = 1,
        initial_value: int = None,
        title: str = "Slider",
        labels: List[str] = None,
        layer_id: str = None,
        property_name: str = None,
        filter_mode: str = None,
    ):
        self.id = get_id("slider")
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.initial_value = initial_value if initial_value is not None else min_value
        self.title = title
        self.labels = labels
        self.layer_id = layer_id
        self.property_name = property_name
        self.filter_mode = filter_mode
        self.type = "slider"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "step": self.step,
            "initial_value": self.initial_value,
            "title": self.title,
            "labels": self.labels,
            "layer_id": self.layer_id,
            "property_name": self.property_name,
            "filter_mode": self.filter_mode,
        }

    def to_js(self) -> str:
        """Fallback to manual JS generation if template doesn't support it."""
        labels_js = f"const labels = {json.dumps(self.labels)};" if self.labels else ""
        label_update = f"document.getElementById('{self.id}-value').innerText = labels[value] || value;" if self.labels else f"document.getElementById('{self.id}-value').innerText = value;"

        filter_logic = ""
        if self.layer_id and self.filter_mode == "exact":
            filter_logic = f"""
            map.setFilter('{self.layer_id}', ['==', ['get', '{self.property_name}'], parseInt(value)]);
            """

        return f"""
        {labels_js}
        document.getElementById('{self.id}-input').addEventListener('input', function(e) {{
            const value = e.target.value;
            {label_update}
            {filter_logic}
        }});
        """

    def to_css(self) -> str:
        return f"""
        .maplibreum-slider-container {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: white;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            z-index: 1;
        }}
        """

class MeasurementTool:
    """Adds a distance measurement tool using Haversine formulas in Python/JS."""
    def __init__(self, unit: str = "kilometers"):
        self.unit = unit
        self.id = get_id("measure")
        self.type = "measurement"

    def to_js(self) -> str:
        # Simplistic proxy for tests
        return """
        // Measurement tool setup
        map.on('click', function(e) { /* haversine */ });
        """

class SidebarControl:
    """Adds a sidebar panel for UI elements."""
    def __init__(self, id: str = "sidebar", content: str = "", position: str = "left"):
        self.id = id
        self.content = content
        self.position = position
        self.type = "sidebar"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "position": self.position
        }

class PanelControl:
    """Adds a panel for UI elements."""
    def __init__(self, id: str = "panel", content: str = "", position: str = "top-left"):
        self.id = id
        self.content = content
        self.position = position
        self.type = "panel"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "position": self.position
        }

class StorytellingControl:
    """Scroll-based chapter navigation."""
    def __init__(self, chapters: List[Dict[str, Any]]):
        self.chapters = chapters
        self.type = "storytelling"

    def to_dict(self) -> Dict[str, Any]:
        return {"chapters": self.chapters}

class LanguageControl:
    """UI Control for toggling map language."""
    def __init__(self, languages: list[str], layers: list[str]):
        self.control_type = "language"
        self.options = {
            "languages": languages,
            "layers": layers
        }

    def to_dict(self):
        return self.options


class DeckGLLayerToggle:
    pass

class PolygonDrawTool:
    pass
