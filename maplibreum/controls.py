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
