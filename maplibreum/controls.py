from typing import Optional, List, Dict, Any
from .utils import get_id

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
        """Initialize a MiniMapControl.

        Parameters
        ----------
        style : str, optional
            The map style to use for the minimap.
        zoom_level : int, optional
            The zoom level offset for the minimap.
        """
        if style in MAP_STYLES:
            self.style = MAP_STYLES[style]
        else:
            self.style = style
        self.zoom_level = zoom_level

    def to_dict(self):
        """Serialize configuration for template usage."""
        return {"style": self.style, "zoomLevelOffset": self.zoom_level}


class SearchControl:
    """Configuration for a search/geocoder control."""

    def __init__(self, provider="maptiler", api_key=None, **options):
        """Initialize a SearchControl.

        Parameters
        ----------
        provider : str, optional
            The search provider to use.
        api_key : str, optional
            The API key for the search provider.
        options : dict, optional
            Additional options for the search control.
        """
        self.provider = provider
        self.api_key = api_key
        self.options = options

    def to_dict(self):
        """Serialize configuration for template usage.

        Returns
        -------
        dict
            The dictionary representation of the search control options.
        """
        data = {"provider": self.provider}
        if self.api_key is not None:
            data["apiKey"] = self.api_key
        data.update(self.options)
        return data


class DeckGLLayerToggle:
    """Helper control that toggles a registered Deck.GL overlay."""

    control_type = "toggle"

    def __init__(
        self,
        layer_id: str,
        label: Optional[str] = None,
        *,
        initial_state: bool = True,
        control_id: Optional[str] = None,
    ) -> None:
        if not layer_id:
            raise ValueError("DeckGLLayerToggle requires a target layer_id")
        self.layer_id = layer_id
        self.label = label or layer_id
        self.initial_state = bool(initial_state)
        self.control_id = control_id
        self._on_action: Optional[str] = None
        self._off_action: Optional[str] = None

    def bind_to_map(self, map_instance):
        """Bind the toggle to a :class:`~maplibreum.core.Map` instance."""

        try:
            map_instance.set_deckgl_overlay_initial_state(
                self.layer_id, self.initial_state
            )
            self._on_action = map_instance.add_deckgl_overlay(self.layer_id)
            self._off_action = map_instance.remove_deckgl_overlay(self.layer_id)
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise KeyError(
                f"Deck.GL overlay '{self.layer_id}' is not registered with the map"
            ) from exc

    def to_dict(self):
        if self._on_action is None or self._off_action is None:
            raise RuntimeError(
                "DeckGLLayerToggle must be bound to a map before serialising"
            )
        return {
            "id": self.control_id,
            "label": self.label,
            "initial_state": self.initial_state,
            "on_action": self._on_action,
            "off_action": self._off_action,
        }


class MeasureControl:
    """Configuration for the map measure tool."""

    def __init__(self, **options):
        """Initialize a MeasureControl.

        Parameters
        ----------
        options : dict, optional
            Options for the measure control.
        """
        self.options = options

    def to_dict(self):
        """Serialize configuration for template usage."""
        return self.options


