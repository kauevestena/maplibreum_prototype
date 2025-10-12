"""This module contains experimental features."""

from __future__ import annotations

import json
import textwrap

from .core import Map


class MapSynchronizer:
    """Synchronize movement of multiple maps."""

    def __init__(self, maps: list[Map]) -> None:
        if len(maps) < 2:
            raise ValueError("MapSynchronizer requires at least two maps.")
        self._maps = maps
        self._primary_map = maps[0]
        self._secondary_maps = maps[1:]

    def add_to(self, map_obj: Map) -> None:
        """Add the synchronizer to the primary map."""
        if map_obj is not self._primary_map:
            raise ValueError("MapSynchronizer can only be added to the primary map.")

        map_obj.add_external_script(
            "https://unpkg.com/@mapbox/mapbox-gl-sync-move@0.3.1"
        )
        map_obj.add_on_load_js(self._render_js(map_obj))
        map_obj.custom_css = self._render_css()

    def _render_js(self, map_obj: Map) -> str:
        """Render the JavaScript for synchronization."""
        template = map_obj.env.get_template("sync_maps.js")
        return template.render(
            primary_map_id=self._primary_map.map_id,
            secondary_map_configs=[
                {
                    "container": f"{self._primary_map.map_id}-secondary-{i}",
                    "style": m.map_style,
                    "center": m.center,
                    "zoom": m.zoom,
                }
                for i, m in enumerate(self._secondary_maps)
            ],
        )

    def _render_css(self) -> str:
        """Render the CSS for the map layout."""
        return textwrap.dedent(
            f"""
            html, body {{
                height: 100%;
            }}
            .maplibreum-sync-wrapper {{
                display: flex;
                width: 100%;
                height: 100%;
            }}
            .maplibreum-sync-wrapper > .maplibreum-sync-map {{
                flex: 1 1 0;
                height: 100%;
            }}
            #{self._primary_map.map_id} {{
                height: 100%;
            }}
            """
        ).strip()


class GlobeInteraction:
    def __init__(self, element_id: str = "fly", zoom_delta: float = 1.5):
        self.element_id = element_id
        self.zoom_delta = zoom_delta
        self._map = None

    def add_to(self, map_obj: Map) -> None:
        self._map = map_obj
        self._map.add_on_load_js(self._render_js())

    def _render_js(self) -> str:
        js_code = f"""
        let zoomIn = false;

        function getZoomAdjustment(oldLatitude, newLatitude) {{
            return Math.log2(Math.cos(newLatitude / 180 * Math.PI) / Math.cos(oldLatitude / 180 * Math.PI));
        }}

        function flyToWithGlobeCompensation() {{
            const center = [
                map.getCenter().lng,
                zoomIn ? 0 : 80,
            ];
            const mapZoom = map.getZoom();
            const delta = (zoomIn ? {self.zoom_delta} : -{self.zoom_delta});
            const zoom = map.getZoom() + delta + getZoomAdjustment(map.getCenter().lat, center[1]);
            map.flyTo({{
                center,
                zoom,
                essential: true
            }});
            zoomIn = !zoomIn;
        }}

        document.getElementById('{self.element_id}').addEventListener('click', () => {{
            flyToWithGlobeCompensation();
        }});
        """
        return textwrap.dedent(js_code)


