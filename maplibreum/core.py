import json
import math
import os
from urllib.parse import quote
import uuid

from IPython.display import IFrame, display
from jinja2 import Environment, FileSystemLoader

from .expressions import get as expr_get, interpolate, var


# Predefined map styles
MAP_STYLES = {
    "basic": "https://demotiles.maplibre.org/style.json",
    "streets": "https://api.maptiler.com/maps/streets/style.json?key=YOUR_API_KEY",
    "satellite": "https://api.maptiler.com/maps/satellite/style.json?key=YOUR_API_KEY",
    "topo": "https://api.maptiler.com/maps/topo/style.json?key=YOUR_API_KEY",
    "dark": "https://api.maptiler.com/maps/darkmatter/style.json?key=YOUR_API_KEY",
    "light": "https://api.maptiler.com/maps/positron/style.json?key=YOUR_API_KEY",
}


class Tooltip:
    """Simple representation of a tooltip bound to a layer."""

    def __init__(self, text, options=None):
        self.text = text
        self.options = options or {}


class MiniMapControl:
    """Configuration object for the MiniMap plugin control."""

    def __init__(self, style="basic", zoom_level=6):
        if style in MAP_STYLES:
            self.style = MAP_STYLES[style]
        else:
            self.style = style
        self.zoom_level = zoom_level

    def to_dict(self):
        """Serialize configuration for template usage."""
        return {"style": self.style, "zoomLevelOffset": self.zoom_level}