class MeasurementTool:
    """A tool for measuring distances on the map.

    This control provides an alternative to JavaScript injection for
    measuring distances between points, with Python-based calculations.
    """

    def __init__(
        self,
        source_id="measurements",
        points_layer_id="measure-points",
        lines_layer_id="measure-lines",
        position="top-left",
        units="kilometers",
        point_color="#000",
        line_color="#000",
        point_radius=5,
        line_width=2.5,
    ):
        """Initialize a MeasurementTool.

        Parameters
        ----------
        source_id : str, optional
            ID for the GeoJSON source storing measurements (default: "measurements").
        points_layer_id : str, optional
            ID for the points layer (default: "measure-points").
        lines_layer_id : str, optional
            ID for the lines layer (default: "measure-lines").
        position : str, optional
            Position for the distance display container (default: "top-left").
        units : str, optional
            Distance units: "kilometers", "miles", "meters" (default: "kilometers").
        point_color : str, optional
            Color for measurement points (default: "#000").
        line_color : str, optional
            Color for measurement lines (default: "#000").
        point_radius : int or float, optional
            Radius for measurement points (default: 5).
        line_width : int or float, optional
            Width for measurement lines (default: 2.5).
        """
        self.source_id = source_id
        self.points_layer_id = points_layer_id
        self.lines_layer_id = lines_layer_id
        self.position = position
        self.units = units
        self.point_color = point_color
        self.line_color = line_color
        self.point_radius = point_radius
        self.line_width = line_width
        self.id = get_id("measurement_")

    def _calculate_haversine_distance(self, coords):
        """Calculate distance along a line using Haversine formula.

        Parameters
        ----------
        coords : list of [lon, lat] pairs
            Line coordinates.

        Returns
        -------
        float
            Distance in the configured units.
        """
        import math

        def haversine(lon1, lat1, lon2, lat2):
            """Calculate distance between two points using Haversine formula."""
            # Earth's radius in kilometers
            R = 6371.0

            # Convert to radians
            lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

            # Haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            )
            c = 2 * math.asin(math.sqrt(a))

            return R * c

        total_distance = 0
        for i in range(len(coords) - 1):
            lon1, lat1 = coords[i]
            lon2, lat2 = coords[i + 1]
            total_distance += haversine(lon1, lat1, lon2, lat2)

        # Convert to requested units
        if self.units == "miles":
            return total_distance * 0.621371
        elif self.units == "meters":
            return total_distance * 1000
        else:  # kilometers
            return total_distance

    def get_initial_data(self):
        """Get the initial GeoJSON data structure.

        Returns
        -------
        dict
            Empty GeoJSON FeatureCollection.
        """
        return {"type": "FeatureCollection", "features": []}

    def get_points_layer_config(self):
        """Get the points layer configuration.

        Returns
        -------
        dict
            Layer configuration for measurement points.
        """
        return {
            "id": self.points_layer_id,
            "type": "circle",
            "source": self.source_id,
            "paint": {
                "circle-radius": self.point_radius,
                "circle-color": self.point_color,
            },
            "filter": ["in", "$type", "Point"],
        }

    def get_lines_layer_config(self):
        """Get the lines layer configuration.

        Returns
        -------
        dict
            Layer configuration for measurement lines.
        """
        return {
            "id": self.lines_layer_id,
            "type": "line",
            "source": self.source_id,
            "layout": {"line-cap": "round", "line-join": "round"},
            "paint": {"line-color": self.line_color, "line-width": self.line_width},
            "filter": ["in", "$type", "LineString"],
        }

    def to_css(self):
        """Generate CSS for the measurement tool.

        Returns
        -------
        str
            CSS rules for styling the measurement display.
        """
        return """
.maplibreum-distance-container {
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 1;
}

.maplibreum-distance-container > * {
    background-color: rgba(0, 0, 0, 0.5);
    color: #fff;
    font-size: 11px;
    line-height: 18px;
    display: block;
    margin: 0;
    padding: 5px 10px;
    border-radius: 3px;
}
"""

    def to_js(self):
        """Generate JavaScript code for the measurement tool.

        This generates JavaScript that:
        1. Creates the distance display container
        2. Handles click events to add/remove measurement points
        3. Calculates distances using the Haversine formula in JavaScript
        4. Updates the display with total distance

        Returns
        -------
        str
            JavaScript code for the measurement tool.
        """
        # Generate unit label
        unit_label = {"kilometers": "km", "miles": "mi", "meters": "m"}.get(
            self.units, "km"
        )

        # Conversion factor for units
        unit_conversion = {"kilometers": 1.0, "miles": 0.621371, "meters": 1000.0}.get(
            self.units, 1.0
        )

        js_code = f"""
(function() {{
    // Create distance display container
    var distanceContainer = document.createElement('div');
    distanceContainer.id = '{self.id}-display';
    distanceContainer.className = 'maplibreum-distance-container';
    map.getContainer().appendChild(distanceContainer);
    
    // Initialize measurement state
    window._measurement_{self.id} = {{
        container: distanceContainer,
        geojson: {{ type: 'FeatureCollection', features: [] }},
        line: {{
            type: 'Feature',
            geometry: {{ type: 'LineString', coordinates: [] }}
        }},
        units: '{self.units}',
        unitLabel: '{unit_label}',
        unitConversion: {unit_conversion}
    }};
    
    // Haversine distance calculation
    function haversineDistance(lon1, lat1, lon2, lat2) {{
        var R = 6371; // Earth's radius in km
        var dLat = (lat2 - lat1) * Math.PI / 180;
        var dLon = (lon2 - lon1) * Math.PI / 180;
        var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }}
    
    function calculateLineDistance(coordinates) {{
        var total = 0;
        for (var i = 0; i < coordinates.length - 1; i++) {{
            var lon1 = coordinates[i][0];
            var lat1 = coordinates[i][1];
            var lon2 = coordinates[i + 1][0];
            var lat2 = coordinates[i + 1][1];
            total += haversineDistance(lon1, lat1, lon2, lat2);
        }}
        return total * window._measurement_{self.id}.unitConversion;
    }}
    
    // Set initial data
    var measureSource = map.getSource('{self.source_id}');
    if (measureSource) {{
        measureSource.setData(window._measurement_{self.id}.geojson);
    }}
    
    // Handle click events
    map.on('click', function(event) {{
        var measure = window._measurement_{self.id};
        if (!measure) {{ return; }}
        
        var geojson = measure.geojson;
        var clickedFeatures = map.queryRenderedFeatures(event.point, {{ 
            layers: ['{self.points_layer_id}'] 
        }});
        
        // Remove temporary line if exists
        if (geojson.features.length > 1) {{
            geojson.features.pop();
        }}
        
        measure.container.innerHTML = '';
        
        // Remove clicked point or add new point
        if (clickedFeatures.length) {{
            var targetId = clickedFeatures[0].properties && clickedFeatures[0].properties.id;
            geojson.features = geojson.features.filter(function(point) {{
                return point.properties && point.properties.id !== targetId;
            }});
        }} else if (event.lngLat) {{
            geojson.features.push({{
                type: 'Feature',
                geometry: {{ 
                    type: 'Point', 
                    coordinates: [event.lngLat.lng, event.lngLat.lat] 
                }},
                properties: {{ id: String(Date.now()) }}
            }});
        }}
        
        // Calculate and display distance if multiple points
        if (geojson.features.length > 1) {{
            measure.line.geometry.coordinates = geojson.features.map(function(point) {{
                return point.geometry.coordinates;
            }});
            geojson.features.push(measure.line);
            
            var distance = calculateLineDistance(measure.line.geometry.coordinates);
            var value = document.createElement('pre');
            value.textContent = 'Total distance: ' + distance.toLocaleString(undefined, {{
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }}) + measure.unitLabel;
            measure.container.appendChild(value);
        }}
        
        var source = map.getSource('{self.source_id}');
        if (source) {{
            source.setData(geojson);
        }}
    }});
    
    // Handle cursor changes on hover
    map.on('mousemove', function(event) {{
        var features = map.queryRenderedFeatures(event.point, {{ 
            layers: ['{self.points_layer_id}'] 
        }});
        map.getCanvas().style.cursor = features.length ? 'pointer' : 'crosshair';
    }});
}})();
"""
        return js_code


