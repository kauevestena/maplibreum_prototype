"""Marker icon classes for MapLibreum."""

from __future__ import annotations

from typing import Optional


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