class Map:
    _drawn_data = {}
    _event_callbacks = {}
    _marker_registry = {}
    def __init__(
        self,
        title="MapLibreum Map",
        map_style="basic",
        center=[0, 0],
        zoom=2,
        pitch=None,
        bearing=None,
        width="100%",
        height="500px",
        controls=None,
        layers=None,
        popups=None,
        tooltips=None,
        extra_js="",
        custom_css="",
        maplibre_version="3.4.0",
    ):
        """Initialize a map instance.

        Parameters
        ----------
        maplibre_version : str, optional
            Version of MapLibre GL JS to load. Defaults to "3.4.0".
        """
        self.title = title
        if map_style in MAP_STYLES:
            self.map_style = MAP_STYLES[map_style]
        else:
            self.map_style = map_style
        self.center = center
        self.zoom = zoom
        self.pitch = pitch
        self.bearing = bearing
        self.width = width
        self.height = height
        self.controls = controls if controls is not None else []
        self.sources = []
        self.layers = layers if layers is not None else []
        self.tile_layers = []
        self.overlays = []
        self.popups = popups if popups is not None else []
        self.tooltips = tooltips if tooltips is not None else []
        self.markers = []
        self.legends = []
        self.extra_js = extra_js
        self.custom_css = custom_css
        self.maplibre_version = maplibre_version
        self.layer_control = False
        self.cluster_layers = []
        self.bounds = None
        self.bounds_padding = None
        self.draw_control = False
        self.draw_control_options = {}
        self.lat_lng_popup = False
        self.events = []
        self.terrain = None
        self.fog = None
        self.float_images = []


        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.filters["tojson"] = lambda value: json.dumps(value)
        self.template = self.env.get_template("map_template.html")

        # Unique ID for the map (important if multiple maps displayed in a notebook)
        self.map_id = f"maplibreum_{uuid.uuid4().hex}"

    def fit_bounds(self, bounds, padding=None):
        """Store bounds and optional padding for later rendering.

        Parameters
        ----------
        bounds : list
            Bounds in the form ``[[west, south], [east, north]]``.
        padding : int or dict, optional
            Padding to apply in pixels. Can be a number or an options
            dictionary accepted by ``map.fitBounds``.
        """

        self.bounds = bounds
        self.bounds_padding = padding

    def add_control(self, control_type, position="top-right", options=None):
        """Add a UI control to the map.

        Parameters
        ----------
        control_type : str or MiniMapControl
            Type of control to add. Supported string values are ``'navigation'``,
            ``'scale'``, ``'fullscreen'``, ``'geolocate'``, ``'attribution'`` and
            ``'minimap'``. A :class:`MiniMapControl` instance can also be passed
            for the minimap control.
        position : str, optional
            Position on the map (e.g. ``'top-right'`` or ``'bottom-left'``).
        options : dict or MiniMapControl, optional
            Options forwarded to the underlying MapLibre GL control
            constructor. For example ``{"maxWidth": 80, "unit": "imperial"}``
            for the scale control or ``{"trackUserLocation": true}`` for the
            geolocate control. For the minimap control, either provide a
            ``MiniMapControl`` instance or a dictionary with ``style`` and
            ``zoomLevelOffset``.
        """
        if isinstance(control_type, MiniMapControl):
            self.controls.append(
                {
                    "type": "minimap",
                    "position": position,
                    "options": control_type.to_dict(),
                }
            )
            return

        if control_type == "minimap" and isinstance(options, MiniMapControl):
            options = options.to_dict()

        if options is None:
            options = {}
        self.controls.append(
            {"type": control_type, "position": position, "options": options}
        )

    def add_draw_control(self, options=None):
        """Enable a draw control on the map."""
        if options is None:
            options = {}
        self.draw_control = True
        self.draw_control_options = options

    def add_legend(self, legend):
        """Add a legend to the map."""
        if isinstance(legend, Legend):
            self.legends.append(legend)
        else:
            self.legends.append(Legend(legend))


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

        return layer_id

    def add_tile_layer(self, url, name=None, attribution=None, subdomains=None):
        """Add a raster tile layer to the map.

        Parameters
        ----------
        url : str
            Tile URL template. May contain ``{s}`` as a placeholder for
            subdomains.
        name : str, optional
            Name of the layer. If omitted, a unique ID is generated.
        attribution : str, optional
            Attribution text for the layer.
        subdomains : list of str, optional
            Subdomains to replace ``{s}`` in the URL. If provided and ``{s}``
            exists in ``url``, multiple tile URLs will be generated.
        """
        layer_id = name or f"tilelayer_{uuid.uuid4().hex}"

        if "{s}" in url and subdomains:
            tiles = [url.replace("{s}", s) for s in subdomains]
        else:
            tiles = [url]

        source = {
            "type": "raster",
            "tiles": tiles,
            "tileSize": 256,
        }
        if attribution:
            source["attribution"] = attribution
        layer = {"id": layer_id, "type": "raster", "source": layer_id}
        self.add_layer(layer, source=source)
        self.tile_layers.append({"id": layer_id, "name": name or layer_id})

    def register_overlay(self, layer_id, name=None, layers=None):
        """Register a non-tile overlay layer or group for the layer control."""
        overlay = {"id": layer_id, "name": name or layer_id}
        if layers:
            overlay["layers"] = layers
        self.overlays.append(overlay)

    def add_wms_layer(
        self,
        base_url,
        layers,
        name=None,
        styles="",
        version="1.1.1",
        format="image/png",
        transparent=True,
        attribution=None,
        extra_params=None,
    ):
        """Add a WMS layer to the map as raster tiles.

        Parameters
        ----------
        base_url : str
            Base URL of the WMS service without query parameters.
        layers : str
            Comma-separated layer names to request.
        name : str, optional
            Name of the layer. If omitted, a unique ID is generated.
        styles : str, optional
            Comma-separated style names.
        version : str, optional
            WMS version, defaults to ``1.1.1``.
        format : str, optional
            Image format for tiles, defaults to ``image/png``.
        transparent : bool, optional
            Whether the background should be transparent.
        attribution : str, optional
            Attribution text for the layer.
        extra_params : dict, optional
            Additional query parameters for the WMS request.
        """

        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": version,
            "layers": layers,
            "styles": styles,
            "format": format,
            "transparent": str(transparent).lower(),
            "width": 256,
            "height": 256,
            "bbox": "{bbox-epsg-3857}",
        }

        crs_param = "crs" if version == "1.3.0" else "srs"
        params[crs_param] = "EPSG:3857"

        if extra_params:
            params.update(extra_params)

        query = "&".join(
            f"{k}={quote(str(v), safe='{}')}" for k, v in params.items()
        )
        url = f"{base_url}?{query}"

        self.add_tile_layer(url, name=name, attribution=attribution)

    def add_dem_source(self, name, url, tile_size=512, attribution=None):
        """Add a raster-dem source for terrain rendering."""
        source = {"type": "raster-dem", "tiles": [url], "tileSize": tile_size}
        if attribution:
            source["attribution"] = attribution
        self.add_source(name, source)
        return name

    def set_terrain(self, source_name, exaggeration=1.0):
        """Enable 3D terrain using the given raster-dem source."""
        self.terrain = {"source": source_name, "exaggeration": exaggeration}

    def add_sky_layer(self, name="sky", paint=None, layout=None, before=None):
        """Add a sky layer to the map."""
        if paint is None:
            paint = {"sky-type": "atmosphere"}
        layer_definition = {"id": name, "type": "sky", "paint": paint}
        if layout:
            layer_definition["layout"] = layout
        self.add_layer(layer_definition, before=before)

    def set_fog(self, options=None):
        """Set global fog options for the map."""
        self.fog = options if options is not None else {}

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

    def add_tooltip(self, tooltip, layer_id=None, options=None):
        """Add a tooltip to the map."""
        if isinstance(tooltip, Tooltip):
            text = tooltip.text
            opts = tooltip.options
        else:
            text = tooltip
            opts = options or {}
        opts.setdefault("closeButton", False)
        self.tooltips.append({"text": text, "layer_id": layer_id, "options": opts})

    def add_lat_lng_popup(self):
        """Enable a popup showing latitude and longitude on click."""
        self.lat_lng_popup = True

    def on(self, event, callback):
        """Register a callback for a given map event."""
        if event not in self.events:
            self.events.append(event)
        self._event_callbacks.setdefault(self.map_id, {})[event] = callback

    def on_click(self, callback):
        """Convenience method for click events."""
        self.on("click", callback)

    def on_move(self, callback):
        """Convenience method for move events."""
        self.on("move", callback)

    def add_marker(
        self,
        coordinates=None,
        popup=None,
        color="#007cbf",
        cluster=None,
        icon=None,
        tooltip=None,
        draggable=False,
    ):

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
        cluster : MarkerCluster, optional
            Marker cluster to which the marker will be added. When provided,
            the marker is added to the cluster instead of directly to the map.
        icon : Icon, optional
            Custom icon for the marker. If provided, ``color`` is ignored.
        tooltip : str or Tooltip, optional
            Text for a tooltip bound to the marker.
        draggable : bool, optional
            Whether the marker should be draggable.
        """
        if coordinates is None:
            coordinates = self.center

        marker = Marker(
            coordinates=coordinates,
            popup=popup,
            color=color,
            icon=icon,
            tooltip=tooltip,
            draggable=draggable,
        )
        if cluster:
            cluster.add_marker(marker)
            return marker
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

    def add_fill_extrusion_layer(
        self, name, source, paint=None, layout=None, before=None, filter=None
    ):
        """Add a fill-extrusion layer to the map."""
        if paint is None:
            paint = {
                "fill-extrusion-height": 10,
                "fill-extrusion-color": "#007cbf",
                "fill-extrusion-opacity": 0.6,
            }
        layer_definition = {
            "id": name,
            "type": "fill-extrusion",
            "paint": paint,
        }
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
            "heatmap-color": interpolate(
                "linear",
                var("heatmap-density"),
                [
                    (0, "rgba(0,0,255,0)"),
                    (0.2, "blue"),
                    (0.4, "cyan"),
                    (0.6, "lime"),
                    (0.8, "yellow"),
                    (1, "red"),
                ],
            ),
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
        map_options = {
            "container": "map",
            "style": self.map_style,
        }
        if self.bounds is None:
            map_options["center"] = self.center
            map_options["zoom"] = self.zoom
        if self.pitch is not None:
            map_options["pitch"] = self.pitch
        if self.bearing is not None:
            map_options["bearing"] = self.bearing

        include_minimap = any(c["type"] == "minimap" for c in self.controls)

        return self.template.render(
            title=self.title,
            map_options=map_options,
            bounds=self.bounds,
            bounds_padding=self.bounds_padding,
            sources=self.sources,
            controls=self.controls,
            include_minimap=include_minimap,
            layers=self.layers,
            tile_layers=self.tile_layers,
            overlays=self.overlays,
            layer_control=self.layer_control,
            popups=self.popups,
            tooltips=self.tooltips,
            markers=self.markers,
            legends=[legend.render() for legend in self.legends],
            cluster_layers=self.cluster_layers,
            extra_js=self.extra_js,
            custom_css=final_custom_css,
            draw_control=self.draw_control,
            draw_control_options=self.draw_control_options,
            maplibre_version=self.maplibre_version,
            map_id=self.map_id,
            lat_lng_popup=self.lat_lng_popup,
            events=self.events,
            terrain=self.terrain,
            fog=self.fog,
            float_images=self.float_images,
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

    @classmethod
    def _store_drawn_features(cls, map_id, geojson_str):
        cls._drawn_data[map_id] = json.loads(geojson_str)

    @classmethod
    def _handle_event(cls, map_id, event, data_json):
        callback = cls._event_callbacks.get(map_id, {}).get(event)
        if callback:
            data = json.loads(data_json)
            callback(data)

    @classmethod
    def _register_marker(cls, map_id, marker):
        cls._marker_registry.setdefault(map_id, {})[marker.id] = marker

    @classmethod
    def _update_marker_coords(cls, map_id, marker_id, lng, lat):
        marker = cls._marker_registry.get(map_id, {}).get(marker_id)
        if marker:
            marker.coordinates = [lng, lat]

    @property
    def drawn_features(self):
        return self._drawn_data.get(self.map_id)


class MarkerCluster:
    """Group markers into clusters using MapLibre's built-in clustering."""

    def __init__(self, name=None, cluster_radius=50, cluster_max_zoom=14):
        self.name = name or f"markercluster_{uuid.uuid4().hex}"
        self.cluster_radius = cluster_radius
        self.cluster_max_zoom = cluster_max_zoom
        self.features = []
        self.map = None
        self.source_name = None
        self.cluster_layer_id = None
        self.count_layer_id = None
        self.unclustered_layer_id = None

    def add_marker(self, marker):
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": marker.coordinates},
            "properties": {"color": marker.color},
        }
        self.features.append(feature)
        if self.map and self.source_name:
            for src in self.map.sources:
                if src["name"] == self.source_name:
                    src["definition"]["data"]["features"] = self.features
                    break

    def add_to(self, map_instance):
        self.map = map_instance
        self.source_name = f"{self.name}_source"
        source = {
            "type": "geojson",
            "data": {"type": "FeatureCollection", "features": self.features},
            "cluster": True,
            "clusterRadius": self.cluster_radius,
            "clusterMaxZoom": self.cluster_max_zoom,
        }
        map_instance.add_source(self.source_name, source)

        self.cluster_layer_id = f"{self.name}_clusters"
        cluster_layer = {
            "id": self.cluster_layer_id,
            "type": "circle",
            "source": self.source_name,
            "filter": ["has", "point_count"],
            "paint": {
                "circle-color": "#51bbd6",
                "circle-radius": [
                    "step",
                    expr_get("point_count"),
                    20,
                    100,
                    30,
                    750,
                    40,
                ],
            },
        }
        map_instance.add_layer(cluster_layer)

        self.count_layer_id = f"{self.name}_cluster-count"
        count_layer = {
            "id": self.count_layer_id,
            "type": "symbol",
            "source": self.source_name,
            "filter": ["has", "point_count"],
            "layout": {
                "text-field": expr_get("point_count_abbreviated"),
                "text-font": ["Arial Unicode MS Bold"],
                "text-size": 12,
            },
        }
        map_instance.add_layer(count_layer)

        self.unclustered_layer_id = f"{self.name}_unclustered"
        unclustered = {
            "id": self.unclustered_layer_id,
            "type": "circle",
            "source": self.source_name,
            "filter": ["!", ["has", "point_count"]],
            "paint": {
                "circle-color": ["coalesce", expr_get("color"), "#007cbf"],
                "circle-radius": 8,
                "circle-stroke-width": 1,
                "circle-stroke-color": "#fff",
            },
        }
        map_instance.add_layer(unclustered)

        map_instance.cluster_layers.append(
            {"source": self.source_name, "cluster_layer": self.cluster_layer_id}
        )
        return self