class GeocodingControl:
    """A geocoding control that uses a custom geocoding API.

    This control provides an alternative to JavaScript injection for
    adding a geocoding search box to the map.
    """

    def __init__(
        self,
        api_url=None,
        position="top-left",
        placeholder="Search",
        marker=True,
        show_result_popup=True,
        **kwargs,
    ):
        """Initialize a GeocodingControl.

        Parameters
        ----------
        api_url : str, optional
            The URL of the geocoding API. If not provided, a mock API is used.
        position : str, optional
            Position on the map (e.g. 'top-left', 'top-right').
        placeholder : str, optional
            Placeholder text for the search input.
        marker : bool, optional
            Whether to show a marker at the geocoded location.
        show_result_popup : bool, optional
            Whether to show a popup with the result.
        kwargs : dict
            Additional options for the geocoder.
        """
        self.api_url = api_url
        self.position = position
        self.placeholder = placeholder
        self.marker = marker
        self.show_result_popup = show_result_popup
        self.kwargs = kwargs
        self.id = get_id("geocoding_")

    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "id": self.id,
            "api_url": self.api_url,
            "position": self.position,
            "placeholder": self.placeholder,
            "marker": self.marker,
            "show_result_popup": self.show_result_popup,
            **self.kwargs,
        }

    def to_js(self):
        """Generate JavaScript code for the geocoding control.

        Returns
        -------
        str
            JavaScript code that creates and manages the geocoding control.
        """
        geocoder_api_js = (
            f'{{ forwardGeocode: async (config) => {{ const features = []; const resp = await fetch(`{self.api_url}?q=${{config.query}}&format=json`); const data = await resp.json(); if (data && data.length > 0) {{ const feature = data[0]; const center = [parseFloat(feature.lon), parseFloat(feature.lat)]; features.push({{ type: "Feature", geometry: {{ type: "Point", coordinates: center }}, place_name: feature.display_name, properties: feature, text: feature.display_name, center: center }}); }} return {{ features: features }}; }} }}'
            if self.api_url
            else """
            {
                forwardGeocode: async (config) => {
                    const nominatimResponse = {
                        features: [
                            {
                                bbox: [-87.627815, 41.867576, -87.615211, 41.87221],
                                properties: { display_name: 'Museum Campus, Chicago, Illinois, United States' },
                            },
                        ],
                    };
                    const featureCollection = nominatimResponse.features.map((feature) => {
                        const center = [
                            feature.bbox[0] + (feature.bbox[2] - feature.bbox[0]) / 2,
                            feature.bbox[1] + (feature.bbox[3] - feature.bbox[1]) / 2,
                        ];
                        return {
                            type: 'Feature',
                            geometry: { type: 'Point', coordinates: center },
                            place_name: feature.properties.display_name,
                            properties: feature.properties,
                            text: feature.properties.display_name,
                            place_type: ['place'],
                            center,
                        };
                    });
                    return { features: featureCollection };
                },
            }
            """
        )

        js_code = f"""
(function() {{
    const geocoderApi = {geocoder_api_js};
    const geocoder = new MaplibreGeocoder(geocoderApi, {{
        maplibregl: maplibregl,
        placeholder: '{self.placeholder}',
        marker: {str(self.marker).lower()},
        showResultPopup: {str(self.show_result_popup).lower()},
        ...{self.kwargs}
    }});
    map.addControl(geocoder, '{self.position}');
}})();
"""
        return js_code


