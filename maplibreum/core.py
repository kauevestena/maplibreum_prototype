import html
import json
import math
import os
import subprocess
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set
from urllib.parse import quote

from IPython.display import IFrame, display
from jinja2 import Environment, FileSystemLoader

from .babylon import BabylonLayer
from .cluster import ClusteredGeoJson, MarkerCluster
from .layers import Layer
from .three import ThreeLayer
from .threejs import ThreeJSLayer
from .deckgl import DeckGLLayer
from .custom import CustomGlobeLayer
from .expressions import get as expr_get
from .expressions import interpolate, var
from .markers import BeautifyIcon, DivIcon, Icon  # noqa: F401
from . import controls
from . import sources as source_wrappers
from .sources import Source as SourceDefinition
from .styles import MAP_STYLES
from .animation import AnimatedIcon
from .protocols import DEFAULT_PM_TILES_SCRIPT, PMTilesProtocol, PMTilesSource


class Tooltip:
    """Simple representation of a tooltip bound to a layer."""

    def __init__(self, text, options=None):
        """Initialize a Tooltip.

        Parameters
        ----------
        text : str
            The text content of the tooltip.
        options : dict, optional
            A dictionary of tooltip options.
        """
        self.text = text
        self.options = options or {}


class Popup:
    """Representation of a popup with optional Jinja2 templating."""

    _env = Environment(autoescape=True)

    def __init__(self, html=None, template=None):
        """Initialize a Popup.

        Parameters
        ----------
        html : str, optional
            The HTML content of the popup.
        template : str, optional
            A Jinja2 template string for the popup content.
        """
        self.html = html
        self.template = template

    def render(self, context=None):
        """Render the popup content.

        If a template is provided, it is rendered with the given context.
        Otherwise, the plain HTML is returned.

        Parameters
        ----------
        context : dict, optional
            Context for rendering the template.

        Returns
        -------
        str
            The rendered HTML content.
        """
        if self.template is not None:
            tmpl = self._env.from_string(self.template)
            return tmpl.render(context or {})
        return self.html or ""


class GeoJsonPopup:
    """Generate HTML snippets from GeoJSON feature properties."""

    def __init__(self, fields, aliases=None, labels=True, style=""):
        """Initialize a GeoJsonPopup.

        Parameters
        ----------
        fields : list or str
            A list of field names to display.
        aliases : list or str, optional
            A list of aliases for the field names.
        labels : bool, optional
            Whether to display labels for the fields.
        style : str, optional
            A CSS style string to apply to the popup.
        """
        self.fields = list(fields) if isinstance(fields, (list, tuple)) else [fields]
        if aliases is None:
            self.aliases = self.fields
        else:
            self.aliases = (
                list(aliases) if isinstance(aliases, (list, tuple)) else [aliases]
            )
        self.labels = labels
        self.style = style

    def render(self, feature):
        """Render the popup content from a GeoJSON feature.

        Parameters
        ----------
        feature : dict
            A GeoJSON feature.

        Returns
        -------
        str
            The rendered HTML content.
        """
        props = feature.get("properties", {})
        parts = []
        for field, alias in zip(self.fields, self.aliases):
            value = props.get(field, "")
            if self.labels:
                parts.append(f"<b>{alias}</b>: {value}")
            else:
                parts.append(str(value))
        html = "<br>".join(parts)
        if self.style:
            html = f'<div style="{self.style}">{html}</div>'
        return html


class GeoJsonTooltip(GeoJsonPopup):
    """Generate tooltips from GeoJSON feature properties."""

    def render(self, feature):  # pragma: no cover - same as popup rendering
        """Render the tooltip content from a GeoJSON feature.

        Parameters
        ----------
        feature : dict
            A GeoJSON feature.

        Returns
        -------
        str
            The rendered HTML content.
        """
        return super().render(feature)


@dataclass
class StateToggle:
    """Describe DOM state changes that should occur when an event fires."""

    selector: str
    class_name: Optional[str] = None
    state: Optional[bool] = None
    attribute: Optional[str] = None
    value: Any = None
    dataset: Optional[Dict[str, Any]] = None
    text: Any = None

    def __post_init__(self):
        if not self.selector:
            raise ValueError("StateToggle requires a CSS selector")
        if (
            self.class_name is None
            and self.attribute is None
            and self.dataset is None
            and self.text is None
        ):
            raise ValueError(
                "StateToggle needs a class_name, attribute, dataset, or text update"
            )
        if self.dataset is not None:
            if not isinstance(self.dataset, dict):
                raise TypeError("dataset must be a mapping of keys to values")
            self.dataset = {str(k): v for k, v in self.dataset.items()}
        if self.state is not None and not isinstance(self.state, bool):
            self.state = bool(self.state)

    def to_dict(self):
        """Return a JSON-serialisable representation."""

        payload = {"selector": self.selector}
        if self.class_name:
            payload["className"] = self.class_name
        if self.state is not None:
            payload["state"] = self.state
        if self.attribute:
            payload["attribute"] = self.attribute
        if self.value is not None:
            payload["value"] = self.value
        if self.dataset:
            payload["dataset"] = {k: str(v) for k, v in self.dataset.items()}
        if self.text is not None:
            payload["text"] = str(self.text)
        return payload


@dataclass
class EventBinding:
    """Representation of a MapLibre event binding produced from Python."""

    id: str
    event: str
    layer_id: Optional[str] = None
    js: Optional[str] = None
    send_to_python: bool = False
    toggles: list[StateToggle] = field(default_factory=list)
    once: bool = False

    def to_render_dict(self):
        """Convert to the structure used by the template."""

        return {
            "id": self.id,
            "event": self.event,
            "layer_id": self.layer_id,
            "js": self.js,
            "send_to_python": self.send_to_python,
            "state_toggles": [toggle.to_dict() for toggle in self.toggles],
            "once": self.once,
        }


# Re-export commonly used controls for convenience
MiniMapControl = controls.MiniMapControl
SearchControl = controls.SearchControl


_RTL_CALLBACK_UNSET = object()