class Icon:
    """Representation of a map icon used for symbol markers.

    Parameters
    ----------
    icon_image : str
        Name of the image to use for the icon.
    icon_size : float, optional
        Size of the icon relative to its original resolution.
    icon_anchor : str, optional
        Part of the icon that should be placed at the marker's geographical
        location (e.g. ``"bottom"``).
    """

    def __init__(self, icon_image, icon_size=None, icon_anchor=None):
        self.icon_image = icon_image
        self.icon_size = icon_size
        self.icon_anchor = icon_anchor


class Marker:
    def __init__(
        self,
        coordinates,
        popup=None,
        color="#007cbf",
        icon=None,
        tooltip=None,
        draggable=False,
    ):
        self.coordinates = coordinates
        self.popup = popup
        self.color = color
        self.icon = icon
        self.tooltip = tooltip
        self.draggable = draggable
        self.id = None

    def add_to(self, map_instance):
        if isinstance(map_instance, MarkerCluster):
            if self.draggable:
                raise ValueError("Draggable markers cannot be added to a cluster")
            map_instance.add_marker(self)
            return self

        if self.draggable:
            self.id = f"marker_{uuid.uuid4().hex}"
            map_instance.markers.append(
                {
                    "id": self.id,
                    "coordinates": self.coordinates,
                    "color": self.color,
                    "popup": self.popup,
                    "tooltip": self.tooltip,
                    "draggable": True,
                }
            )
            Map._register_marker(map_instance.map_id, self)
            return self

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
        if self.icon:
            layer = {
                "id": layer_id,
                "type": "symbol",
                "source": layer_id,
                "layout": {
                    "icon-image": self.icon.icon_image,
                },
            }
            if self.icon.icon_size is not None:
                layer["layout"]["icon-size"] = self.icon.icon_size
            if self.icon.icon_anchor is not None:
                layer["layout"]["icon-anchor"] = self.icon.icon_anchor
        else:
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
        if self.tooltip:
            map_instance.add_tooltip(self.tooltip, layer_id=layer_id)
        

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
            return expr_get(prop, ["properties"])

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
        fill_opacity=0.5,
        popup=None,
        tooltip=None,
    ):
        self.location = location
        self.radius = radius
        self.color = color
        self.fill = fill
        self.fill_color = fill_color if fill_color else color
        self.fill_opacity = fill_opacity
        self.popup = popup
        self.tooltip = tooltip

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
        self.location = location
        self.radius = radius
        self.color = color
        self.fill = fill
        self.fill_color = fill_color if fill_color else color
        self.fill_opacity = fill_opacity
        self.popup = popup
        self.tooltip = tooltip

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
    def __init__(self, locations, color="#3388ff", weight=2, popup=None, tooltip=None):
        self.locations = locations
        self.color = color
        self.weight = weight
        self.popup = popup
        self.tooltip = tooltip

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
        if self.tooltip:
            map_instance.add_tooltip(self.tooltip, layer_id=layer_id)