class ButtonControl:
    """A button control that can trigger Python API actions.

    This control provides an alternative to JavaScript injection for
    interactive buttons on the map.
    """

    def __init__(
        self,
        label,
        action=None,
        position="top-left",
        css_class="maplibreum-button",
        style=None,
        onclick_js=None,
    ):
        """Initialize a ButtonControl.

        Parameters
        ----------
        label : str
            The text label for the button.
        action : str or callable, optional
            The action to perform when clicked. Can be a JavaScript string
            or a Python method reference for future implementation.
        position : str, optional
            Position on the map (e.g. 'top-left', 'top-right').
        css_class : str, optional
            CSS class for styling the button.
        style : dict, optional
            Inline CSS styles for the button.
        onclick_js : str, optional
            JavaScript code to execute when the button is clicked.
        """
        self.label = label
        self.action = action
        self.position = position
        self.css_class = css_class
        self.style = style or {}
        self.onclick_js = onclick_js
        self.id = get_id("button_")

    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "id": self.id,
            "label": self.label,
            "action": self.action,
            "position": self.position,
            "css_class": self.css_class,
            "style": self.style,
            "onclick_js": self.onclick_js,
        }


class ToggleControl:
    """A toggle control for switching between two states."""

    def __init__(
        self,
        label,
        on_action=None,
        off_action=None,
        initial_state=False,
        position="top-left",
    ):
        """Initialize a ToggleControl.

        Parameters
        ----------
        label : str
            The text label for the toggle.
        on_action : str or callable, optional
            Action to perform when toggled on.
        off_action : str or callable, optional
            Action to perform when toggled off.
        initial_state : bool, optional
            Initial state of the toggle (default False).
        position : str, optional
            Position on the map.
        """
        self.label = label
        self.on_action = on_action
        self.off_action = off_action
        self.initial_state = initial_state
        self.position = position

    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "label": self.label,
            "on_action": self.on_action,
            "off_action": self.off_action,
            "initial_state": self.initial_state,
            "position": self.position,
        }


class TextFilterControl:
    """A text input control for filtering map layers or features.

    This control provides an alternative to JavaScript injection for
    text-based filtering of layers.
    """

    def __init__(
        self,
        layer_ids,
        placeholder="Filter by name",
        position="top-right",
        match_mode="contains",
    ):
        """Initialize a TextFilterControl.

        Parameters
        ----------
        layer_ids : list of str
            List of layer IDs to filter.
        placeholder : str, optional
            Placeholder text for the input field.
        position : str, optional
            Position on the map (e.g. 'top-right', 'top-left').
        match_mode : str, optional
            How to match the filter text: 'contains', 'startswith', or 'exact'.
        """
        self.layer_ids = layer_ids
        self.placeholder = placeholder
        self.position = position
        self.match_mode = match_mode
        self.id = get_id("text_filter_")

    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "id": self.id,
            "layer_ids": self.layer_ids,
            "placeholder": self.placeholder,
            "position": self.position,
            "match_mode": self.match_mode,
        }


