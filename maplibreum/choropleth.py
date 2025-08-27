import math
import uuid  # for generating unique layer/source identifiers

from .expressions import get as expr_get


class Choropleth:
    """Simple choropleth renderer for GeoJSON data.

    Parameters
    ----------
    geojson : dict
        FeatureCollection containing polygon features.
    data : dict
        Mapping from feature key to numeric value.
    key_on : str, optional
        Feature key to match in ``data``. Default ``"id"``.
    colors : list of str, optional
        Sequence of colors used for bins.
    color_scale : str, optional
        ``"linear"`` for equal-interval bins or ``"quantile"`` for quantile bins.
    legend_title : str, optional
        Title shown on the legend.
    """

    def __init__(
        self,
        geojson,
        data,
        key_on="id",
        colors=None,
        color_scale="linear",
        legend_title="",
    ):
        self.geojson = geojson
        self.data = data
        self.key_on = key_on
        self.colors = colors or [
            "#ffffcc",
            "#c2e699",
            "#78c679",
            "#31a354",
            "#006837",
        ]
        self.color_scale = color_scale
        self.legend_title = legend_title

    def _feature_key(self, feature):
        """Extract the key used to match feature to data."""
        if self.key_on == "id":
            return feature.get("id") or feature.get("properties", {}).get("id")
        parts = self.key_on.split(".")
        val = feature
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part)
            else:
                return None
        return val

    def _compute_bins(self, values):
        n = len(self.colors)
        if not values:
            return [0] * (n + 1)
        if self.color_scale == "quantile":
            sorted_vals = sorted(values)
            bins = [sorted_vals[0]]
            for i in range(1, n):
                idx = math.ceil(len(sorted_vals) * i / n) - 1
                bins.append(sorted_vals[idx])
            bins.append(sorted_vals[-1])
        else:  # linear
            min_val = min(values)
            max_val = max(values)
            step = (max_val - min_val) / n if n else 0
            bins = [min_val + step * i for i in range(n)]
            bins.append(max_val)
        return bins

    def _color_for_value(self, value, bins):
        for i in range(len(self.colors)):
            if value <= bins[i + 1] or i == len(self.colors) - 1:
                return self.colors[i]
        return self.colors[-1]

    def add_to(self, map_instance):
        features = self.geojson.get("features", [])
        values = []
        for feat in features:
            key = self._feature_key(feat)
            if key in self.data:
                value = self.data[key]
                feat.setdefault("properties", {})["value"] = value
                values.append(value)

        bins = self._compute_bins(values)
        for feat in features:
            value = feat.get("properties", {}).get("value")
            if value is None:
                continue
            color = self._color_for_value(value, bins)
            feat.setdefault("properties", {})["fillColor"] = color

        source_id = f"choropleth_{uuid.uuid4().hex}_source"
        source = {"type": "geojson", "data": self.geojson}
        map_instance.add_source(source_id, source)

        layer = {
            "id": f"choropleth_{uuid.uuid4().hex}",
            "type": "fill",
            "source": source_id,
            "paint": {
                "fill-color": expr_get("fillColor", ["properties"]),
                "fill-opacity": 0.7,
            },
        }
        map_instance.add_layer(layer)

        legend_rows = []
        for i in range(len(self.colors)):
            start = bins[i]
            end = bins[i + 1]
            label = f"{start:.2f} – {end:.2f}"
            legend_rows.append(
                f"<div><i style='background:{self.colors[i]}'></i>{label}</div>"
            )
        legend_html = f"<div><strong>{self.legend_title}</strong><br>{''.join(legend_rows)}</div>"
        map_instance.add_legend(legend_html)

        return self
