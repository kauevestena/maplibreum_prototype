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

class LiveDataFetcher:
    """
    Fetches and updates map data from a URL at regular intervals.
    
    This class provides an alternative to JavaScript injection for
    real-time data updates by managing fetch intervals and map updates.
    """
    
    def __init__(self, source_id, url, interval=2000, 
                 transform_fn=None, fly_to=True, fly_speed=0.5,
                 initial_data=None):
        """Initialize a LiveDataFetcher.
        
        Parameters
        ----------
        source_id : str
            ID of the GeoJSON source to update.
        url : str
            URL to fetch data from.
        interval : int, optional
            Update interval in milliseconds (default: 2000).
        transform_fn : str, optional
            JavaScript function to transform fetched data.
            Should be a string like: "function(data) { return transformedData; }"
        fly_to : bool, optional
            Whether to fly the map to new coordinates (default: True).
        fly_speed : float, optional
            Speed of the fly animation (default: 0.5).
        initial_data : dict, optional
            Initial GeoJSON data for the source.
        """
        self.source_id = source_id
        self.url = url
        self.interval = interval
        self.transform_fn = transform_fn
        self.fly_to = fly_to
        self.fly_speed = fly_speed
        self.initial_data = initial_data or {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0]}
        }
        
    def get_initial_data(self):
        """Get the initial GeoJSON data structure.
        
        Returns
        -------
        dict
            Initial GeoJSON data.
        """
        return self.initial_data
    
    def to_js(self):
        """Generate JavaScript code for periodic data fetching.
        
        Returns
        -------
        str
            JavaScript code that fetches and updates data at intervals.
        """
        # Build transform function
        if self.transform_fn:
            transform_code = f"""
            const transformData = {self.transform_fn};
            json = transformData(json);
            """
        else:
            transform_code = "// No transformation applied"
        
        # Build fly-to logic
        if self.fly_to:
            fly_code = f"""
            // Fly the map to the new location
            if (json.geometry && json.geometry.coordinates) {{
                map.flyTo({{
                    center: json.geometry.coordinates,
                    speed: {self.fly_speed}
                }});
            }}
            """
        else:
            fly_code = "// Fly-to disabled"
        
        js_code = f"""
(function() {{
    // Fetch and update data at regular intervals
    window.setInterval(() => {{
        fetch('{self.url}')
            .then(r => r.text())
            .then(text => {{
                let json;
                try {{
                    // Try parsing as JSON
                    json = JSON.parse(text);
                }} catch (e) {{
                    // If not JSON, assume it's text data that needs transformation
                    json = {{ rawText: text }};
                }}
                
                {transform_code}
                
                // Update the source data
                const source = map.getSource('{self.source_id}');
                if (source) {{
                    source.setData(json);
                }}
                
                {fly_code}
            }})
            .catch(err => {{
                console.error('Error fetching live data:', err);
            }});
    }}, {self.interval});
}})();
"""
        return js_code


class RandomCoordinateFetcher(LiveDataFetcher):
    """
    Specialized fetcher for random.org decimal fractions API.
    
    This class extends LiveDataFetcher with a built-in transform function
    for converting random decimal fractions to geographic coordinates.
    """
    
    def __init__(self, source_id, interval=2000, fly_to=True, fly_speed=0.5):
        """Initialize a RandomCoordinateFetcher.
        
        Parameters
        ----------
        source_id : str
            ID of the GeoJSON source to update.
        interval : int, optional
            Update interval in milliseconds (default: 2000).
        fly_to : bool, optional
            Whether to fly the map to new coordinates (default: True).
        fly_speed : float, optional
            Speed of the fly animation (default: 0.5).
        """
        # Transform function that converts two random decimals to coordinates
        transform_fn = """
        function(data) {
            // Takes the two random numbers between 0 and 1 and converts them to degrees
            const coordinates = data.rawText.split('\\n').map(l => (Number(l) * 180) - 90);
            return {
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: coordinates
                }
            };
        }
        """
        
        super().__init__(
            source_id=source_id,
            url='https://www.random.org/decimal-fractions/?num=2&dec=10&col=1&format=plain&rnd=new',
            interval=interval,
            transform_fn=transform_fn,
            fly_to=fly_to,
            fly_speed=fly_speed
        )