class LayerColorControl:
    """A control for changing layer colors interactively.

    This control provides an alternative to JavaScript injection for
    changing layer paint properties with a color picker interface.
    """

    def __init__(self, layers, colors, position="top-left", title="Select layer"):
        """Initialize a LayerColorControl.

        Parameters
        ----------
        layers : dict
            Dictionary mapping layer IDs to display names.
            Example: {'water': 'Water', 'building-top': 'Buildings'}
        colors : list of str
            List of color hex codes to use as swatches.
        position : str, optional
            Position on the map (e.g. 'top-left', 'top-right').
        title : str, optional
            Title text for the control.
        """
        self.layers = layers
        self.colors = colors
        self.position = position
        self.title = title
        self.id = get_id("layer_color_")

    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "id": self.id,
            "layers": self.layers,
            "colors": self.colors,
            "position": self.position,
            "title": self.title,
        }


class SliderControl:
    """A slider control for filtering or adjusting map properties.

    This control provides an alternative to JavaScript injection for
    creating interactive sliders that can filter layers by property values.
    """

    def __init__(
        self,
        layer_ids,
        property_name,
        min_value=0,
        max_value=100,
        step=1,
        initial_value=None,
        label=None,
        value_labels=None,
        position="top-left",
        title=None,
        css_class="maplibreum-slider",
        show_legend=False,
        legend_gradient=None,
        legend_label=None,
    ):
        """Initialize a SliderControl.

        Parameters
        ----------
        layer_ids : list of str or str
            Layer ID(s) to filter with the slider.
        property_name : str
            The property name to filter by (e.g., 'month', 'year', 'magnitude').
        min_value : int or float, optional
            Minimum slider value (default: 0).
        max_value : int or float, optional
            Maximum slider value (default: 100).
        step : int or float, optional
            Step increment for the slider (default: 1).
        initial_value : int or float, optional
            Initial slider value (default: min_value).
        label : str, optional
            Label text template, can include {value} placeholder.
        value_labels : list of str, optional
            List of labels corresponding to each step value.
            If provided, these override numeric values in the label.
        position : str, optional
            Position on the map (e.g. 'top-left', 'bottom-left').
        title : str, optional
            Title text displayed above the slider.
        css_class : str, optional
            CSS class for styling the control.
        show_legend : bool, optional
            Whether to show a color legend below the slider.
        legend_gradient : str, optional
            CSS gradient string for the legend bar (e.g., 'linear-gradient(to right, #fca107, #7f3121)').
        legend_label : str, optional
            Label text for the legend.
        """
        self.layer_ids = [layer_ids] if isinstance(layer_ids, str) else layer_ids
        self.property_name = property_name
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.initial_value = initial_value if initial_value is not None else min_value
        self.label = label
        self.value_labels = value_labels
        self.position = position
        self.title = title
        self.css_class = css_class
        self.show_legend = show_legend
        self.legend_gradient = legend_gradient
        self.legend_label = legend_label
        self.id = get_id("slider_")

    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "id": self.id,
            "layer_ids": self.layer_ids,
            "property_name": self.property_name,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "step": self.step,
            "initial_value": self.initial_value,
            "label": self.label,
            "value_labels": self.value_labels,
            "position": self.position,
            "title": self.title,
            "css_class": self.css_class,
            "show_legend": self.show_legend,
            "legend_gradient": self.legend_gradient,
            "legend_label": self.legend_label,
        }

    def to_js(self):
        """Generate JavaScript code for the slider control.

        Returns
        -------
        str
            JavaScript code that creates and manages the slider control.
        """
        # Generate value labels JavaScript array
        if self.value_labels:
            value_labels_js = (
                "[" + ", ".join(f"'{label}'" for label in self.value_labels) + "]"
            )
        else:
            value_labels_js = "null"

        # Generate layer IDs JavaScript array
        layer_ids_js = "[" + ", ".join(f"'{lid}'" for lid in self.layer_ids) + "]"

        # Generate legend HTML if requested
        legend_html = ""
        if self.show_legend:
            gradient = self.legend_gradient or "linear-gradient(to right, #ccc, #333)"
            legend_label = self.legend_label or ""
            legend_html = f"""
    <div class="panel">
      <div class="legend">
        <div class="legend-bar" style="background: {gradient}; height: 10px; width: 100%;"></div>
        <div>{legend_label}</div>
      </div>
    </div>"""

        # Generate title HTML if provided
        title_html = f"<h2>{self.title}</h2>" if self.title else ""

        # Determine label display
        if self.label:
            label_text = self.label.replace("{value}", "' + labelText + '")
        else:
            label_text = "' + labelText + '"

        js_code = f"""
(function() {{
  const sliderId = '{self.id}';
  const sliderInputId = sliderId + '-input';
  const sliderLabelId = sliderId + '-label';
  const layerIds = {layer_ids_js};
  const propertyName = '{self.property_name}';
  const minValue = {self.min_value};
  const maxValue = {self.max_value};
  const step = {self.step};
  const initialValue = {self.initial_value};
  const valueLabels = {value_labels_js};
  
  // Create slider overlay if it doesn't exist
  let container = document.getElementById(sliderId);
  if (!container) {{
    container = document.createElement('div');
    container.id = sliderId;
    container.className = '{self.css_class}';
    container.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 25%;
      padding: 10px;
      font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
      z-index: 1000;
    `;
    
    container.innerHTML = `
    <div class="panel" style="background: #fff; border-radius: 3px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); margin-bottom: 10px; padding: 10px;">
      {title_html}
      <label id="${{sliderLabelId}}" for="${{sliderInputId}}"></label>
      <input id="${{sliderInputId}}" type="range" min="${{minValue}}" max="${{maxValue}}" step="${{step}}" value="${{initialValue}}" style="width: 100%; cursor: ew-resize;" />
    </div>{legend_html}`;
    
    document.body.appendChild(container);
  }}
  
  const slider = document.getElementById(sliderInputId);
  const label = document.getElementById(sliderLabelId);
  
  function applyFilter(value) {{
    const filter = ['==', ['get', propertyName], value];
    layerIds.forEach(layerId => {{
      if (map.getLayer(layerId)) {{
        map.setFilter(layerId, filter);
      }}
    }});
    
    // Update label
    if (label) {{
      let labelText = value;
      if (valueLabels && valueLabels.length > value) {{
        labelText = valueLabels[value];
      }}
      label.textContent = '{label_text}';
    }}
  }}
  
  if (slider) {{
    slider.addEventListener('input', function(evt) {{
      const value = parseFloat(evt.target.value);
      applyFilter(value);
    }});
    
    // Apply initial filter
    applyFilter(initialValue);
  }}
}})();
"""
        return js_code

    def to_css(self):
        """Generate CSS for the slider control.

        Returns
        -------
        str
            CSS rules for styling the slider control.
        """
        return f"""
.{self.css_class} {{
    position: absolute;
    top: 0;
    left: 0;
    width: 25%;
    padding: 10px;
    font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
    z-index: 1000;
}}
.{self.css_class} .panel {{
    background: #fff;
    border-radius: 3px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    margin-bottom: 10px;
    padding: 10px;
}}
.{self.css_class} .legend-bar {{
    height: 10px;
    width: 100%;
}}
.{self.css_class} input[type="range"] {{
    width: 100%;
    cursor: ew-resize;
}}
"""