class Polygon:
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
        self.locations = locations
        self.color = color
        self.weight = weight
        self.fill = fill
        self.fill_color = fill_color if fill_color else color
        self.fill_opacity = fill_opacity
        self.popup = popup
        self.tooltip = tooltip

    def add_to(self, map_instance):
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


class ImageOverlay:
    """Overlay a georeferenced image on the map."""

    def __init__(
        self,
        image,
        bounds=None,
        coordinates=None,
        opacity=1.0,
        attribution=None,
        name=None,
    ):
        """Create an ImageOverlay.

        Parameters
        ----------
        image : str
            URL or local path to the image.
        bounds : list, optional
            Bounds of the image as ``[west, south, east, north]`` or
            ``[[west, south], [east, north]]``.
        coordinates : list, optional
            Four corner coordinates of the image specified as
            ``[[west, north], [east, north], [east, south], [west, south]]``.
            If provided, ``bounds`` is ignored.
        opacity : float, optional
            Opacity of the raster layer, defaults to ``1.0``.
        attribution : str, optional
            Attribution text for the source.
        name : str, optional
            Layer identifier. If omitted, a unique one is generated.
        """

        self.image = image
        self.attribution = attribution
        self.opacity = opacity
        self.name = name or f"imageoverlay_{uuid.uuid4().hex}"

        if coordinates is not None:
            self.coordinates = coordinates
        elif bounds is not None:
            if len(bounds) == 2 and all(len(b) == 2 for b in bounds):
                west, south = bounds[0]
                east, north = bounds[1]
            else:
                west, south, east, north = bounds
            self.coordinates = [
                [west, north],
                [east, north],
                [east, south],
                [west, south],
            ]
        else:
            raise ValueError("Either coordinates or bounds must be provided")

    def add_to(self, map_instance):
        source = {
            "type": "image",
            "url": self.image,
            "coordinates": self.coordinates,
        }
        if self.attribution:
            source["attribution"] = self.attribution

        layer = {"id": self.name, "type": "raster", "source": self.name}
        if self.opacity is not None:
            layer["paint"] = {"raster-opacity": self.opacity}

        map_instance.add_layer(layer, source=source)
        return self