class GeoJSONFilePicker:
    """Create a button that loads local GeoJSON files via the File System Access API.

    The control mirrors the "view-local-geojson-experimental" MapLibre GL JS example
    by rendering a button inside the map container. When the browser supports the
    File System Access API the button opens the native file picker and injects the
    selected GeoJSON into the map. Browsers without support fall back to a hidden
    ``<input type="file">`` element, matching the copy and UX of the original example.

    Parameters
    ----------
    button_id : str, optional
        Identifier for the button element. Defaults to ``"maplibreum-geojson-picker"``.
    button_text : str, optional
        Text rendered on the button when the File System Access API is available.
    fallback_message : str, optional
        Message displayed on the button when the API is unavailable.
    source_id : str, optional
        Identifier for the GeoJSON source added/updated when files are loaded.
    layer_id : str, optional
        Identifier for the layer created for the uploaded data.
    layer_type : str, optional
        MapLibre layer type. Defaults to ``"fill"``.
    paint : dict, optional
        Paint properties for the generated layer. A sensible default fill style is used
        when omitted.
    layout : dict, optional
        Optional layout properties for the generated layer.
    filter_expression : list, optional
        Optional MapLibre filter expression applied to the layer. When omitted and the
        layer type is ``"fill"`` a polygon filter is applied automatically.
    start_in : str, optional
        Directory hint forwarded to ``window.showOpenFilePicker``. Defaults to
        ``"downloads"``.
    file_types : list, optional
        Custom file type configuration for ``showOpenFilePicker``. Defaults to a
        GeoJSON specific configuration when omitted.
    accept : str, optional
        Value forwarded to the fallback ``<input type="file">`` element's ``accept``
        attribute. Defaults to common GeoJSON MIME types and extensions.
    """

    def __init__(
        self,
        *,
        button_id: str = "maplibreum-geojson-picker",
        button_text: str = "View local GeoJSON file",
        fallback_message: str = "Your browser does not support File System Access API",
        source_id: str = "uploaded-source",
        layer_id: str = "uploaded-polygons",
        layer_type: str = "fill",
        paint: dict | None = None,
        layout: dict | None = None,
        filter_expression: list | None = None,
        start_in: str = "downloads",
        file_types: list[dict[str, object]] | None = None,
        accept: str | None = None,
    ) -> None:
        if not button_id:
            raise ValueError("GeoJSONFilePicker requires a button_id")
        if not source_id:
            raise ValueError("GeoJSONFilePicker requires a source_id")
        if not layer_id:
            raise ValueError("GeoJSONFilePicker requires a layer_id")

        self.button_id = button_id
        self.button_text = button_text
        self.fallback_message = fallback_message
        self.source_id = source_id
        self.layer_id = layer_id
        self.layer_type = layer_type
        self.paint = paint if paint is not None else {
            "fill-color": "#888888",
            "fill-outline-color": "red",
            "fill-opacity": 0.4,
        }
        self.layout = layout
        default_filter = ["==", "$type", "Polygon"] if layer_type == "fill" else None
        self.filter_expression = filter_expression or default_filter
        self.start_in = start_in
        if file_types is None:
            file_types = [
                {
                    "description": "GeoJSON",
                    "accept": {
                        "application/geo+json": [".geojson"],
                        "application/vnd.geo+json": [".geojson"],
                        "application/json": [".json"],
                    },
                }
            ]
        self.file_types = file_types
        if accept is None:
            accept = (
                "application/geo+json,application/vnd.geo+json,"
                "application/json,.geojson,.json"
            )
        self.accept = accept

        self._picker_options = {
            "multiple": False,
            "types": self.file_types,
            "startIn": self.start_in,
        }

    def to_css(self) -> str:
        """Return CSS that positions and styles the picker button."""

        return textwrap.dedent(
            f"""
            #{self.button_id} {{
                position: absolute;
                top: 12px;
                left: 12px;
                z-index: 2;
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid #d0d7de;
                background-color: rgba(255, 255, 255, 0.95);
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.15);
                font-family: inherit;
                font-size: 14px;
                cursor: pointer;
            }}

            #{self.button_id}.maplibreum-geojson-picker-unsupported {{
                cursor: not-allowed;
                opacity: 0.8;
            }}
            """
        ).strip()

    def to_js(self) -> str:
        """Generate JavaScript that wires the picker into the map instance."""

        layer_config: dict[str, object] = {
            "id": self.layer_id,
            "type": self.layer_type,
            "source": self.source_id,
        }
        if self.paint:
            layer_config["paint"] = self.paint
        if self.layout:
            layer_config["layout"] = self.layout
        if self.filter_expression:
            layer_config["filter"] = self.filter_expression

        js_code = f"""
        (function() {{
            const container = map.getContainer();
            if (!container) {{
                console.warn('GeoJSONFilePicker requires a map container.');
                return;
            }}

            let button = container.querySelector('#{self.button_id}');
            if (!button) {{
                button = document.createElement('button');
                button.id = '{self.button_id}';
                button.type = 'button';
                container.appendChild(button);
            }}
            button.textContent = {json.dumps(self.button_text)};
            button.classList.add('maplibreum-geojson-picker-button');

            let fallbackInput = container.querySelector('#{self.button_id}-input');
            if (!fallbackInput) {{
                fallbackInput = document.createElement('input');
                fallbackInput.type = 'file';
                fallbackInput.id = '{self.button_id}-input';
                fallbackInput.accept = '{self.accept}';
                fallbackInput.style.display = 'none';
                container.appendChild(fallbackInput);
            }}

            const layerConfig = {json.dumps(layer_config)};
            const pickerOptions = {json.dumps(self._picker_options)};
            const unsupportedMessage = {json.dumps(self.fallback_message)};

            async function applyGeoJSON(file) {{
                if (!file) {{
                    return;
                }}
                try {{
                    const text = await file.text();
                    const data = JSON.parse(text);
                    const existingSource = map.getSource('{self.source_id}');
                    if (existingSource) {{
                        existingSource.setData(data);
                    }} else {{
                        map.addSource('{self.source_id}', {{ type: 'geojson', data }});
                    }}
                    if (!map.getLayer(layerConfig.id)) {{
                        map.addLayer(layerConfig);
                    }}
                }} catch (error) {{
                    console.error('GeoJSONFilePicker failed to load data', error);
                }}
            }}

            async function openWithPicker() {{
                if (!window.showOpenFilePicker) {{
                    fallbackInput.click();
                    return;
                }}
                try {{
                    const [handle] = await window.showOpenFilePicker(pickerOptions);
                    if (!handle) {{
                        return;
                    }}
                    const file = await handle.getFile();
                    await applyGeoJSON(file);
                }} catch (error) {{
                    if (error && error.name === 'AbortError') {{
                        return;
                    }}
                    console.error('GeoJSONFilePicker selection error', error);
                }}
            }}

            button.addEventListener('click', openWithPicker);
            fallbackInput.addEventListener('change', (event) => {{
                const file = event.target.files && event.target.files[0];
                if (file) {{
                    applyGeoJSON(file);
                }}
                event.target.value = '';
            }});

            if (!('showOpenFilePicker' in window)) {{
                button.textContent = unsupportedMessage;
                button.classList.add('maplibreum-geojson-picker-unsupported');
            }}
        }})();
        """
        return textwrap.dedent(js_code).strip()

    def add_to(self, map_obj: Map) -> None:
        """Attach the picker to a map by injecting CSS and JavaScript."""

        if not isinstance(map_obj, Map):
            raise TypeError("GeoJSONFilePicker.add_to expects a Map instance")

        css = self.to_css()
        if map_obj.custom_css:
            map_obj.custom_css = "\n".join(filter(None, [map_obj.custom_css, css]))
        else:
            map_obj.custom_css = css
        map_obj.add_on_load_js(self.to_js())