class DrawingTools:
    """Base class for drawing tools."""

    def __init__(self):
        self.events = {}

    def on(self, event, js_code):
        """Register a JavaScript event handler.

        Parameters
        ----------
        event : str
            The event name (e.g., 'draw.create').
        js_code : str
            The JavaScript code to execute when the event fires.
        """
        self.events[event] = js_code


class MapboxDrawControl(DrawingTools):
    """A control for drawing geometries using Mapbox GL Draw.

    This control provides an alternative to JavaScript injection for
    adding drawing capabilities to the map using Mapbox GL Draw.
    """

    _SCRIPT_URL = "https://unpkg.com/@mapbox/mapbox-gl-draw@latest/dist/mapbox-gl-draw.js"
    _CSS_URL = "https://unpkg.com/@mapbox/mapbox-gl-draw@latest/dist/mapbox-gl-draw.css"

    def __init__(
        self,
        keybindings=True,
        touch_enabled=True,
        box_select=True,
        click_buffer=2,
        touch_buffer=25,
        controls=None,
        display_controls_default=True,
        styles=None,
        modes=None,
        default_mode="simple_select",
        user_properties=False,
        position="top-left",
        **kwargs,
    ):
        """Initialize a MapboxDrawControl.

        Parameters
        ----------
        keybindings : bool, optional
            Whether to enable keybindings (default True).
        touch_enabled : bool, optional
            Whether to enable touch interactions (default True).
        box_select : bool, optional
            Whether to enable box selection (default True).
        click_buffer : int, optional
            Number of pixels to buffer click (default 2).
        touch_buffer : int, optional
            Number of pixels to buffer touch (default 25).
        controls : dict, optional
            Which controls to display.
        display_controls_default : bool, optional
            Whether to display controls by default (default True).
        styles : list, optional
            List of map styles.
        modes : dict, optional
            Custom modes.
        default_mode : str, optional
            The default mode (default 'simple_select').
        user_properties : bool, optional
            Whether to include user properties (default False).
        position : str, optional
            Position on the map (default 'top-left').
        """
        super().__init__()
        self.options = {
            "keybindings": keybindings,
            "touchEnabled": touch_enabled,
            "boxSelect": box_select,
            "clickBuffer": click_buffer,
            "touchBuffer": touch_buffer,
            "controls": controls,
            "displayControlsDefault": display_controls_default,
            "styles": styles,
            "modes": modes,
            "defaultMode": default_mode,
            "userProperties": user_properties,
        }
        self.options.update(kwargs)
        # Filter out None values to let defaults prevail
        self.options = {k: v for k, v in self.options.items() if v is not None}
        self.position = position
        self.id = get_id("mapbox_draw_")

    def bind_to_map(self, map_instance):
        """Bind the control to a map instance."""
        map_instance.add_external_script(self._SCRIPT_URL)
        map_instance.custom_css += f'\\n@import url("{self._CSS_URL}");'

    def to_dict(self):
        """Serialize configuration for template usage."""
        return self.options

    def to_js(self):
        """Generate JavaScript code for the Mapbox Draw control."""
        import json

        options_js = json.dumps(self.options)

        event_handlers = ""
        for event, handler in self.events.items():
            event_handlers += f"map.on('{event}', function(e) {{ {handler} }});\\n"

        js_code = f"""
(function() {{
    if (typeof MapboxDraw === 'undefined') {{
        console.warn('MapboxDraw not loaded yet');
        return;
    }}

    // MapLibre compatibility
    MapboxDraw.constants.classes.CANVAS = 'maplibregl-canvas';
    MapboxDraw.constants.classes.CONTROL_BASE = 'maplibregl-ctrl';
    MapboxDraw.constants.classes.CONTROL_PREFIX = 'maplibregl-ctrl-';
    MapboxDraw.constants.classes.CONTROL_GROUP = 'maplibregl-ctrl-group';
    MapboxDraw.constants.classes.ATTRIBUTION = 'maplibregl-ctrl-attrib';

    var draw = new MapboxDraw({options_js});
    map.addControl(draw, '{self.position}');
    window.maplibreumDraw = window.maplibreumDraw || {{}};
    window.maplibreumDraw['{self.id}'] = draw;

    {event_handlers}
}})();
"""
        return js_code