class FloatImage:
    """Add a floating image to the map."""

    def __init__(self, image_url, bottom=None, left=None, width=None):
        self.image_url = image_url
        self.bottom = bottom
        self.left = left
        self.width = width

    def add_to(self, map_instance):
        map_instance.float_images.append(self)
        return self


class VideoOverlay:
    """Overlay a georeferenced video on the map."""

    def __init__(
        self,
        videos,
        bounds=None,
        coordinates=None,
        opacity=1.0,
        attribution=None,
        name=None,
    ):
        """Create a VideoOverlay.

        Parameters
        ----------
        videos : str or list
            URL or local path to the video, or a list of URLs for different
            formats.
        bounds : list, optional
            Bounds of the video as ``[west, south, east, north]`` or
            ``[[west, south], [east, north]]``.
        coordinates : list, optional
            Four corner coordinates of the video specified as
            ``[[west, north], [east, north], [east, south], [west, south]]``.
            If provided, ``bounds`` is ignored.
        opacity : float, optional
            Opacity of the raster layer, defaults to ``1.0``.
        attribution : str, optional
            Attribution text for the source.
        name : str, optional
            Layer identifier. If omitted, a unique one is generated.
        """

        if isinstance(videos, str):
            self.urls = [videos]
        else:
            self.urls = list(videos)
        self.attribution = attribution
        self.opacity = opacity
        self.name = name or f"videooverlay_{uuid.uuid4().hex}"

        if coordinates is not None:
            self.coordinates = coordinates
        elif bounds is not None:
            if len(bounds) == 2 and all(len(b) == 2 for b in bounds):
                west, south = bounds[0]
                east, north = bounds[1]
            else:
                west, south, east, north = bounds
            self.coordinates = [
                [west, north],
                [east, north],
                [east, south],
                [west, south],
            ]
        else:
            raise ValueError("Either coordinates or bounds must be provided")

    def add_to(self, map_instance):
        source = {
            "type": "video",
            "urls": self.urls,
            "coordinates": self.coordinates,
        }
        if self.attribution:
            source["attribution"] = self.attribution

        layer = {"id": self.name, "type": "raster", "source": self.name}
        if self.opacity is not None:
            layer["paint"] = {"raster-opacity": self.opacity}

        map_instance.add_layer(layer, source=source)
        return self


