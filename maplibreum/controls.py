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


class TextFilterControl:
    """A text input control for filtering map layers or features.
    
    This control provides an alternative to JavaScript injection for
    text-based filtering of layers.
    """
    
    def __init__(self, layer_ids, placeholder="Filter by name", 
                 position="top-right", match_mode="contains"):
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
        self.id = f"text_filter_{uuid.uuid4().hex}" if 'uuid' in globals() else f"text_filter_{hash(placeholder)}"
        
    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "id": self.id,
            "layer_ids": self.layer_ids,
            "placeholder": self.placeholder,
            "position": self.position,
            "match_mode": self.match_mode
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
        self.id = f"layer_color_{uuid.uuid4().hex}" if 'uuid' in globals() else f"layer_color_{hash(title)}"
        
    def to_dict(self):
        """Serialize configuration for template usage."""
        return {
            "id": self.id,
            "layers": self.layers,
            "colors": self.colors,
            "position": self.position,
            "title": self.title
        }