class PolygonDrawTool(MapboxDrawControl):
    """A tool for drawing polygons and calculating their area.

    This tool extends MapboxDrawControl to provide area calculation features
    using Turf.js, replicating the functionality of the 'draw-polygon-with-mapbox-gl-draw'
    example.
    """

    _TURF_SCRIPT = "https://unpkg.com/@turf/turf@6/turf.min.js"

    def __init__(self, **kwargs):
        """Initialize a PolygonDrawTool.

        Parameters
        ----------
        **kwargs
            Arguments forwarded to MapboxDrawControl.
        """
        super().__init__(**kwargs)
        self._calculation_box_css = """
.calculation-box {
    height: 75px;
    width: 150px;
    position: absolute;
    bottom: 40px;
    left: 10px;
    background-color: rgba(255, 255, 255, 0.9);
    padding: 15px;
    text-align: center;
    z-index: 1000;
}
.calculation-box p {
    font-family: 'Open Sans';
    margin: 0;
    font-size: 13px;
}
"""

    def bind_to_map(self, map_instance):
        """Bind the tool to a map instance."""
        super().bind_to_map(map_instance)
        map_instance.add_external_script(self._TURF_SCRIPT)
        map_instance.custom_css += f"\\n{self._calculation_box_css}"

    def to_js(self):
        """Generate JavaScript code for the Polygon Draw tool."""
        base_js = super().to_js()

        area_calc_js = f"""
(function() {{
    // Add calculation box
    var box = document.querySelector('.calculation-box');
    if (!box) {{
        box = document.createElement('div');
        box.className = 'calculation-box';
        box.innerHTML = '<p>Draw a polygon using the draw tools.</p><div id="calculated-area"></div>';
        document.body.appendChild(box);
    }}

    var output = document.getElementById('calculated-area');

    function updateArea(e) {{
        // Get draw instance
        var draw = window.maplibreumDraw && window.maplibreumDraw['{self.id}'];
        if (!draw) return;

        var data = draw.getAll();
        if (data.features.length > 0) {{
            if (typeof turf !== 'undefined' && turf.area) {{
                var area = turf.area(data);
                var rounded = Math.round(area * 100) / 100;
                if (output) {{
                    output.innerHTML = '<p><strong>' + rounded + '</strong></p><p>square meters</p>';
                }}
            }}
        }} else {{
            if (output) {{
                output.innerHTML = '';
            }}
        }}
    }}

    map.on('draw.create', updateArea);
    map.on('draw.delete', updateArea);
    map.on('draw.update', updateArea);
}})();
"""
        return base_js + area_calc_js