class Map:
    """The main Map class."""

    _drawn_data = {}
    _event_callbacks = {}
    _marker_registry = {}
    _search_data = {}

    def __init__(
        self,
        title="MapLibreum Map",
        map_style="basic",
        center=[0, 0],
        zoom=2,
        pitch=None,
        bearing=None,
        elevation=None,
        center_clamped_to_ground=None,
        width="100%",
        height="500px",
        controls=None,
        layers=None,
        popups=None,
        tooltips=None,
        extra_js="",
        custom_css="",
        maplibre_version="3.4.0",
        projection=None,
        map_options=None,
        container_id=None,
    ):
        """Initialize a map instance.

        Parameters
        ----------
        maplibre_version : str, optional
            Version of MapLibre GL JS to load. Defaults to "3.4.0".
        """
        self.title = title
        if isinstance(map_style, str) and map_style in MAP_STYLES:
            self.map_style = MAP_STYLES[map_style]
        else:
            self.map_style = map_style
        self.center = center
        self.zoom = zoom
        self.pitch = pitch
        self.bearing = bearing
        self.elevation = elevation
        self.center_clamped_to_ground = center_clamped_to_ground
        self.width = width
        self.height = height
        self.controls = controls if controls is not None else []
        self.sources = []
        self.layers = layers if layers is not None else []
        self.deckgl_overlays: List[Dict[str, Any]] = []
        self._deckgl_overlay_lookup: Dict[str, Dict[str, Any]] = {}
        self.tile_layers = []
        self.overlays = []
        self.popups = popups if popups is not None else []
        self.tooltips = tooltips if tooltips is not None else []
        self.markers = []
        self.marker_css = []
        self.legends = []
        self.extra_js = extra_js
        self._extra_js_snippets: List[str] = []
        self.custom_css = custom_css
        self.maplibre_version = maplibre_version
        self.additional_map_options = dict(map_options) if map_options else {}
        self.layer_control = False
        self.cluster_layers = []
        self.bounds = None
        self.bounds_padding = None
        self.draw_control = False
        self.draw_control_options = {}
        self.measure_control = False
        self.measure_control_options = {}
        self.measure_control_position = "top-left"
        self.lat_lng_popup = False
        self.events = []
        self.event_bindings = []
        self.terrain = None
        self.fog = None
        self.float_images = []
        self.images = []
        self.camera_actions = []
        self.time_dimension_data = None
        self.time_dimension_options = {}
        self._on_load_callbacks: List[str] = []
        self.animations: List[str] = []
        self.rtl_text_plugin: Optional[Dict[str, Any]] = None
        self.external_scripts: List[Dict[str, Any]] = []
        self._pmtiles_protocols: Dict[str, Dict[str, Any]] = {}
        self._pmtiles_protocol_scripts: Dict[str, str] = {}
        self._pmtiles_sources: List[Dict[str, Any]] = []
        self._pmtiles_script_urls: Set[str] = set()

        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.filters["tojson"] = lambda value: json.dumps(value)
        self.template = self.env.get_template("map_template.html")

        # Unique ID for the map (important if multiple maps displayed in a notebook)
        self.map_id = container_id or f"maplibreum_{uuid.uuid4().hex}"

        if projection is not None:
            self.set_projection(projection)

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

    def add_control(self, control, position="top-right", options=None):
        """Add a UI control to the map.
        Parameters
        ----------
        control : object or str
            Either a control instance or a known control alias such as ``"navigation"``.
        position : str, optional
            Position on the map (e.g. ``'top-right'`` or ``'bottom-left'``).
        options : dict, optional
            Additional configuration forwarded to the control when ``control``
            is provided as a string alias.
        """
        options = options or {}

        if isinstance(control, str):
            alias = control.lower()
            native = {"navigation", "scale", "fullscreen", "geolocate", "attribution"}
            if alias in native:
                control_type = alias
                control_options = options
            elif alias == "minimap":
                minimap = controls.MiniMapControl(**options)
                control_type = "minimap"
                control_options = minimap.to_dict()
            elif alias == "search":
                search = controls.SearchControl(**options)
                control_type = "search"
                control_options = search.to_dict()
            elif alias == "terrain":
                terrain = controls.TerrainControl(**options)
                control_type = "terrain"
                control_options = terrain.to_dict()
            elif alias == "globe":
                control_type = "globe"
                control_options = options
            else:
                raise ValueError(f"Unknown control alias '{control}'")
        else:
            if hasattr(control, "bind_to_map"):
                control.bind_to_map(self)
            if hasattr(control, "to_js"):
                self._extra_js_snippets.append(control.to_js())

            if hasattr(control, "to_css"):
                self.custom_css += f"\n{control.to_css()}"

            control_type = getattr(
                control,
                "control_type",
                control.__class__.__name__.lower().replace("control", ""),
            )
            control_options = control.to_dict()
            if options:
                control_options.update(options)

        self.controls.append(
            {"type": control_type, "position": position, "options": control_options}
        )

    def add_search_control(self, control=None, position="top-left", **options):
        if control is None:
            control = controls.SearchControl(**options)
        elif isinstance(control, dict):
            control = controls.SearchControl(**control)
        self.add_control(control, position)

    def add_draw_control(self, options=None):
        """Enable a draw control on the map."""
        if options is None:
            options = {}
        self.draw_control = True
        self.draw_control_options = options

        from .controls import MapboxDrawControl

        control = MapboxDrawControl(**options)

        # Add Jupyter integration
        update_js = """
        var data = draw.getAll();
        if (window.Jupyter && Jupyter.notebook && Jupyter.notebook.kernel) {
            var cmd = "from maplibreum.core import Map; Map._store_drawn_features('" + map.getContainer().id + "', '" + JSON.stringify(data).replace(/'/g, "\\\\'") + "')";
            Jupyter.notebook.kernel.execute(cmd);
        }
        """
        control.on("draw.create", update_js)
        control.on("draw.update", update_js)
        control.on("draw.delete", update_js)

        self.add_control(control)

    def add_measure_control(self, control=None, position="top-left", **options):
        if control is None:
            control = controls.MeasureControl(**options)
        elif isinstance(control, dict):
            control = controls.MeasureControl(**control)
        self.measure_control = True
        self.measure_control_options = control.to_dict()
        self.measure_control_position = position

    def add_legend(self, legend):
        """Add a legend to the map."""
        if isinstance(legend, Legend):
            self.legends.append(legend)
        else:
            self.legends.append(Legend(legend))

    def add_source(self, name, definition):
        """Add a source definition to the style.

        Parameters
        ----------
        name : str
            The name of the source.
        definition : dict or :class:`maplibreum.sources.Source`
            The source definition. Instances of :class:`~maplibreum.sources.Source`
            are converted to the underlying dictionary automatically so both the
            plain MapLibre dictionaries and the convenience wrappers are
            supported.
        """

        if isinstance(definition, SourceDefinition):
            payload = definition.to_dict()
        else:
            payload = definition

        self.sources.append({"name": name, "definition": payload})
        return name

    def add_layer(self, layer_definition, source=None, before=None):
        """Add a layer to the map.

        Parameters
        ----------
        layer_definition : dict
            A dictionary describing a MapLibre GL style layer.
        source : dict or str, optional
            A dictionary describing a MapLibre source, or a string
            referencing an existing source.
        before : str, optional
            The ID of an existing layer before which this layer should be
            placed.

        Returns
        -------
        str
            The ID of the added layer.
        """
        if isinstance(layer_definition, BabylonLayer):
            layer_id = layer_definition.id
            self.add_external_script("https://unpkg.com/babylonjs@5.42.2/babylon.js")
            self.add_external_script(
                "https://unpkg.com/babylonjs-loaders@5.42.2/babylonjs.loaders.min.js"
            )
            self.add_on_load_js(layer_definition.js_code)
            layer_definition = layer_definition.to_dict()
        elif isinstance(layer_definition, ThreeLayer):
            layer_id = layer_definition.id
            self.add_external_script(
                "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.js"
            )
            self.add_external_script(
                "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/js/loaders/GLTFLoader.js"
            )
            self.add_on_load_js(layer_definition.js_code)
            layer_definition = layer_definition.to_dict()
        elif isinstance(layer_definition, ThreeJSLayer):
            layer_id = layer_definition.id
            for script in layer_definition.scripts:
                self.add_external_script(script, defer=True)
            self.add_on_load_js(layer_definition.add_to(before_layer_id=before))
            return layer_id
        elif isinstance(layer_definition, DeckGLLayer):
            layer_id = layer_definition.id
            for script in layer_definition.scripts:
                self.add_external_script(script, defer=True)
            config = layer_definition.serialize(before_layer_id=before)
            config.setdefault("enabled", True)
            self._deckgl_overlay_lookup[layer_id] = config
            self.deckgl_overlays.append(config)
            self.layers.append(
                {
                    "id": layer_id,
                    "definition": None,
                    "before": before,
                    "kind": "deckgl_overlay",
                    "overlay": config,
                }
            )
            return layer_id
        elif isinstance(layer_definition, CustomGlobeLayer):
            if source is not None:
                raise ValueError("CustomGlobeLayer does not accept a source")
            return layer_definition.add_to(self, before=before)
        else:
            if isinstance(source, str):
                # Source is a string, so we assume it's a source name
                # that has already been added to the map.
                layer_definition["source"] = source
            elif source is not None:
                # Source is a dict or Source wrapper, so we add it to the map.
                source_name = f"source_{uuid.uuid4().hex}"
                self.add_source(source_name, source)
                layer_definition["source"] = source_name

            if isinstance(layer_definition, Layer):
                layer_definition = layer_definition.to_dict()

            layer_id = layer_definition.get("id", f"layer_{uuid.uuid4().hex}")
            layer_definition["id"] = layer_id

        self.layers.append(
            {"id": layer_id, "definition": layer_definition, "before": before}
        )

        return layer_id

    def set_deckgl_overlay_initial_state(self, overlay_id: str, enabled: bool) -> None:
        """Mark a Deck.GL overlay as enabled/disabled when the map loads."""

        config = self._deckgl_overlay_lookup.get(overlay_id)
        if config is None:
            raise KeyError(f"Unknown Deck.GL overlay '{overlay_id}'")
        config["enabled"] = bool(enabled)

    def add_deckgl_overlay(self, overlay_id: str) -> str:
        """Return JS snippet to activate a registered Deck.GL overlay."""

        if overlay_id not in self._deckgl_overlay_lookup:
            raise KeyError(f"Unknown Deck.GL overlay '{overlay_id}'")
        manager_expr = (
            "window.maplibreumDeckOverlayManagers && "
            f"window.maplibreumDeckOverlayManagers[{json.dumps(self.map_id)}]"
        )
        return (
            f"const overlayManager = {manager_expr};"
            f" if (overlayManager) {{ overlayManager.addOverlay({json.dumps(overlay_id)}); }}"
        )

    def remove_deckgl_overlay(self, overlay_id: str) -> str:
        """Return JS snippet to remove a registered Deck.GL overlay."""

        if overlay_id not in self._deckgl_overlay_lookup:
            raise KeyError(f"Unknown Deck.GL overlay '{overlay_id}'")
        manager_expr = (
            "window.maplibreumDeckOverlayManagers && "
            f"window.maplibreumDeckOverlayManagers[{json.dumps(self.map_id)}]"
        )
        return (
            f"const overlayManager = {manager_expr};"
            f" if (overlayManager) {{ overlayManager.removeOverlay({json.dumps(overlay_id)}); }}"
        )

    def add_tile_layer(
        self,
        url,
        name=None,
        attribution=None,
        subdomains=None,
        *,
        tile_size=256,
        min_zoom=None,
        max_zoom=None,
        bounds=None,
        scheme=None,
        volatile=None,
        **source_options,
    ):
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
        tile_size : int, optional
            Tile size in pixels. Defaults to ``256`` which matches the MapLibre
            GL JS default for raster sources.
        min_zoom, max_zoom : int, optional
            Optional zoom constraints forwarded to the underlying source.
        bounds : sequence of float, optional
            Geographic bounds of the tile set as ``[west, south, east, north]``.
        scheme : str, optional
            Tile scheme (``'xyz'`` or ``'tms'``).
        volatile : bool, optional
            Whether tiles may change frequently.
        **source_options
            Additional keyword arguments forwarded to
            :class:`maplibreum.sources.RasterSource` for advanced
            configuration.
        """

        layer_id = name or f"tilelayer_{uuid.uuid4().hex}"

        if "{s}" in url and subdomains:
            tiles = [url.replace("{s}", s) for s in subdomains]
        else:
            tiles = [url]

        source_kwargs = dict(source_options)
        if attribution is not None:
            source_kwargs["attribution"] = attribution

        source = source_wrappers.RasterSource(
            tiles=tiles,
            tile_size=tile_size,
            min_zoom=min_zoom,
            max_zoom=max_zoom,
            bounds=bounds,
            scheme=scheme,
            volatile=volatile,
            **source_kwargs,
        )

        layer = {"id": layer_id, "type": "raster", "source": layer_id}
        self.add_layer(layer, source=source)
        self.tile_layers.append({"id": layer_id, "name": name or layer_id})

    def register_overlay(self, layer_id, name=None, layers=None):
        """Register a non-tile overlay layer or group for the layer control."""
        overlay = {"id": layer_id, "name": name or layer_id}
        if layers:
            overlay["layers"] = layers
        self.overlays.append(overlay)

    def add_float_image(self, image_url, position="top-left", width=None):
        """Add a floating image anchored to a map corner.

        Parameters
        ----------
        image_url : str
            URL of the image to display.
        position : str, optional
            One of ``'top-left'``, ``'top-right'``, ``'bottom-left'`` or
            ``'bottom-right'``. Defaults to ``'top-left'``.
        width : int, optional
            Width of the image in pixels.
        """

        img = FloatImage(image_url, position=position, width=width)
        self.float_images.append(img)
        return img

    def add_external_script(
        self,
        src: str,
        *,
        defer: bool = False,
        async_: bool = False,
        module: bool = False,
        attributes: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """Load an additional JavaScript bundle before the map initialises.

        Parameters
        ----------
        src : str
            Absolute or relative URL of the script to include.
        defer : bool, optional
            Add the ``defer`` attribute so the browser defers execution until
            after parsing the document.
        async_ : bool, optional
            Add the ``async`` attribute for asynchronous loading.
        module : bool, optional
            Mark the script as an ES module by setting ``type="module"``.
        attributes : mapping, optional
            Extra HTML attributes (e.g. ``integrity``) to attach to the tag.
        """

        if not isinstance(src, str) or not src.strip():
            raise ValueError("add_external_script requires a script URL")

        attr_map: Dict[str, Any] = {}
        if defer:
            attr_map["defer"] = True
        if async_:
            attr_map["async"] = True
        if module:
            attr_map.setdefault("type", "module")

        if attributes is not None:
            if not isinstance(attributes, Mapping):
                raise TypeError("attributes must be a mapping of attribute names to values")
            for key, value in attributes.items():
                if value is False or value is None:
                    continue
                attr_map[str(key)] = True if value is True else str(value)

        self.external_scripts.append({"src": src, "attributes": attr_map})
        return src

    def _ensure_pmtiles_script(self, script_url: str) -> None:
        """Include the PMTiles runtime bundle only once."""

        if script_url in self._pmtiles_script_urls:
            return

        self.add_external_script(script_url)
        self._pmtiles_script_urls.add(script_url)

    def add_pmtiles_protocol(
        self, protocol: Optional[PMTilesProtocol] = None, **kwargs: Any
    ) -> PMTilesProtocol:
        """Register a :class:`PMTilesProtocol` for client-side initialisation."""

        if protocol is None:
            protocol = PMTilesProtocol(**kwargs)
        elif kwargs:
            raise TypeError(
                "Cannot pass keyword arguments when providing a PMTilesProtocol instance"
            )

        if not isinstance(protocol, PMTilesProtocol):
            raise TypeError("protocol must be a PMTilesProtocol instance")

        existing = self._pmtiles_protocols.get(protocol.name)
        if existing is not None:
            stored_script = self._pmtiles_protocol_scripts.get(protocol.name)
            if stored_script is not None and stored_script != protocol.script_url:
                raise ValueError(
                    f"Protocol '{protocol.name}' already registered with script {stored_script}"
                )
            existing_credentials = existing.get("credentials")
            if protocol.credentials is not None and protocol.credentials != existing_credentials:
                raise ValueError(
                    f"Protocol '{protocol.name}' already registered with different credentials"
                )
        else:
            payload = protocol.to_render_payload()
            self._pmtiles_protocols[protocol.name] = payload
            self._pmtiles_protocol_scripts[protocol.name] = protocol.script_url

        self._ensure_pmtiles_script(protocol.script_url)
        return protocol

    def add_pmtiles_source(
        self, source: Optional[PMTilesSource] = None, **kwargs: Any
    ) -> PMTilesSource:
        """Register a PMTiles archive so it is preloaded for MapLibre."""

        if source is None:
            source = PMTilesSource(**kwargs)
        elif kwargs:
            raise TypeError(
                "Cannot pass keyword arguments when providing a PMTilesSource instance"
            )

        if not isinstance(source, PMTilesSource):
            raise TypeError("source must be a PMTilesSource instance")

        protocol_payload = self._pmtiles_protocols.get(source.protocol)
        if protocol_payload is None:
            inferred = PMTilesProtocol(
                name=source.protocol,
                credentials=source.credentials,
                script_url=self._pmtiles_protocol_scripts.get(
                    source.protocol, DEFAULT_PM_TILES_SCRIPT
                ),
            )
            self.add_pmtiles_protocol(inferred)
            protocol_payload = self._pmtiles_protocols[source.protocol]
        elif (
            source.credentials is not None
            and protocol_payload.get("credentials") != source.credentials
        ):
            raise ValueError(
                f"Protocol '{source.protocol}' already registered with different credentials"
            )

        payload = source.to_render_payload()
        duplicate = any(
            existing["protocol"] == payload["protocol"]
            and existing["archive"] == payload["archive"]
            for existing in self._pmtiles_sources
        )
        if not duplicate:
            self._pmtiles_sources.append(payload)

        script_url = self._pmtiles_protocol_scripts.get(
            source.protocol, DEFAULT_PM_TILES_SCRIPT
        )
        self._ensure_pmtiles_script(script_url)
        return source

    def add_image(self, name, url=None, data=None, options=None):
        """Register a style image so it can be referenced by layers.

        Parameters
        ----------
        name : str
            Identifier to use from layer ``icon-image`` or ``fill-pattern``.
        url : str, optional
            Remote image URL to be loaded via ``map.loadImage`` at runtime.
        data : Any, optional
            Direct image data to pass to ``map.addImage``.
        options : dict, optional
            Extra parameters forwarded to ``map.addImage`` (e.g. ``sdf`` or
            ``pixelRatio``).
        """

        if url is None and data is None:
            raise ValueError("add_image requires either 'url' or 'data'")

        entry = {"id": name}
        if url is not None:
            entry["url"] = url
        if data is not None:
            entry["data"] = data
        if options:
            entry["options"] = options
        self.images.append(entry)
        return name

    def add_animated_icon(self, icon: AnimatedIcon) -> str:
        """Add an animated icon to the map.
        Parameters
        ----------
        icon : AnimatedIcon
            The animated icon to add.
        Returns
        -------
        str
            The ID of the added icon.
        """
        return icon.add_to_map(self)

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

        query = "&".join(f"{k}={quote(str(v), safe='{}')}" for k, v in params.items())
        url = f"{base_url}?{query}"

        self.add_tile_layer(url, name=name, attribution=attribution)

    def add_dem_source(
        self,
        name,
        url=None,
        *,
        tiles=None,
        tile_size=512,
        attribution=None,
        **kwargs,
    ):
        """Add a raster-dem source for terrain rendering.

        Parameters
        ----------
        name : str
            Identifier for the source.
        url : str or list, optional
            Tile JSON URL or template string. When the URL ends with
            ``.json`` it is treated as a TileJSON endpoint; otherwise it is
            interpreted as a tile template.
        tiles : str or sequence, optional
            Explicit tile URL template or list of templates. When provided it
            takes precedence over ``url``.
        tile_size : int, optional
            Tile size in pixels, defaults to ``512``.
        attribution : str, optional
            Attribution string for the DEM source.
        kwargs : dict, optional
            Additional source parameters forwarded to MapLibre.
        """

        if url is None and tiles is None:
            raise ValueError("add_dem_source requires either 'url' or 'tiles'")

        source_kwargs = dict(kwargs)
        if attribution is not None:
            source_kwargs["attribution"] = attribution

        source = source_wrappers.RasterDemSource(
            url=url,
            tiles=tiles,
            tile_size=tile_size,
            **source_kwargs,
        )

        self.add_source(name, source)
        return name

    def set_terrain(self, source_name, exaggeration=1.0, **options):
        """Enable 3D terrain using the given raster-dem source."""

        terrain_config = {"source": source_name}
        if exaggeration is not None:
            terrain_config["exaggeration"] = exaggeration
        if options:
            terrain_config.update(options)
        self.terrain = terrain_config

    def enable_globe(
        self,
        *,
        projection="globe",
        add_control=False,
        control_position="top-left",
        control_options=None,
    ):
        """Switch the map projection to globe and optionally add a control."""

        self.set_projection(
            projection,
            add_globe_control=add_control,
            control_position=control_position,
            control_options=control_options,
        )

    def set_projection(
        self,
        projection,
        *,
        add_globe_control=False,
        control_position="top-left",
        control_options=None,
    ):
        """Set the map projection used by MapLibre.

        Parameters
        ----------
        projection : str or mapping
            Either the name of the projection (e.g. ``"globe"`` or
            ``"mercator"``) or a mapping describing projection parameters.
            The mapping is passed straight through to MapLibre allowing
            custom projections such as Albers.
        add_globe_control : bool, optional
            When ``True`` and ``projection`` is ``"globe"``, the globe
            control is added to the map UI.
        control_position : str, optional
            Position for the optional globe control.
        control_options : dict, optional
            Additional options forwarded to the globe control.
        """

        if projection is None:
            raise ValueError("projection is required")
        if not isinstance(projection, (str, dict)):
            raise TypeError("projection must be a string or mapping")

        self.additional_map_options["projection"] = projection

        if add_globe_control:
            is_globe_projection = False
            if isinstance(projection, str):
                is_globe_projection = projection == "globe"
            elif isinstance(projection, dict):
                is_globe_projection = projection.get("name") == "globe"
            if not is_globe_projection:
                raise ValueError(
                    "Globe control can only be added when projection is 'globe'"
                )
            if control_options is None:
                control_options = {}
            self.add_control(
                "globe", position=control_position, options=control_options
            )

    def set_mobile_behavior(
        self,
        *,
        cooperative_gestures=None,
        touch_zoom_rotate=None,
        touch_pitch=None,
        pitch_with_rotate=None,
    ):
        """Toggle mobile-friendly MapLibre constructor flags.

        Parameters
        ----------
        cooperative_gestures : bool, optional
            Enable ``cooperativeGestures`` for friendlier embedded mobile maps.
        touch_zoom_rotate : bool, optional
            Toggle ``touchZoomRotate`` which controls pinch gestures.
        touch_pitch : bool, optional
            Toggle ``touchPitch`` to enable two-finger pitch gestures.
        pitch_with_rotate : bool, optional
            Toggle ``pitchWithRotate`` to control pitch during rotation.
        """

        flag_map = {
            "cooperativeGestures": cooperative_gestures,
            "touchZoomRotate": touch_zoom_rotate,
            "touchPitch": touch_pitch,
            "pitchWithRotate": pitch_with_rotate,
        }

        for flag, value in flag_map.items():
            if value is None:
                continue
            if not isinstance(value, bool):
                raise TypeError(f"{flag} expects a boolean value")
            self.additional_map_options[flag] = value

    def disable_rotation(
        self,
        *,
        drag_rotate=True,
        touch_zoom_rotate=True,
        keyboard_rotate=True
    ):
        """Disable map rotation interactions.
        
        This method provides a Python API alternative to JavaScript injection
        for disabling rotation controls.
        
        Parameters
        ----------
        drag_rotate : bool, optional
            Whether to disable drag rotation (default True).
        touch_zoom_rotate : bool, optional
            Whether to disable touch zoom rotation (default True).
        keyboard_rotate : bool, optional
            Whether to disable keyboard rotation (default True).
        """
        
        # Add JavaScript to disable rotation after map loads
        disable_js = []
        
        if drag_rotate:
            disable_js.append("map.dragRotate.disable();")
        
        if touch_zoom_rotate:
            disable_js.append("map.touchZoomRotate.disableRotation();")
            
        if keyboard_rotate:
            disable_js.append("map.keyboard.disableRotation();")
        
        if disable_js:
            self.add_on_load_js("\n".join(disable_js))

    def enable_rtl_text_plugin(
        self,
        url="https://unpkg.com/maplibre-gl-rtl-text@latest/dist/maplibre-gl-rtl-text.js",
        *,
        callback=_RTL_CALLBACK_UNSET,
        lazy=False,
        force=False,
    ):
        """Register the MapLibre RTL text plugin.

        Parameters
        ----------
        url : str, optional
            URL for the ``maplibre-gl-rtl-text`` plugin script.
        callback : str or None, optional
            JavaScript callback invoked once the plugin is loaded. Pass
            ``None`` to emit ``null`` and ``lazy=True`` when replicating the
            official example snippet.
        lazy : bool, optional
            When ``True`` the plugin is only fetched on demand, matching the
            third argument of ``maplibregl.setRTLTextPlugin``.
        force : bool, optional
            Force re-registering the plugin even if MapLibre reports that it
            has already been loaded.
        """

        if not isinstance(url, str) or not url:
            raise ValueError("A plugin URL is required")
        plugin_config: Dict[str, Any] = {
            "url": url,
            "lazy": bool(lazy),
            "force": bool(force),
        }

        if callback is not _RTL_CALLBACK_UNSET:
            if callback is not None and not isinstance(callback, str):
                raise TypeError("callback must be JavaScript code or None")
            plugin_config["callback"] = callback

        self.rtl_text_plugin = plugin_config

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
        self,
        html=None,
        coordinates=None,
        layer_id=None,
        events=None,
        options=None,
        prop=None,
        template=None,
        context=None,
    ):
        """Add a popup to the map.

        Parameters
        ----------
        html : str or object with render method
            HTML content of the popup.
        coordinates : list, optional
            [lng, lat] for a fixed popup position.
        layer_id : str, optional
            The ID of the layer to which the popup is bound.
        events : list, optional
            List of events that trigger the popup (e.g., ``['click']``).
        options : dict, optional
            A dictionary of popup options.
        prop : str, optional
            The name of a feature property to use as the popup content.
        template : str, optional
            A Jinja2 template string for the popup content.
        context : dict, optional
            The rendering context for templates.
        """
        if options is None:
            options = {}
        if events is None:
            events = ["click"]  # default event

        if template is not None:
            popup_obj = Popup(template=template)
            html_content = popup_obj.render(context)
        elif hasattr(html, "render"):
            html_content = html.render(context or {})
        else:
            html_content = html

        self.popups.append(
            {
                "html": html_content,
                "coordinates": coordinates,
                "layer_id": layer_id,
                "events": events,
                "options": options,
                "prop": prop,
            }
        )

    def add_tooltip(self, tooltip=None, layer_id=None, options=None, prop=None):
        """Add a tooltip to the map."""
        if isinstance(tooltip, Tooltip):
            text = tooltip.text
            opts = tooltip.options
        else:
            text = tooltip
            opts = options or {}
        opts.setdefault("closeButton", False)
        self.tooltips.append(
            {"text": text, "layer_id": layer_id, "options": opts, "prop": prop}
        )

    def add_lat_lng_popup(self):
        """Enable a popup showing latitude and longitude on click."""
        self.lat_lng_popup = True

    def set_source_tile_lod_params(
        self, max_zoom_levels: int, tile_count_ratio: float
    ):
        """Set the LOD parameters for source tiles.

        This is a wrapper around the MapLibre GL JS `setSourceTileLodParams` method.

        Parameters
        ----------
        max_zoom_levels : int
            The maximum number of zoom levels to show on screen.
        tile_count_ratio : float
            The ratio of tiles to render at high pitch angles.
        """
        js_code = f"map.setSourceTileLodParams({max_zoom_levels}, {tile_count_ratio});"
        self.add_on_load_js(js_code)

    def add_on_load_js(self, code: str) -> None:
        """Schedule raw JavaScript to execute within the load handler."""

        if not isinstance(code, str):
            raise TypeError("on-load JavaScript must be provided as a string")
        self._on_load_callbacks.append(code)

    def add_animation(self, animation) -> None:
        """Register an animation or temporal loop to run after load."""

        if hasattr(animation, "to_js"):
            script = animation.to_js()
        else:
            script = str(animation)
        self.animations.append(script)

    def _prepare_state_toggles(self, state_toggles):
        """Normalize toggle definitions into :class:`StateToggle` objects."""

        if not state_toggles:
            return []

        if isinstance(state_toggles, StateToggle):
            candidates = [state_toggles]
        elif isinstance(state_toggles, dict):
            candidates = [StateToggle(**state_toggles)]
        elif isinstance(state_toggles, Iterable) and not isinstance(
            state_toggles, (str, bytes)
        ):
            candidates = state_toggles
        else:
            raise TypeError(
                "state_toggles must be a StateToggle, dict, or iterable of these"
            )

        toggles = []
        for toggle in candidates:
            if isinstance(toggle, StateToggle):
                toggles.append(toggle)
            elif isinstance(toggle, dict):
                toggles.append(StateToggle(**toggle))
            else:
                raise TypeError(
                    "state_toggles entries must be mappings or StateToggle objects"
                )
        return toggles

    def _register_event_binding(
        self,
        event,
        *,
        layer_id=None,
        js=None,
        state_toggles=None,
        once=False,
        event_id=None,
        send_to_python=False,
    ):
        """Create or replace an :class:`EventBinding` for the map."""

        toggles = self._prepare_state_toggles(state_toggles)
        binding_id = event_id or (f"{event}@{layer_id}" if layer_id else event)
        binding = EventBinding(
            id=binding_id,
            event=event,
            layer_id=layer_id,
            js=js,
            send_to_python=send_to_python,
            toggles=toggles,
            once=once,
        )
        self.event_bindings = [b for b in self.event_bindings if b.id != binding.id]
        self.event_bindings.append(binding)
        if not send_to_python:
            callbacks = self._event_callbacks.get(self.map_id)
            if callbacks:
                callbacks.pop(binding.id, None)
            if binding.id in self.events:
                self.events.remove(binding.id)
        return binding

    def add_event_listener(
        self,
        event,
        *,
        layer_id=None,
        js=None,
        state_toggles=None,
        once=False,
        event_id=None,
    ):
        """Attach a pure JavaScript handler for a MapLibre event.

        Parameters
        ----------
        event : str
            Name of the MapLibre event to listen for (e.g., ``'click'``).
        layer_id : str, optional
            If provided, the handler listens to events bound to the given
            rendered layer ID.
        js : str, optional
            JavaScript snippet executed inside the handler. The snippet has
            access to ``map`` (the map instance), ``event`` (the MapLibre
            event object) and ``data`` (the payload sent to Python callbacks).
        state_toggles : iterable, optional
            Collection of :class:`StateToggle` objects or dictionaries that
            describe DOM state changes (class toggles, attribute updates, etc.)
            to execute alongside the handler.
        once : bool, optional
            When ``True`` the handler is registered with ``map.once`` instead of
            ``map.on``.
        event_id : str, optional
            Explicit identifier for the handler. Defaults to ``"{event}@{layer}"``
            when ``layer_id`` is provided or simply ``event`` otherwise.

        Returns
        -------
        str
            The identifier of the registered handler, useful for debugging or
            manual inspection.
        """

        binding = self._register_event_binding(
            event,
            layer_id=layer_id,
            js=js,
            state_toggles=state_toggles,
            once=once,
            event_id=event_id,
            send_to_python=False,
        )
        return binding.id

    def on(
        self,
        event,
        callback,
        *,
        layer_id=None,
        js=None,
        state_toggles=None,
        once=False,
        event_id=None,
    ):
        """Register a Python callback for a MapLibre event.

        The callback receives a dictionary with ``lngLat`` (when available),
        current ``center`` and ``zoom`` information. Extra JavaScript snippets
        or DOM state toggles can be chained to the same event using the
        ``js`` and ``state_toggles`` arguments.

        Parameters
        ----------
        event : str
            MapLibre event name.
        callback : callable
            Python callable invoked when the event fires. Executed via the
            Jupyter kernel in notebook environments.
        layer_id : str, optional
            Restrict the listener to features rendered by this layer.
        js : str, optional
            JavaScript snippet executed after the callback payload is queued.
        state_toggles : iterable, optional
            DOM toggle definitions applied whenever the event fires.
        once : bool, optional
            Register a one-shot listener using ``map.once``.
        event_id : str, optional
            Explicit identifier for this handler. Defaults to ``"{event}@{layer}"``
            for layer-bound handlers or ``event`` for map-wide listeners.

        Returns
        -------
        str
            The identifier associated with the handler.
        """

        binding = self._register_event_binding(
            event,
            layer_id=layer_id,
            js=js,
            state_toggles=state_toggles,
            once=once,
            event_id=event_id,
            send_to_python=True,
        )
        if binding.id not in self.events:
            self.events.append(binding.id)
        self._event_callbacks.setdefault(self.map_id, {})[binding.id] = callback
        return binding.id

    def on_click(self, callback, **kwargs):
        """Convenience method for click events."""

        return self.on("click", callback, **kwargs)

    def on_move(self, callback, **kwargs):
        """Convenience method for move events."""

        return self.on("move", callback, **kwargs)

    def on_hover(self, callback, **kwargs):
        """Convenience method for mouseenter events (hover)."""

        return self.on("mouseenter", callback, **kwargs)

    def on_mousemove(self, callback, **kwargs):
        """Convenience method for mousemove events."""

        return self.on("mousemove", callback, **kwargs)

    def on_mouseover(self, callback, **kwargs):
        """Convenience method for mouseover events."""

        return self.on("mouseover", callback, **kwargs)

    def on_mouseout(self, callback, **kwargs):
        """Convenience method for mouseout events."""

        return self.on("mouseout", callback, **kwargs)

    def query_rendered_features_at_point(self, point, layers=None, filter=None):
        """Create a JavaScript snippet to query rendered features at a point.
        
        This method provides a helper for generating feature query JavaScript
        that can be used in event handlers.
        
        Parameters
        ----------
        point : str
            JavaScript expression for the point (e.g., "event.point").
        layers : list, optional
            List of layer IDs to query.
        filter : dict, optional
            Filter expression to apply.
            
        Returns
        -------
        str
            JavaScript code snippet for querying features.
        """
        options = {}
        if layers is not None:
            options["layers"] = layers
        if filter is not None:
            options["filter"] = filter
            
        if options:
            return f"map.queryRenderedFeatures({point}, {json.dumps(options)})"
        else:
            return f"map.queryRenderedFeatures({point})"

    # Camera control methods
    def fly_to(self, **options):
        """Queue a MapLibre ``flyTo`` camera animation."""
        self.camera_actions.append({"method": "flyTo", "options": options})

    def ease_to(self, **options):
        """Queue a MapLibre ``easeTo`` camera animation."""
        self.camera_actions.append({"method": "easeTo", "options": options})

    def pan_to(self, center, **options):
        """Queue a MapLibre ``panTo`` camera movement."""
        action = {"method": "panTo", "center": center, "options": options}
        self.camera_actions.append(action)

    def jump_to_sequence(self, locations, interval=2000):
        """Queue a sequential `jumpTo` animation.

        Parameters
        ----------
        locations : list
            A list of coordinate pairs (e.g., `[[lng1, lat1], [lng2, lat2]]`).
        interval : int, optional
            Time in milliseconds between each jump. Defaults to 2000.
        """
        js_code = [
            f"const locations = {json.dumps(locations)};",
            "locations.forEach((location, index) => {",
            f"    setTimeout(() => {{",
            f"        map.jumpTo({{center: location}});",
            f"    }}, {interval} * index);",
            "});",
        ]
        self.add_on_load_js("\n".join(js_code))

    def animate_camera_around(self, period_ms=36000):
        """Animate the camera continuously rotating around the center point.

        This method provides a high-level Python API for creating a smooth,
        continuous camera rotation animation.

        Parameters
        ----------
        period_ms : int, optional
            The time in milliseconds for one full 360-degree rotation.
            Defaults to 36000 (36 seconds).
        """
        from .animation import AnimationLoop

        animation_js = (
            f"map.rotateTo((timestamp * 360 / {period_ms}) % 360, {{duration: 0}});"
        )

        loop = AnimationLoop(
            name="rotateCamera",
            body=animation_js,
        )
        self.add_animation(loop)

    def add_keyboard_navigation(self, pan_distance=100, rotate_degrees=25):
        """Enable game-like keyboard navigation for panning and rotating.

        This method provides a high-level Python API for adding keyboard
        listeners that allow users to navigate the map with arrow keys.

        Parameters
        ----------
        pan_distance : int, optional
            Distance in pixels to pan the map on each key press.
        rotate_degrees : int, optional
            Degrees to rotate the map on each key press.
        """
        js_code = [
            "const canvas = map.getCanvas();",
            "if (!canvas) { return; }",
            "if (!canvas.hasAttribute('tabindex')) {",
            "    canvas.setAttribute('tabindex', '0');",
            "}",
            "canvas.focus();",
            "",
            f"const deltaDistance = {pan_distance};",
            f"const deltaDegrees = {rotate_degrees};",
            "",
            "function easing(t) { return t * (2 - t); }",
            "",
            "canvas.addEventListener('keydown', function(e) {",
            "    e.preventDefault();",
            "    if (e.which === 38) {",
            "        map.panBy([0, -deltaDistance], { easing: easing });",
            "    } else if (e.which === 40) {",
            "        map.panBy([0, deltaDistance], { easing: easing });",
            "    } else if (e.which === 37) {",
            "        map.easeTo({ bearing: map.getBearing() - deltaDegrees, easing: easing });",
            "    } else if (e.which === 39) {",
            "        map.easeTo({ bearing: map.getBearing() + deltaDegrees, easing: easing });",
            "    }",
            "}, true);",
        ]
        self.add_on_load_js("\n".join(js_code))

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

    def add_clustered_geojson(
        self,
        data,
        name=None,
        radius=50,
        max_zoom=14,
    ):
        """Add a clustered GeoJSON source and layers to the map.

        Parameters
        ----------
        data : dict
            GeoJSON ``FeatureCollection`` to cluster.
        name : str, optional
            Base name for generated source and layers.
        radius : int, optional
            Cluster radius in pixels passed to ``Supercluster``.
        max_zoom : int, optional
            Maximum zoom level at which clustering occurs.
        """
        cluster = ClusteredGeoJson(
            data,
            name=name,
            cluster_radius=radius,
            cluster_max_zoom=max_zoom,
        )
        cluster.add_to(self)
        return cluster

    def add_circle_layer(
        self, name, source, paint=None, layout=None, before=None, filter=None
    ):
        """Add a circle layer to the map.

        Parameters
        ----------
        name : str
            The name of the layer.
        source : str or dict
            The source for the layer.
        paint : dict, optional
            The paint properties for the layer.
        layout : dict, optional
            The layout properties for the layer.
        before : str, optional
            The ID of an existing layer to insert this layer before.
        filter : list, optional
            A MapLibre GL filter expression.
        """
        if paint is None:
            paint = {"circle-radius": 6, "circle-color": "#007cbf"}
        layer_definition = {"id": name, "type": "circle", "paint": paint}
        if layout:
            layer_definition["layout"] = layout
        if filter:
            layer_definition["filter"] = filter
        self.add_layer(layer_definition, source=source, before=before)

    def add_time_dimension(self, data, options=None):
        """Store timestamped GeoJSON data for simple animation playback.

        Parameters
        ----------
        data : dict
            GeoJSON ``FeatureCollection`` whose features include a ``time``
            property.
        options : dict, optional
            Configuration dictionary. Supports ``interval`` in milliseconds
            for playback speed.
        """

        self.time_dimension_data = data
        self.time_dimension_options = options or {}

    def add_fill_layer(
        self, name, source, paint=None, layout=None, before=None, filter=None
    ):
        """Add a fill layer to the map.

        Parameters
        ----------
        name : str
            The name of the layer.
        source : str or dict
            The source for the layer.
        paint : dict, optional
            The paint properties for the layer.
        layout : dict, optional
            The layout properties for the layer.
        before : str, optional
            The ID of an existing layer to insert this layer before.
        filter : list, optional
            A MapLibre GL filter expression.
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
        """Add a line layer to the map.

        Parameters
        ----------
        name : str
            The name of the layer.
        source : str or dict
            The source for the layer.
        paint : dict, optional
            The paint properties for the layer.
        layout : dict, optional
            The layout properties for the layer.
        before : str, optional
            The ID of an existing layer to insert this layer before.
        filter : list, optional
            A MapLibre GL filter expression.
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
        """Add a heatmap layer to the map.

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
        """Add a symbol layer to the map.

        Parameters
        ----------
        name : str
            The name of the layer.
        source : str or dict
            The source for the layer.
        paint : dict, optional
            The paint properties for the layer.
        layout : dict, optional
            The layout properties for the layer.
        before : str, optional
            The ID of an existing layer to insert this layer before.
        filter : list, optional
            A MapLibre GL filter expression.
        """
        if layout is None:
            layout = {"icon-image": "marker-15"}
        layer_definition = {"id": name, "type": "symbol", "layout": layout}
        if paint:
            layer_definition["paint"] = paint
        if filter:
            layer_definition["filter"] = filter
        self.add_layer(layer_definition, source=source, before=before)

    def add_button_control(self, label, action, position="top-left", css_class="maplibreum-button", style=None):
        """Add a button control that can trigger map actions.
        
        This provides a Python API alternative to JavaScript injection for
        interactive buttons.
        
        Parameters
        ----------
        label : str
            The text label for the button.
        action : callable
            A function that takes the map instance as parameter.
        position : str, optional
            Position on the map (e.g. 'top-left', 'top-right').
        css_class : str, optional
            CSS class for styling the button.
        style : dict, optional
            Inline CSS styles for the button.
        
        Returns
        -------
        str
            A unique identifier for this button control.
        """
        from . import controls
        
        # Create a ButtonControl instance
        button = controls.ButtonControl(
            label=label,
            action=action,
            position=position,
            css_class=css_class,
            style=style
        )
        
        # Add it to the map's controls
        self.add_control(button, position)
        
        return button

    def render(self):
        """Render the map to an HTML string.

        Returns
        -------
        str
            The rendered HTML.
        """
        # Inject custom CSS to adjust the map div if needed
        # The template expects the unique map container ID to control sizing.
        dimension_css = (
            f"#{self.map_id} {{ width: {self.width}; height: {self.height}; }}"
        )
        marker_css = "\n".join(self.marker_css)
        final_custom_css = "\n".join([dimension_css, marker_css, self.custom_css])
        map_options = {
            "container": self.map_id,
            "style": self.map_style,
        }
        if self.bounds is None:
            map_options["center"] = self.center
            map_options["zoom"] = self.zoom
        if self.pitch is not None:
            map_options["pitch"] = self.pitch
        if self.bearing is not None:
            map_options["bearing"] = self.bearing
        if self.elevation is not None:
            map_options["elevation"] = self.elevation
        if self.center_clamped_to_ground is not None:
            map_options["centerClampedToGround"] = self.center_clamped_to_ground
        if self.additional_map_options:
            map_options.update(self.additional_map_options)

        if isinstance(map_options.get("projection"), str):
            map_options["projection"] = {"name": map_options["projection"]}

        include_minimap = any(c["type"] == "minimap" for c in self.controls)
        include_search = any(c["type"] in ["search", "geocoding"] for c in self.controls)

        combined_extra_js = "\n".join(
            part for part in [self.extra_js, *self._extra_js_snippets] if part
        )

        return self.template.render(
            title=self.title,
            map_options=map_options,
            bounds=self.bounds,
            bounds_padding=self.bounds_padding,
            sources=self.sources,
            controls=self.controls,
            include_minimap=include_minimap,
            include_search=include_search,
            layers=self.layers,
            deckgl_overlays=self.deckgl_overlays,
            tile_layers=self.tile_layers,
            overlays=self.overlays,
            layer_control=self.layer_control,
            popups=self.popups,
            tooltips=self.tooltips,
            markers=self.markers,
            legends=[legend.render() for legend in self.legends],
            cluster_layers=self.cluster_layers,
            extra_js=combined_extra_js,
            custom_css=final_custom_css,
            draw_control=self.draw_control,
            draw_control_options=self.draw_control_options,
            measure_control=self.measure_control,
            measure_control_options=self.measure_control_options,
            measure_control_position=self.measure_control_position,
            maplibre_version=self.maplibre_version,
            map_id=self.map_id,
            lat_lng_popup=self.lat_lng_popup,
            events=self.events,
            event_bindings=[b.to_render_dict() for b in self.event_bindings],
            terrain=self.terrain,
            fog=self.fog,
            float_images=self.float_images,
            images=self.images,
            camera_actions=self.camera_actions,
            time_dimension=self.time_dimension_data is not None,
            time_dimension_data=self.time_dimension_data,
            time_dimension_options=self.time_dimension_options,
            on_load_callbacks=self._on_load_callbacks,
            animations=self.animations,
            rtl_text_plugin=self.rtl_text_plugin,
            external_scripts=self.external_scripts,
            pmtiles_protocols=list(self._pmtiles_protocols.values()),
            pmtiles_sources=self._pmtiles_sources,
        )

    def _repr_html_(self):
        """Jupyter Notebook display method."""
        iframe_id = f"{self.map_id}_iframe"
        escaped_html = html.escape(self.render(), quote=True)
        style = f"width: {self.width}; height: {self.height}; border: none;"
        return (
            f'<iframe id="{iframe_id}" srcdoc="{escaped_html}" '
            f'style="{style}" loading="lazy"></iframe>'
        )

    def display_in_notebook(self, width="100%", height="500px"):
        """Display the map in a Jupyter Notebook with a specific size.

        This method writes the map to a temporary HTML file and displays it
        in an IFrame.

        Parameters
        ----------
        width : str, optional
            The width of the IFrame.
        height : str, optional
            The height of the IFrame.
        """
        # More controlled display using IFrame approach
        from tempfile import NamedTemporaryFile

        f = NamedTemporaryFile(suffix=".html", delete=False)
        f.write(self.render().encode("utf-8"))
        f.close()
        return display(IFrame(src=f.name, width=width, height=height))

    def save(self, filepath):
        """Save the map to an HTML file.

        Parameters
        ----------
        filepath : str
            The path to the output HTML file.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.render())

    def export_png(self, filepath, width=None, height=None):
        """Export the map to a PNG image using the MapLibre export CLI.

        Parameters
        ----------
        filepath : str
            Destination path for the PNG file.
        width, height : int, optional
            Dimensions for the exported image in pixels.
        """
        from tempfile import NamedTemporaryFile

        html = self.render()
        tmp = NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
        tmp.write(html)
        tmp.close()

        cmd = [
            "npx",
            "@maplibre/maplibre-gl-export",
            "--input",
            tmp.name,
            "--output",
            filepath,
        ]
        if width:
            cmd.extend(["--width", str(width)])
        if height:
            cmd.extend(["--height", str(height)])

        try:
            subprocess.run(cmd, check=True)
        finally:
            os.remove(tmp.name)

    @classmethod
    def _store_drawn_features(cls, map_id, geojson_str):
        """Store features drawn on the map."""
        cls._drawn_data[map_id] = json.loads(geojson_str)

    @classmethod
    def _handle_event(cls, map_id, event, data_json):
        """Handle a map event by invoking a registered callback."""
        callback = cls._event_callbacks.get(map_id, {}).get(event)
        if callback:
            data = json.loads(data_json)
            callback(data)

    @classmethod
    def _register_marker(cls, map_id, marker):
        """Register a marker to track its state."""
        cls._marker_registry.setdefault(map_id, {})[marker.id] = marker

    @classmethod
    def _update_marker_coords(cls, map_id, marker_id, lng, lat):
        """Update the coordinates of a draggable marker."""
        marker = cls._marker_registry.get(map_id, {}).get(marker_id)
        if marker:
            marker.coordinates = [lng, lat]

    @classmethod
    def _store_search_result(cls, map_id, lng, lat):
        """Store the result of a geocoder search."""
        cls._search_data[map_id] = [lng, lat]

    @property
    def drawn_features(self):
        """Get the features drawn on the map.

        Returns
        -------
        dict
            A GeoJSON FeatureCollection of the drawn features.
        """
        return self._drawn_data.get(self.map_id)

    @property
    def search_result(self):
        """Get the result of the last geocoder search.

        Returns
        -------
        list
            A ``[lng, lat]`` coordinate pair.
        """
        return self._search_data.get(self.map_id)


class Marker:
    """A marker on the map."""

    def __init__(
        self,
        coordinates,
        popup=None,
        color="#007cbf",
        icon=None,
        tooltip=None,
        draggable=False,
    ):
        """Initialize a Marker.

        Parameters
        ----------
        coordinates : list or tuple
            The ``[lng, lat]`` coordinates of the marker.
        popup : str, optional
            The HTML content of the marker's popup.
        color : str, optional
            The color of the marker.
        icon : Icon, optional
            The icon to use for the marker.
        tooltip : str or Tooltip, optional
            The text content of the marker's tooltip.
        draggable : bool, optional
            Whether the marker is draggable.
        """
        self.coordinates = coordinates
        self.popup = popup
        self.color = color
        self.icon = icon
        self.tooltip = tooltip
        self.draggable = draggable
        self.id = None

    def add_to(self, map_instance):
        """Add the marker to a map or marker cluster.

        Parameters
        ----------
        map_instance : maplibreum.Map or maplibreum.MarkerCluster
            The map or marker cluster to which the marker will be added.

        Returns
        -------
        self
        """
        if isinstance(map_instance, MarkerCluster):
            if self.draggable:
                raise ValueError("Draggable markers cannot be added to a cluster")
            map_instance.add_marker(self)
            return self

        is_feature_group = map_instance.__class__.__name__ == "FeatureGroup"

        if isinstance(self.icon, Icon):
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
            map_instance.add_layer(layer, source=source)

            if self.popup:
                map_instance.add_popup(html=self.popup, layer_id=layer_id)
            if self.tooltip:
                map_instance.add_tooltip(self.tooltip, layer_id=layer_id)
            return self

        if is_feature_group:
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
            if self.tooltip:
                map_instance.add_tooltip(self.tooltip, layer_id=layer_id)
            return self

        self.id = f"marker_{uuid.uuid4().hex}"

        if self.popup is not None and callable(getattr(self.popup, "render", None)):
            popup_content = self.popup.render({})
        else:
            popup_content = self.popup

        if isinstance(self.tooltip, Tooltip):
            tooltip_content = self.tooltip.text
        else:
            tooltip_content = self.tooltip

        marker_data = {
            "id": self.id,
            "coordinates": self.coordinates,
            "popup": popup_content,
            "tooltip": tooltip_content,
            "draggable": self.draggable,
        }
        if isinstance(self.icon, (DivIcon, BeautifyIcon)):
            marker_data["html"] = self.icon.html
            marker_data["class_name"] = self.icon.class_name
            if getattr(self.icon, "css", None):
                if self.icon.css not in map_instance.marker_css:
                    map_instance.marker_css.append(self.icon.css)
        else:
            marker_data["color"] = self.color
        map_instance.markers.append(marker_data)
        if self.draggable:
            Map._register_marker(map_instance.map_id, self)
        return self



class GeoJson:
    """Representation of a GeoJSON overlay."""

    def __init__(
        self,
        data,
        style_function=None,
        name=None,
        popup=None,
        tooltip=None,
    ):
        """Initialize a GeoJson overlay.

        Parameters
        ----------
        data : dict
            The GeoJSON data.
        style_function : callable, optional
            A function that takes a feature and returns a style dictionary.
        name : str, optional
            The name of the GeoJSON layer.
        popup : str or GeoJsonPopup, optional
            A popup to display when a feature is clicked.
        tooltip : str or GeoJsonTooltip, optional
            A tooltip to display when hovering over a feature.
        """
        self.data = data
        self.name = name if name else f"geojson_{uuid.uuid4().hex}"
        self.popup = popup
        self.tooltip = tooltip

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
            if self.popup:
                feature["properties"]["_popup"] = self.popup.render(feature)
            if self.tooltip:
                feature["properties"]["_tooltip"] = self.tooltip.render(feature)

        source_id = f"{self.name}_source"
        source = {"type": "geojson", "data": self.data}
        map_instance.add_source(source_id, source)

        def _get(prop):
            return expr_get(prop, ["properties"])

        geometry_types = [
            f.get("geometry", {}).get("type") for f in features if f.get("geometry")
        ]

        layer_ids = []

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
            layer_ids.append(fill_layer["id"])

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
            layer_ids.append(line_layer["id"])

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
            layer_ids.append(circle_layer["id"])

        if self.popup:
            for lid in layer_ids:
                map_instance.add_popup(layer_id=lid, prop="_popup")
        if self.tooltip:
            for lid in layer_ids:
                map_instance.add_tooltip(layer_id=lid, prop="_tooltip")


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
        """Add the image overlay to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the image overlay will be added.

        Returns
        -------
        self
        """
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
    """Add an image floating above the map at a fixed position."""

    _POSITION_STYLES = {
        "top-left": "top: 0px; left: 0px;",
        "top-right": "top: 0px; right: 0px;",
        "bottom-left": "bottom: 0px; left: 0px;",
        "bottom-right": "bottom: 0px; right: 0px;",
    }

    def __init__(self, image_url, position="top-left", width=None):
        """Initialize a FloatImage.

        Parameters
        ----------
        image_url : str
            The URL of the image.
        position : str, optional
            The position of the image on the map.
        width : int, optional
            The width of the image in pixels.
        """
        self.image_url = image_url
        self.position = position
        self.width = width

    @property
    def style(self):
        """Get the CSS style for the floating image."""
        base = self._POSITION_STYLES.get(self.position, "")
        if self.width is not None:
            base += f" width: {self.width}px;"
        return base

    def add_to(self, map_instance):
        """Add the floating image to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the floating image will be added.

        Returns
        -------
        self
        """
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
        """Add the video overlay to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the video overlay will be added.

        Returns
        -------
        self
        """
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
        """Initialize a FeatureGroup.

        Parameters
        ----------
        name : str, optional
            The name of the feature group.
        """
        self.name = name or f"featuregroup_{uuid.uuid4().hex}"
        self.sources = []
        self.layers = []
        self.popups = []
        self.tooltips = []
        self.layer_ids = []

    def add_source(self, name, definition):
        """Add a source to the feature group.

        Parameters
        ----------
        name : str
            The name of the source.
        definition : dict
            The source definition.
        """
        self.sources.append({"name": name, "definition": definition})

    def add_layer(self, layer_definition, source=None, before=None):
        """Add a layer to the feature group.

        Parameters
        ----------
        layer_definition : dict
            A dictionary describing a MapLibre GL style layer.
        source : dict or str, optional
            A dictionary describing a MapLibre source, or a string
            referencing an existing source.
        before : str, optional
            The ID of an existing layer before which this layer should be
            placed.

        Returns
        -------
        str
            The ID of the added layer.
        """
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

    def add_popup(
        self,
        html=None,
        coordinates=None,
        layer_id=None,
        events=None,
        options=None,
        prop=None,
        template=None,
        context=None,
    ):
        """Add a popup to the feature group.

        Parameters
        ----------
        html : str or object with render method
            HTML content of the popup.
        coordinates : list, optional
            [lng, lat] for a fixed popup position.
        layer_id : str, optional
            The ID of the layer to which the popup is bound.
        events : list, optional
            List of events that trigger the popup (e.g., ``['click']``).
        options : dict, optional
            A dictionary of popup options.
        prop : str, optional
            The name of a feature property to use as the popup content.
        template : str, optional
            A Jinja2 template string for the popup content.
        context : dict, optional
            The rendering context for templates.
        """
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
                "prop": prop,
                "template": template,
                "context": context,
            }
        )

    def add_tooltip(self, tooltip=None, layer_id=None, options=None, prop=None):
        """Add a tooltip to the feature group.

        Parameters
        ----------
        tooltip : str or Tooltip
            The tooltip content.
        layer_id : str, optional
            The ID of the layer to which the tooltip is bound.
        options : dict, optional
            A dictionary of tooltip options.
        prop : str, optional
            The name of a feature property to use as the tooltip content.
        """
        if isinstance(tooltip, Tooltip):
            text = tooltip.text
            opts = tooltip.options
        else:
            text = tooltip
            opts = options or {}
        opts.setdefault("closeButton", False)
        self.tooltips.append(
            {"text": text, "layer_id": layer_id, "options": opts, "prop": prop}
        )

    def add_to(self, map_instance):
        """Add the feature group to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the feature group will be added.

        Returns
        -------
        self
        """
        for src in self.sources:
            map_instance.add_source(src["name"], src["definition"])
        for layer in self.layers:
            map_instance.add_layer(layer["definition"], before=layer["before"])
        for popup in self.popups:
            map_instance.add_popup(**popup)
        for tooltip in self.tooltips:
            map_instance.add_tooltip(
                tooltip["text"],
                layer_id=tooltip["layer_id"],
                options=tooltip["options"],
            )
        return self


class LayerControl:
    """Simple layer control to toggle tile and overlay layers."""

    def __init__(self):
        """Initialize a LayerControl."""
        self.overlays = []

    def add_overlay(self, layer, name=None):
        """Register an overlay layer or group by ID and display name."""
        if isinstance(layer, FeatureGroup):
            self.overlays.append(
                {
                    "id": layer.name,
                    "name": name or layer.name,
                    "layers": layer.layer_ids,
                }
            )
        else:
            self.overlays.append({"id": layer, "name": name or layer})
        return self

    def add_to(self, map_instance):
        """Add the layer control to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the layer control will be added.

        Returns
        -------
        self
        """
        map_instance.layer_control = True
        if self.overlays:
            for ov in self.overlays:
                map_instance.register_overlay(ov["id"], ov["name"], ov.get("layers"))
        return self


class Legend:
    """Map legend supporting raw HTML or label/color pairs."""

    def __init__(self, content):
        """Initialize a Legend.

        Parameters
        ----------
        content : str or list
            If a string, it is used as raw HTML. If a list, it should
            contain ``(label, color)`` tuples.
        """
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
        """Render the legend to HTML."""
        return self._html

    def add_to(self, map_instance):
        """Add the legend to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the legend will be added.

        Returns
        -------
        self
        """
        map_instance.add_legend(self)
        return self


class LatLngPopup:
    """Display a popup with latitude and longitude when the map is clicked."""

    def add_to(self, map_instance):
        """Add the LatLngPopup to a map instance.

        Parameters
        ----------
        map_instance : maplibreum.Map
            The map instance to which the LatLngPopup will be added.

        Returns
        -------
        self
        """
        map_instance.add_lat_lng_popup()
        return self