class FeatureGroup:
    """Group multiple layers so they can be toggled together."""

    def __init__(self, name=None):
        self.name = name or f"featuregroup_{uuid.uuid4().hex}"
        self.sources = []
        self.layers = []
        self.popups = []
        self.tooltips = []
        self.layer_ids = []

    def add_source(self, name, definition):
        self.sources.append({"name": name, "definition": definition})

    def add_layer(self, layer_definition, source=None, before=None):
        if isinstance(source, str):
            layer_definition["source"] = source
        elif source is not None:
            source_name = f"source_{uuid.uuid4().hex}"
            self.add_source(source_name, source)
            layer_definition["source"] = source_name

        layer_id = layer_definition.get("id", f"layer_{uuid.uuid4().hex}")
        layer_definition["id"] = layer_id
        self.layers.append(
            {"id": layer_id, "definition": layer_definition, "before": before}
        )
        self.layer_ids.append(layer_id)
        return layer_id

    def add_popup(self, html, coordinates=None, layer_id=None, events=None, options=None):
        if options is None:
            options = {}
        if events is None:
            events = ["click"]
        self.popups.append(
            {
                "html": html,
                "coordinates": coordinates,
                "layer_id": layer_id,
                "events": events,
                "options": options,
            }
        )

    def add_tooltip(self, tooltip, layer_id=None, options=None):
        if isinstance(tooltip, Tooltip):
            text = tooltip.text
            opts = tooltip.options
        else:
            text = tooltip
            opts = options or {}
        opts.setdefault("closeButton", False)
        self.tooltips.append({"text": text, "layer_id": layer_id, "options": opts})

    def add_to(self, map_instance):
        for src in self.sources:
            map_instance.add_source(src["name"], src["definition"])
        for layer in self.layers:
            map_instance.add_layer(layer["definition"], before=layer["before"])
        for popup in self.popups:
            map_instance.add_popup(**popup)
        for tooltip in self.tooltips:
            map_instance.add_tooltip(
                tooltip["text"], layer_id=tooltip["layer_id"], options=tooltip["options"]
            )
        return self