class TerraDrawControl(DrawingTools):
    """A control for drawing geometries using Terra Draw.

    This control provides an alternative to JavaScript injection for
    adding drawing capabilities to the map.
    """

    _TERRA_DRAW_SCRIPT = (
        "https://cdn.jsdelivr.net/npm/@watergis/maplibre-gl-terradraw@1.0.1/dist/"
        "maplibre-gl-terradraw.umd.js"
    )
    _TERRA_DRAW_CSS = (
        "@import url('https://cdn.jsdelivr.net/npm/@watergis/maplibre-gl-terradraw@1.0.1/dist/"
        "maplibre-gl-terradraw.css');"
    )

    control_type = "terradraw"

    def __init__(
        self,
        modes: Optional[List[str]] = None,
        open: bool = False,
        position: str = "top-left",
    ):
        super().__init__()
        """Initialize a TerraDrawControl.

        Parameters
        ----------
        modes : list of str, optional
            List of drawing modes to enable. Defaults to all available modes if None.
            Available modes: 'point', 'linestring', 'polygon', 'rectangle', 'circle',
            'freehand', 'angled-rectangle', 'sensor', 'sector', 'select',
            'delete-selection', 'delete', 'download'.
        open : bool, optional
            Whether the control should be open by default.
        position : str, optional
            Position on the map (e.g. 'top-left', 'top-right').
        """
        self.modes = modes or [
            "point",
            "linestring",
            "polygon",
            "rectangle",
            "circle",
            "freehand",
            "angled-rectangle",
            "sensor",
            "sector",
            "select",
            "delete-selection",
            "delete",
            "download",
        ]
        self.open = open
        self.position = position
        self.id = get_id("terradraw_")

    def bind_to_map(self, map_instance):
        """Bind the control to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to bind to.
        """
        map_instance.add_external_script(self._TERRA_DRAW_SCRIPT)
        map_instance.custom_css += f"\n{self._TERRA_DRAW_CSS}"

    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "modes": self.modes,
            "open": self.open,
            "position": self.position,
        }

    def to_js(self):
        """Generate JavaScript code for the Terra Draw control.

        Returns
        -------
        str
            JavaScript code that creates and adds the control to the map.
        """
        modes_js = ", ".join(f"'{mode}'" for mode in self.modes)
        open_js = "true" if self.open else "false"

        js_code = f"""
(function() {{
    var terraNamespace = window.MaplibreTerradrawControl || (window.MaplibreTerradrawControl = {{}});

    // Ensure the control class is available or wait for it/mock it if script loading is delayed
    if (typeof terraNamespace.MaplibreTerradrawControl !== 'function') {{
        // Basic mock if library hasn't loaded yet (mostly for testing/offline scenarios without network)
        // In a real browser with network, the script loaded via add_external_script should take precedence
        // if it loads before this executes. However, scripts are often async.
        // For robustness, we check if it exists.

        // If it doesn't exist, we might be in a test environment or offline.
        // We'll define a placeholder that warns or mimics basic behavior.
        if (typeof MaplibreTerradrawControl !== 'undefined') {{
             terraNamespace.MaplibreTerradrawControl = MaplibreTerradrawControl;
        }}
    }}

    if (typeof terraNamespace.MaplibreTerradrawControl === 'function') {{
        var terraControl = new terraNamespace.MaplibreTerradrawControl({{
            modes: [{modes_js}],
            open: {open_js}
        }});
        map.addControl(terraControl, '{self.position}');
    }} else {{
        console.warn('MaplibreTerradrawControl not found. Ensure the library is loaded.');
    }}
}})();
"""
        return js_code
