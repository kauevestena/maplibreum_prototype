"""Marker icon classes for MapLibreum."""

from __future__ import annotations

import uuid
from typing import Optional
from jinja2 import Environment

from .cluster import MarkerCluster


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


class Icon:
    """Representation of an image-based icon used for symbol markers.

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

    def __init__(
        self,
        icon_image: str,
        icon_size: Optional[float] = None,
        icon_anchor: Optional[str] = None,
    ) -> None:
        """Initialize an Icon."""
        self.icon_image = icon_image
        self.icon_size = icon_size
        self.icon_anchor = icon_anchor


class DivIcon:
    """HTML/CSS based icon rendered with a DOM element."""

    def __init__(
        self, html: str = "", class_name: str = "maplibreum-div-icon"
    ) -> None:
        """Initialize a DivIcon.

        Parameters
        ----------
        html : str, optional
            The HTML content of the icon.
        class_name : str, optional
            The CSS class name of the icon.
        """
        self.html = html
        self.class_name = class_name
        # Basic display rules so the element is visible
        self.css = ".maplibreum-div-icon {display: inline-block;}"


class BeautifyIcon(DivIcon):
    """A simple BeautifyIcon similar to Leaflet's plugin.

    Parameters
    ----------
    icon : str
        CSS class for an inner icon element.
    icon_shape : str, optional
        Shape of the marker. Only ``"marker"`` is implemented.
    border_color : str, optional
        Border color for the marker.
    text_color : str, optional
        Color of the icon text.
    background_color : str, optional
        Background color of the marker.
    """

    def __init__(
        self,
        icon: str = "",
        icon_shape: str = "marker",
        border_color: str = "#b8b8b8",
        text_color: str = "white",
        background_color: str = "#2a81cb",
    ) -> None:
        """Initialize a BeautifyIcon."""
        class_name = f"beautify-marker beautify-marker-{icon_shape}"
        html = f"<i class='{icon}'></i>"
        super().__init__(html=html, class_name=class_name)
        base_css = (
            ".beautify-marker {display:flex;align-items:center;justify-content:center;"
            "width:26px;height:26px;line-height:26px;}"
            ".beautify-marker-marker {border-radius:13px 13px 13px 0;"
            "transform:rotate(-45deg);"
            f"background-color:{background_color};border:2px solid {border_color};}}"
            ".beautify-marker-marker i {transform:rotate(45deg);color:"
            + text_color
            + ";}"
        )
        self.css = base_css
        self.background_color = background_color
        self.text_color = text_color
        self.border_color = border_color


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
            # Use the class of the instance to avoid circular import of Map
            map_instance.__class__._register_marker(map_instance.map_id, self)
        return self