class LayerControl:
    """Simple layer control to toggle tile and overlay layers."""

    def __init__(self):
        self.overlays = []

    def add_overlay(self, layer, name=None):
        """Register an overlay layer or group by ID and display name."""
        if isinstance(layer, FeatureGroup):
            self.overlays.append(
                {"id": layer.name, "name": name or layer.name, "layers": layer.layer_ids}
            )
        else:
            self.overlays.append({"id": layer, "name": name or layer})
        return self

    def add_to(self, map_instance):
        map_instance.layer_control = True
        if self.overlays:
            for ov in self.overlays:
                map_instance.register_overlay(ov["id"], ov["name"], ov.get("layers"))
        return self


class Legend:
    """Map legend supporting raw HTML or label/color pairs."""

    def __init__(self, content):
        if isinstance(content, str):
            self._html = content
        else:
            items = []
            for label, color in content:
                items.append(
                    f'<div><span style="background:{color}"></span>{label}</div>'
                )
            self._html = "".join(items)

    def render(self):
        return self._html

    def add_to(self, map_instance):
        map_instance.add_legend(self)
        return self


class LatLngPopup:
    """Display a popup with latitude and longitude when the map is clicked."""

    def add_to(self, map_instance):
        map_instance.add_lat_lng_popup()
        return self

