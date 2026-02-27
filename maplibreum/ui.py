from jinja2 import Environment


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
