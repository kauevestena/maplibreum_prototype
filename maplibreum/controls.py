import uuid
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


class ButtonControl:
    """A button control that can trigger Python API actions.
    
    This control provides an alternative to JavaScript injection for
    interactive buttons on the map.
    """
    
    def __init__(self, label, action=None, position="top-left", 
                 css_class="maplibreum-button", style=None, onclick_js=None):
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
        self.id = f"button_{uuid.uuid4().hex}" if 'uuid' in globals() else f"button_{hash(label)}"
        
    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "id": self.id,
            "label": self.label,
            "action": self.action,
            "position": self.position,
            "css_class": self.css_class,
            "style": self.style,
            "onclick_js": self.onclick_js
        }


class ToggleControl:
    """A toggle control for switching between two states."""
    
    def __init__(self, label, on_action=None, off_action=None, 
                 initial_state=False, position="top-left"):
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
            "position": self.position
        }
