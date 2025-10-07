"""
Support for real-time data updates and animations.
"""
from __future__ import annotations

import json
from typing import Any, Dict

import requests

from .animation import TemporalInterval
from .sources import GeoJSONSource


class RealTimeDataSource(GeoJSONSource):
    """
    A GeoJSON source that is designed to be updated in real-time.
    This class is a marker class and does not add any new functionality
    to GeoJSONSource, but it is used to identify sources that are
    intended for real-time updates. The full dataset is stored in the
    `data` property of the parent class.
    """

    def __init__(self, data: dict, **kwargs: Any):
        super().__init__(data=data, **kwargs)

    @classmethod
    def from_url(cls, url: str, **kwargs: Any) -> "RealTimeDataSource":
        """
        Create a RealTimeDataSource from a URL.
        """
        data = requests.get(url).json()
        return cls(data=data, **kwargs)


class AnimatePointOnLine:
    """
    Creates a JavaScript animation loop to animate a point along a line.
    This is a high-level abstraction over TemporalInterval.
    """

    def __init__(
        self,
        source_id: str,
        data: dict,
        interval: int = 10,
    ):
        self.source_id = source_id
        self.data = data
        self.interval = interval
        self._js_code = self._create_js()

    def _create_js(self) -> str:
        try:
            coordinates = self.data["features"][0]["geometry"]["coordinates"]
        except (KeyError, IndexError, TypeError):
            return ""

        coordinates_json = json.dumps(coordinates)

        initial_data = self.data.copy()
        initial_data["features"][0]["geometry"]["coordinates"] = [coordinates[0]]
        initial_data_json = json.dumps(initial_data)

        callback = f"""
            if (i < coordinates.length) {{
                data.features[0].geometry.coordinates.push(coordinates[i]);
                map.getSource('{self.source_id}').setData(data);
                map.panTo(coordinates[i]);
                i++;
            }} else {{
                window.clearInterval(timer);
            }}
        """

        interval_js = TemporalInterval(
            callback=callback,
            interval=self.interval,
            name="timer",
        ).to_js()

        return f"""
(function() {{
    const coordinates = {coordinates_json};
    let data = {initial_data_json};

    map.getSource('{self.source_id}').setData(data);

    let i = 1;
    {interval_js}
}})();
        """

    def to_js(self) -> str:
        """Return the JavaScript code for the animation loop."""
        return self._js_code